import os

WORKSPACE = "/Users/sychong/.hermes/workspace-kara"
OPTIONS_FILE = f"{WORKSPACE}/options/active_positions.md"

content = """# Active Options Positions

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

## 🐂 BULL PUT SPREAD — META
────────────────────────────────────────────────
Short put:  535P | Current underlying: $541.20 | Distance: 1.15% / $6.20
Long put:   525P
Credit received: $404.00 | Max loss: $596.00 | Current value: $380.00
P&L at current: 5.9% of max profit
DTE: 28 days
Status: 🟡 Watch (Buffer < 2%)

Opened: 2026-06-12 | Contracts: 2 | Expiry: 2026-07-10 | Spread width: $10.00 | Commission: $1.43

## 📅 CALENDAR SPREAD — BRK B
────────────────────────────────────────────────
Short leg:  490C | Expiry: 2026-06-18 | Delta: 0.38 | Target range: 0.30–0.45
Long leg:   487.5C | Expiry: 2026-06-12 (Expired Worthless)
Net delta:  -0.38
DTE (short): 6 days
Underlying: $485.60
Status: 🟢 Safe (Short call OTM)

Opened: 2026-06-12 | Contracts: 1 | Commission: $2.11
"""

with open(OPTIONS_FILE, "w") as f:
    f.write(content)

print("active_positions.md updated with June 12 positions!")
