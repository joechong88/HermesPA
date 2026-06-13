import os

WORKSPACE = "/Users/sychong/.hermes/workspace-kara"
OPTIONS_FILE = f"{WORKSPACE}/options/active_positions.md"
EQUITIES_FILE = f"{WORKSPACE}/equities/open_positions.md"

# Ensure directories exist
os.makedirs(os.path.dirname(OPTIONS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(EQUITIES_FILE), exist_ok=True)

# Generate updated active_positions.md
options_content = """# Active Options Positions

## 🐂 BULL PUT SPREAD — RKLB
────────────────────────────────────────────────
Short put:  115P | Current underlying: $118.50 | Distance: 3.04% / $3.50
Long put:   110P
Credit received: $580.33 | Max loss: $1,419.67 | Current value: $340.00
P&L at current: 41.4% of max profit
DTE: 21 days
Status: 🟢 Safe (Buffer > 3%)

Opened: 2026-05-29 | Contracts: 4 | Expiry: 2026-07-02 | Spread width: $5.00 | Commission: $5.67

## 🐻 SHORT CALL — INTC
────────────────────────────────────────────────
Short call: 125C | Current underlying: $118.00 | Distance: 5.93% / $7.00
Credit received: $132.44 | Max loss: Unlimited | Current value: $110.00
DTE: 7 days
Status: 🟢 Safe (Buffer > 5%)

Opened: 2026-06-10 | Contracts: 1 | Expiry: 2026-06-18 | Commission: $0.56

## ⚠️ CUSTOM COMPLEX STRUCTURE — SE (Non-Standard)
────────────────────────────────────────────────
Legs:
- BUY 2x 96C | Expiry: 2026-07-02 | Price: $1.12
- SELL 2x 99C | Expiry: 2026-07-02 | Price: $0.73
- BUY 2x 84P | Expiry: 2026-07-02 | Price: $4.41

Net Debit Paid: $963.60 | Commission: $3.60
DTE: 21 days
Status: 🟡 Pending Manual Confirmation / Non-Standard Risk Profile

Opened: 2026-06-10 | Underlying: SE

## 🦎 JADE LIZARD — NOW
────────────────────────────────────────────────
Short put:  110P | Underlying: $122.50 | Distance: 10.20% / $12.50
Short call: 130C | Distance: 6.12% / $7.50
Long put:   115P
────────────────────────────────────────────────
Total credit received: $2,163.19 | Call spread width: $15.00
Upside risk eliminated: ✅ YES (Credit of $21.63 > $15.00 call spread width)
DTE: 71 days
Status: 🟢 Safe (Buffer > 5%)

Opened: 2026-06-01 | Contracts: 1 | Expiry: 2026-08-21 | Commission: $0.81
"""

with open(OPTIONS_FILE, "w") as f:
    f.write(options_content)

# Generate updated open_positions.md
equities_content = """# Open Equity Positions

| Symbol | Stream | Qty | Avg Entry | Entry Date | Current Cost Basis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SNDK** | Stream 2 | 1 | $1,700.00 | 2026-05-29 | $1,700.00 |
| **ASTC** | Stream 1 | 100 | $35.25 | 2026-06-01 | $3,525.00 |
"""

with open(EQUITIES_FILE, "w") as f:
    f.write(equities_content)

print("Both active_positions.md and open_positions.md updated successfully!")
