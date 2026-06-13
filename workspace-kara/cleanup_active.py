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
"""

with open(OPTIONS_FILE, "w") as f:
    f.write(content)

print("Removed SE and NOW from active_positions.md")
