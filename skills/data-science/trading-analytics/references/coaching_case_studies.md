# Trading Case Studies & Behavioral Risk Patterns

This reference documents real trading behaviors observed during portfolio reviews, specifically focusing on execution failures, risk breaches, and de-risking recovery strategies.

---

## ⚠️ Case Study 1: The Max Loss Rule Breach (June 05, 2026)
* **Underlying Symbol:** `SNDK` (SanDisk Corp)
* **Realized Daily P&L:** -$1,762.53
* **Hard Stop-Loss Limit:** -$400.00
* **Breach Severity:** Critical (Over-limit by -$1,362.53)

### Behavioral Observations:
1. **Fighting the Tape (0% Win Rate):** The trader executed 7 consecutive long scalps on `SNDK` during a severe downtrend. Every single trade resulted in a loss. No adjustment was made to sit on hands or switch sides.
2. **Terminal Lockup Refusal:** The hard stop-loss is an absolute boundary. Instead of closing down the execution terminal when the net loss crossed -$400.00, the trader continued to execute larger size to "make it back" (revenge trading).

### Analytical Takeaway:
* If win rate is 0% after 3 trades, there is a mismatch between the trading system and market conditions. Trading must be halted immediately.
* Hard stops must be enforced at the broker level or via automated scripts, not left to human discretion when emotions are running hot.

---

## 🟢 Case Study 2: The Legacy Carryover De-risking Recovery (June 08, 2026)
* **Underlying Symbol:** `SNDK` (SanDisk Corp)
* **Realized Daily P&L:** -$114.27
* **Intraday Scalp P&L:** +$364.00
* **Legacy Loss Realized:** -$478.27

### Behavioral Observations:
1. **Accepting the Hit:** On market open, the trader accepted the reality of the underwater `SNDK` long positions carried over from the June 05 disaster. All 10 shares were exited at $16.18, locking in a substantial loss of -$478.27 immediately.
2. **Mental Reset & Clean Execution:** Rather than tilting, the trader performed a complete mental reset, took the hit, and cleanly executed 5 consecutive winning day trades on `SNDK` for a net positive intraday recovery of +$364.00.

### Analytical Takeaway:
* Holding onto losing swing inventory "hoping it gets back to even" ties up capital and incurs massive psychological drag.
* Closing toxic carryover positions on open cleans the slate and allows the trader to focus on high-probability intraday setups.
