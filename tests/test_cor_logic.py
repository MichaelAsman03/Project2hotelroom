import importlib.util, os

MODULE_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "hotel_bidding_cor.py")
spec = importlib.util.spec_from_file_location("hotel_mod", MODULE_PATH)
hotel_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hotel_mod)

def build_chain(std=45, dlx=15, ste=10):
    suite = hotel_mod.SuiteHandler(ste)
    deluxe = hotel_mod.DeluxeHandler(dlx, suite_ref=suite)
    standard = hotel_mod.StandardHandler(std, suite_ref=suite, deluxe_ref=deluxe)
    suite.next = deluxe
    deluxe.next = standard
    return suite, deluxe, standard

def accept_price(handler, price):
    return handler.handle(hotel_mod.BidRequest(price))

def test_suite_accepts_280_or_more():
    suite, _, _ = build_chain()
    assert "Suite booked" in accept_price(suite, 280)

def test_deluxe_accepts_150_to_279_99():
    suite, _, _ = build_chain()
    assert "Deluxe booked" in accept_price(suite, 200)

def test_standard_accepts_80_to_149_99():
    suite, _, _ = build_chain()
    assert "Standard booked" in accept_price(suite, 120)

def test_deluxe_accepts_280_when_suites_sold_out():
    suite, _, _ = build_chain(ste=0)
    assert "Deluxe booked" in accept_price(suite, 300)

def test_standard_accepts_150_when_deluxe_and_suite_sold_out():
    suite, _, _ = build_chain(std=45, dlx=0, ste=0)
    assert "Standard booked" in accept_price(suite, 180)

def test_reject_when_all_sold_out():
    suite, _, _ = build_chain(std=0, dlx=0, ste=0)
    assert accept_price(suite, 200) is None
