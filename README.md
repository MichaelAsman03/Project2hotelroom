Project2hotelroom

CIS 476 – Project 2: Chain of Responsibility (CoR) Hotel Room Bidding System**

Implements hotel bidding with CoR handlers ordered Suite → Deluxe → Standard and a Tkinter GUI.

## Rules
- Suite: accepts ≥ $280
- Deluxe: accepts $150–$279.99, or ≥ $280 when Suites are sold out
- **Standard:** accepts **$80–$149.99**, or **≥ $150** when **Deluxe & Suite** are both sold out
- Inventory: **Standard 45**, **Deluxe 15**, **Suite 10** (decrement on accept)

## Run
```bash
python src/hotel_bidding_cor.py
