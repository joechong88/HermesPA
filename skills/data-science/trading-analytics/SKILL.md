---
name: trading-analytics
description: "Core procedures for parsing IBKR Flex Query XML files, FIFO trade matching, options Greeks monitoring, and writing ruthless coaching reviews."
version: 1.1.0
author: Kara
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [trading, ibkr, finance, options, portfolio, analytics, coaching]
    related_skills: [jupyter-live-kernel, notion]
---

# Trading Analytics & Trade Cataloger

Use this skill when processing raw brokerage statements (e.g. Interactive Brokers Flex Query XML), matching executions to compute trading metrics, parsing derivatives structures, or delivering data-driven forensic feedback.

## 1. Brokerage Statement Parsing (IBKR XML)

Brokerage trade records must be extracted systematically. Do not rely on manual copying. Maintain a python parsing engine supporting both execution confirms and standard trades.

### XML Nodes to Support
- Root tag: `<FlexQueryResponse>`
- Elements to search: `.//TradeConfirm` or `.//Trade`
- Required Attributes:
  - `dateTime`: Execution timestamp (EST) in `"YYYYMMDD;HHMMSS"`
  - `symbol`: Ticker (equity symbol or option string)
  - `buySell`: `"BUY"` or `"SELL"`
  - `quantity`: Signed or unsigned decimal float (IBKR uses negative quantity for sells, and can represent fractional shares as floats e.g. 0.0082)
  - `price` / `tradePrice`: Match price
  - `proceeds`: Gross value in base currency (negative for buys, positive for sells)
  - `commission` / `ibCommission`: Transaction fees (always negative)
  - `assetCategory`: `"STK"` (Stock) or `"OPT"` (Option)
  - `expiry`, `strike`, `putCall`: Option-specific contract definitions

### Fractional Shares & Quantities
Always parse the `quantity` attribute as a **floating-point decimal** (`float`) rather than a strict integer (`int`). In systems supporting fractional share execution (e.g. IBKR DRIP or micro-investing), quantities like `0.0082` are common and casting them directly to `int` will result in a fatal `ValueError` crash. Ensure all internal calculators and matches handle floats seamlessly.

### Math Rules
- **Gross Proceeds / Value:** `proceeds` field.
- **Commission:** `commission` field.
- **Net Cash:** `proceeds + commission`. Since commission is negative, this correctly subtracts transaction fees. E.g., buying 10 shares for -$10,000 with -$1.00 commission results in net cash of -$10,001.00.

---

## 2. FIFO Stock Matching

Stock trades are executed in lots. Match buys and sells chronologically using a First-In-First-Out (FIFO) queue:

1. Filter and group executions by `symbol`.
2. Sort chronologically by parsed `dateTime` objects.
3. Maintain a persistent, stateful queue of `buys` and `sells` across files to track multi-day swing positions (e.g., carrying inventory of ASTC, CRWD, or SNDK over subsequent days).
4. Iterate and pair:
   - For a `BUY` then a `SELL`: Trade is a `LONG`.
     - `gross_pnl = (exit_price - entry_price) * matched_quantity`
   - For a `SELL` then a `BUY` (Shorting): Trade is a `SHORT`.
     - `gross_pnl = (entry_price - exit_price) * matched_quantity`
   - Realized `commission` is the proportional sum of both legs' commissions.
   - `net_pnl = gross_pnl + realized_commission`.
5. Remaining unmatched execution lots at market close must be logged as `status: OPEN` in `equities/open_positions.md` and carried forward as state for subsequent parsing sessions.

---

## 3. Options Structures & Jade Lizard Detection

Derivatives combinations (spreads) must be reconstructed from leg combinations.

| Structure | Leg Pattern |
|---|---|
| **Calendar Spread** | Long Option (Expiry A) + Short Option (Expiry B, nearer term), same strike, both calls or both puts. |
| **Bull Put Spread** | Short Put (higher strike) + Long Put (lower strike), same expiry. |
| **Bear Call Spread** | Short Call (lower strike) + Long Call (higher strike), same expiry. |
| **Iron Condor** | Bull Put Spread + Bear Call Spread, same expiry. |
| **Jade Lizard 🦎** | Sell Put (unhedged downside) + Bear Call Spread, same expiry. |

### Jade Lizard Validation Logic:
When a Jade Lizard 🦎 is identified, verify:
$$\text{Total Net Credit Received} \ge \text{Call Spread Width}$$
- **If Yes:** Upside risk is fully eliminated. Underlyings moving far above the short call strike are offset by the credit collected.
- **If No:** Upside risk remains. Trigger a warning.
- **Primary Risk:** Downside exposure to the naked put. Target rolls if the underlying gets within 2% of the short put strike.

---

## 4. Forensic Coaching Reports

A professional trading analyst is a risk coach, not a cheerleader. Structure reviews using high-impact, data-driven tables and ruthless feedback.

### Structure:
1. **Executive Summary Table:** Net profit, target hit (Yes/No), max loss breach (Yes/No).
2. **Stream Analysis:** Segment performance by stream (e.g., Small Cap Momentum vs. Large Cap Scalp).
3. **Execution Metrics:** Win rate, average winner, average loser, and profit factor.
4. **Forensic Observations:** Call out explicit behavioral patterns (e.g., overtrading, early exits, letting losers run, ignoring strike breaches). Never soften a critique. Let the numbers drive the feedback.

See `references/coaching_case_studies.md` for historical coaching case studies of severe risk breaches and clean recovery execution patterns.

---

## Pitfalls to Avoid

- **Incorrect Timezone Handling:** IBKR exports timestamps in EST. Convert to user's localized timezone (e.g. MYT) for summaries but preserve EST for execution sequences.
- **Pre-Closed Positions Reconciliation:** Do not add option legs to `active_positions.md` if the cumulative records or `all_trades.csv` indicate they were already closed on a subsequent date. Reconcile them directly, update `closed_positions.md`, and exclude them from active books.
- **Cross-File Dependency Validation:** Before classifying any options legs, check `active_positions.md` and `all_trades.csv` for any existing related positions first to see if they are already closed or belong to an ongoing trade, preventing duplicate open positions.
- **Obsolete Position Cleanups:** Keep `active_positions.md` pruned and clear of old, expired, or manually closed positions. Update status to closed immediately when confirmed.
- **Commission Double-Counting:** Ensure commissions are only deducted on realized matches and proportionally distributed if lots are partially filled.
- **Jade Lizard vs. Naked Put False Positives:** Always look for the corresponding Call Spread legs before classifying a short put as naked. If they share the same underlying and expiry, they are a single Lizard.
- **Unnecessary Mentions:** Never use user mentions (e.g. `@sychong`) in reports or responses. Keep feedback direct, cold, and professional.
- **Verbatim Reading:** When asked to output or read a workspace file verbatim, present its exact contents in code blocks without wrapping explanation or summaries unless explicitly asked.
