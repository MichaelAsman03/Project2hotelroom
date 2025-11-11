import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Optional


@dataclass
class BidRequest:
    price: float


class RoomBidHandler:
    def __init__(self, name: str, next_handler: Optional['RoomBidHandler'] = None):
        self.name = name
        self.next = next_handler

    def handle(self, bid: BidRequest) -> Optional[str]:
        if self.can_accept(bid):
            self.on_accept(bid)
            return f"ACCEPTED: {self.name} booked at ${bid.price:,.2f}. Remaining: {self.remaining()}"
        elif self.next is not None:
            return self.next.handle(bid)
        return None

    def can_accept(self, bid: BidRequest) -> bool: ...
    def on_accept(self, bid: BidRequest) -> None: ...
    def remaining(self) -> int: ...


class SuiteHandler(RoomBidHandler):
    def __init__(self, inventory: int, next_handler: Optional['RoomBidHandler'] = None):
        super().__init__("Suite", next_handler)
        self._inv = inventory

    def can_accept(self, bid: BidRequest) -> bool:
        if self._inv <= 0:
            return False
        return bid.price >= 280

    def on_accept(self, bid: BidRequest) -> None:
        self._inv -= 1

    def remaining(self) -> int:
        return self._inv


class DeluxeHandler(RoomBidHandler):
    def __init__(self, inventory: int, suite_ref: SuiteHandler, next_handler: Optional['RoomBidHandler'] = None):
        super().__init__("Deluxe", next_handler)
        self._inv = inventory
        self._suite_ref = suite_ref

    def can_accept(self, bid: BidRequest) -> bool:
        if self._inv <= 0:
            return False
        if 150 <= bid.price < 280:
            return True
        if self._suite_ref.remaining() == 0 and bid.price >= 280:
            return True
        return False

    def on_accept(self, bid: BidRequest) -> None:
        self._inv -= 1

    def remaining(self) -> int:
        return self._inv


class StandardHandler(RoomBidHandler):
    def __init__(self, inventory: int, suite_ref: SuiteHandler, deluxe_ref: DeluxeHandler):
        super().__init__("Standard", None)
        self._inv = inventory
        self._suite_ref = suite_ref
        self._deluxe_ref = deluxe_ref

    def can_accept(self, bid: BidRequest) -> bool:
        if self._inv <= 0:
            return False
        if 80 <= bid.price < 150:
            return True
        if self._suite_ref.remaining() == 0 and self._deluxe_ref.remaining() == 0 and bid.price >= 150:
            return True
        return False

    def on_accept(self, bid: BidRequest) -> None:
        self._inv -= 1

    def remaining(self) -> int:
        return self._inv


class HotelBiddingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Room Bidding - COR Pattern")
        self.geometry("680x460")
        self.resizable(False, False)

        self.suite = SuiteHandler(10)
        self.deluxe = DeluxeHandler(15, suite_ref=self.suite)
        self.standard = StandardHandler(45, suite_ref=self.suite, deluxe_ref=self.deluxe)

        self.suite.next = self.deluxe
        self.deluxe.next = self.standard

        self._build_widgets()
        self._refresh_inventory_labels()

    def _build_widgets(self):
        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        title = ttk.Label(frm, text="Hotel Room Bidding System (Chain of Responsibility)", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w")

        desc = ttk.Label(frm, text="Enter your bid price (USD). The system routes Suite → Deluxe → Standard.")
        desc.pack(anchor="w", pady=(4, 10))

        row = ttk.Frame(frm); row.pack(anchor="w")
        ttk.Label(row, text="Bid price: $").pack(side="left")
        self.entry = ttk.Entry(row, width=12); self.entry.pack(side="left")
        ttk.Button(row, text="Place Bid", command=self._on_place_bid).pack(side="left", padx=8)

        inv = ttk.LabelFrame(frm, text="Inventory Remaining", padding=8)
        inv.pack(fill="x", pady=(12, 8))
        self.lbl_suite = ttk.Label(inv, text="Suite: 0"); self.lbl_suite.pack(anchor="w")
        self.lbl_deluxe = ttk.Label(inv, text="Deluxe: 0"); self.lbl_deluxe.pack(anchor="w")
        self.lbl_standard = ttk.Label(inv, text="Standard: 0"); self.lbl_standard.pack(anchor="w")

        log_frame = ttk.LabelFrame(frm, text="Bid Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.txt = tk.Text(log_frame, height=12, state="disabled"); self.txt.pack(fill="both", expand=True)

        self.footer = ttk.Label(frm, text="Ready.", foreground="#666")
        self.footer.pack(anchor="w", pady=(6,0))

    def _append_log(self, message: str):
        self.txt.configure(state="normal")
        self.txt.insert("end", message + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _refresh_inventory_labels(self):
        self.lbl_suite.config(text=f"Suite: {self.suite.remaining()}")
        self.lbl_deluxe.config(text=f"Deluxe: {self.deluxe.remaining()}")
        self.lbl_standard.config(text=f"Standard: {self.standard.remaining()}")
        total_left = self.suite.remaining() + self.deluxe.remaining() + self.standard.remaining()
        if total_left == 0:
            self.footer.config(text="SOLD OUT — No more rooms available.")
            self.entry.configure(state="disabled")
        else:
            self.footer.config(text=f"Rooms left: {total_left}")

    def _all_sold_out(self) -> bool:
        return (self.suite.remaining() + self.deluxe.remaining() + self.standard.remaining()) == 0

    def _on_place_bid(self):
        if self._all_sold_out():
            messagebox.showinfo("Sold Out", "All rooms are sold out.")
            return

        raw = self.entry.get().strip()
        try:
            price = float(raw)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive numeric price, e.g., 199 or 280.00")
            return

        result = self.suite.handle(BidRequest(price))
        if result:
            self._append_log(result)
        else:
            self._append_log(f"REJECTED: No room type available for ${price:,.2f}. Try another price.")
        self._refresh_inventory_labels()
        self.entry.delete(0, "end")


if __name__ == "__main__":
    app = HotelBiddingApp()
    app.mainloop()
