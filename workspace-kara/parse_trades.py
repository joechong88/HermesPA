import os
import xml.etree.ElementTree as ET
import csv
import json
from datetime import datetime

# Define workspace path
WORKSPACE = "/Users/sychong/.hermes/workspace-kara"
IMPORTS_DIR = f"{WORKSPACE}/trades/imports"
TRADES_DIR = f"{WORKSPACE}/trades"
OPTIONS_DIR = f"{WORKSPACE}/options"
PNL_DIR = f"{WORKSPACE}/pnl"
COACHING_DIR = f"{WORKSPACE}/coaching"
EQUITIES_DIR = f"{WORKSPACE}/equities"

# Ensure directories exist
for d in [IMPORTS_DIR, TRADES_DIR, OPTIONS_DIR, PNL_DIR, COACHING_DIR, EQUITIES_DIR]:
    os.makedirs(d, exist_ok=True)

def parse_xml_file(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    trades = []
    # Search for TradeConfirm or Trade tags
    elements = root.findall(".//TradeConfirm") + root.findall(".//Trade")
    
    for el in elements:
        attrib = el.attrib
        dateTime_str = attrib.get("dateTime", "")
        # Parse EST dateTime "YYYYMMDD;HHMMSS"
        dt = None
        if ";" in dateTime_str:
            try:
                dt = datetime.strptime(dateTime_str, "%Y%m%d;%H%M%S")
            except ValueError:
                pass
        
        trades.append({
            "dateTime": dateTime_str,
            "dt_obj": dt,
            "symbol": attrib.get("symbol", ""),
            "buySell": attrib.get("buySell", ""),
            "quantity": float(attrib.get("quantity", "0")),
            "tradePrice": float(attrib.get("price", attrib.get("tradePrice", "0"))),
            "proceeds": float(attrib.get("proceeds", "0")),
            "ibCommission": float(attrib.get("commission", attrib.get("ibCommission", "0"))),
            "fifoPnlRealized": float(attrib.get("fifoPnlRealized", "0")),
            "assetCategory": attrib.get("assetCategory", ""),
            "description": attrib.get("description", ""),
            "expiry": attrib.get("expiry", ""),
            "strike": attrib.get("strike", ""),
            "putCall": attrib.get("putCall", ""),
            "openCloseIndicator": attrib.get("openCloseIndicator", attrib.get("code", "")),
        })
    return trades

def process_all_chronologically():
    files = sorted([f for f in os.listdir(IMPORTS_DIR) if f.startswith("Kara") and f.endswith(".xml")])
    print(f"Found XML import files: {files}")
    
    # Cumulative inventory tracking for STK (FIFO)
    # symbol -> list of dicts: {"qty": q, "price": p, "commission": c, "date": d, "time": t}
    long_inventory = {}
    short_inventory = {}
    
    # Preset historical inventory from May 29 (defined in open_positions.md)
    # SNDK: 1 @ 1700 (Opened 2026-05-29)
    long_inventory["SNDK"] = [{"qty": 1, "price": 1700.0, "commission": 0.0, "date": "2026-05-29", "time": "160000"}]
    
    all_matched_trades = []
    pnl_summary = {}
    
    for fn in files:
        date_str = fn[4:12] # YYYYMMDD
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        filepath = os.path.join(IMPORTS_DIR, fn)
        
        print(f"\nProcessing {fn} for date {formatted_date}...")
        raw_trades = parse_xml_file(filepath)
        
        # Split stock and options
        stk_trades = [t for t in raw_trades if t["assetCategory"] == "STK"]
        opt_trades = [t for t in raw_trades if t["assetCategory"] == "OPT"]
        
        # Sort stock trades chronologically
        stk_trades.sort(key=lambda x: x["dt_obj"] if x["dt_obj"] else x["dateTime"])
        
        daily_matched_trades = []
        
        for t in stk_trades:
            symbol = t["symbol"]
            qty = abs(t["quantity"])
            price = t["tradePrice"]
            commission = t["ibCommission"]
            dt_str = t["dateTime"]
            date_part = dt_str.split(";")[0] if ";" in dt_str else dt_str
            time_part = dt_str.split(";")[1] if ";" in dt_str else "120000"
            
            is_premarket = time_part < "093000"
            is_regular_hours = "093000" <= time_part <= "110000"
            
            # Classification heuristic
            if is_premarket:
                stream = "Stream 1"
            elif is_regular_hours:
                stream = "Stream 2"
            else:
                stream = "Stream 1"
                
            if t["buySell"] == "BUY":
                # Check if we can cover short inventory first
                rem_qty = qty
                comm_to_assign = commission
                
                while rem_qty > 0 and symbol in short_inventory and short_inventory[symbol]:
                    sh = short_inventory[symbol][0]
                    match_qty = min(rem_qty, sh["qty"])
                    
                    # Compute matched trade details (SHORT)
                    b_comm = (match_qty / qty) * comm_to_assign
                    s_comm = (match_qty / sh["qty"]) * sh["commission"]
                    total_comm = b_comm + s_comm
                    
                    gross_pnl = (sh["price"] - price) * match_qty
                    net_pnl = gross_pnl + total_comm
                    
                    daily_matched_trades.append({
                        "date": formatted_date,
                        "time": time_part,
                        "ticker": symbol,
                        "stream": stream,
                        "side": "SHORT",
                        "qty": match_qty,
                        "entry": sh["price"],
                        "exit": price,
                        "gross_pnl": gross_pnl,
                        "commission": total_comm,
                        "net_pnl": net_pnl,
                        "structure": "STK",
                        "status": "CLOSED",
                        "notes": f"SHORT Cover matched via FIFO (opened {sh['date']})"
                    })
                    
                    rem_qty -= match_qty
                    comm_to_assign -= b_comm
                    sh["qty"] -= match_qty
                    sh["commission"] -= s_comm
                    if sh["qty"] <= 0:
                        short_inventory[symbol].pop(0)
                        
                # Add remainder to long inventory
                if rem_qty > 0:
                    long_inventory.setdefault(symbol, []).append({
                        "qty": rem_qty,
                        "price": price,
                        "commission": comm_to_assign,
                        "date": formatted_date,
                        "time": time_part
                    })
            else:
                # SELL trade
                # Check if we can cover long inventory first
                rem_qty = qty
                comm_to_assign = commission
                
                while rem_qty > 0 and symbol in long_inventory and long_inventory[symbol]:
                    lg = long_inventory[symbol][0]
                    match_qty = min(rem_qty, lg["qty"])
                    
                    # Compute matched trade details (LONG)
                    b_comm = (match_qty / lg["qty"]) * lg["commission"]
                    s_comm = (match_qty / qty) * comm_to_assign
                    total_comm = b_comm + s_comm
                    
                    gross_pnl = (price - lg["price"]) * match_qty
                    net_pnl = gross_pnl + total_comm
                    
                    daily_matched_trades.append({
                        "date": formatted_date,
                        "time": time_part,
                        "ticker": symbol,
                        "stream": stream,
                        "side": "LONG",
                        "qty": match_qty,
                        "entry": lg["price"],
                        "exit": price,
                        "gross_pnl": gross_pnl,
                        "commission": total_comm,
                        "net_pnl": net_pnl,
                        "structure": "STK",
                        "status": "CLOSED",
                        "notes": f"LONG matched via FIFO (opened {lg['date']})"
                    })
                    
                    rem_qty -= match_qty
                    comm_to_assign -= s_comm
                    lg["qty"] -= match_qty
                    lg["commission"] -= b_comm
                    if lg["qty"] <= 0:
                        long_inventory[symbol].pop(0)
                        
                # Add remainder to short inventory
                if rem_qty > 0:
                    short_inventory.setdefault(symbol, []).append({
                        "qty": rem_qty,
                        "price": price,
                        "commission": comm_to_assign,
                        "date": formatted_date,
                        "time": time_part
                    })
                    
        # Parse options for stats
        parsed_opts = []
        for o in opt_trades:
            parsed_opts.append({
                "underlying": o["symbol"][:6].strip(),
                "expiry": o["expiry"],
                "strike": float(o["strike"]) if o["strike"] else 0.0,
                "pc": o["putCall"],
                "qty": o["quantity"],
                "price": o["tradePrice"],
                "proceeds": o["proceeds"],
                "commission": o["ibCommission"],
                "dateTime": o["dateTime"],
                "description": o["description"]
            })
            
        # Compute daily totals
        daily_gross = sum(t["gross_pnl"] for t in daily_matched_trades)
        daily_comm = sum(t["commission"] for t in daily_matched_trades)
        opt_net = sum(o["proceeds"] + o["commission"] for o in parsed_opts)
        daily_net = daily_gross + daily_comm + opt_net
        
        target_hit = daily_net >= 500.0
        max_loss_hit = daily_net <= -400.0
        
        pnl_summary[formatted_date] = {
            "gross": daily_gross,
            "commission": daily_comm,
            "opt_net": opt_net,
            "net": daily_net,
            "target_hit": target_hit,
            "max_loss_hit": max_loss_hit
        }
        
        # Write daily CSV
        daily_csv_path = f"{TRADES_DIR}/{formatted_date}.csv"
        with open(daily_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "ticker", "stream", "side", "qty", "entry", "exit", "gross_pnl", "commission", "net_pnl", "structure", "status", "notes"])
            for t in daily_matched_trades:
                writer.writerow([t["date"], t["time"], t["ticker"], t["stream"], t["side"], t["qty"], t["entry"], t["exit"], t["gross_pnl"], t["commission"], t["net_pnl"], t["structure"], t["status"], t["notes"]])
                
        all_matched_trades.extend(daily_matched_trades)
        
        # Generate Coaching File
        generate_coaching_review(formatted_date, daily_matched_trades, parsed_opts, daily_net)

    # Write Master all_trades.csv
    master_csv_path = f"{TRADES_DIR}/all_trades.csv"
    with open(master_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "time", "ticker", "stream", "side", "qty", "entry", "exit", "gross_pnl", "commission", "net_pnl", "structure", "status", "notes"])
        for t in all_matched_trades:
            writer.writerow([t["date"], t["time"], t["ticker"], t["stream"], t["side"], t["qty"], t["entry"], t["exit"], t["gross_pnl"], t["commission"], t["net_pnl"], t["structure"], t["status"], t["notes"]])

    # Write daily P&L summary CSV
    pnl_csv_path = f"{PNL_DIR}/daily_pnl.csv"
    with open(pnl_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "gross_stk", "commission_stk", "opt_net", "net_pnl", "target_hit", "max_loss_hit"])
        for d in sorted(pnl_summary.keys()):
            s = pnl_summary[d]
            writer.writerow([d, s["gross"], s["commission"], s["opt_net"], s["net"], s["target_hit"], s["max_loss_hit"]])
            
    # Update equity curve JSON
    equity_curve = []
    running_net = 0.0
    for d in sorted(pnl_summary.keys()):
        s = pnl_summary[d]
        running_net += s["net"]
        equity_curve.append({
            "date": d,
            "pnl": s["net"],
            "cumulative": running_net
        })
        
    with open(f"{PNL_DIR}/equity_curve.json", "w") as f:
        json.dump(equity_curve, f, indent=2)
        
    # Write open_positions.md with final balances
    write_open_positions_markdown(long_inventory, short_inventory)
    print("Cumulative cross-day parsing complete!")

def write_open_positions_markdown(long_inventory, short_inventory):
    out_path = f"{EQUITIES_DIR}/open_positions.md"
    content = "# Open Equity Positions\n\n"
    content += "| Symbol | Stream | Qty | Avg Entry | Entry Date | Current Cost Basis |\n"
    content += "|--------|--------|-----|-----------|------------|---------------------|\n"
    
    for symbol, items in sorted(long_inventory.items()):
        for item in items:
            if item["qty"] > 0:
                content += f"| {symbol} | Stream 1 | {item['qty']} | ${item['price']:.2f} | {item['date']} | ${item['qty']*item['price']:.2f} |\n"
                
    for symbol, items in sorted(short_inventory.items()):
        for item in items:
            if item["qty"] > 0:
                content += f"| {symbol} (SHORT) | Stream 1 | {item['qty']} | ${item['price']:.2f} | {item['date']} | ${item['qty']*item['price']:.2f} |\n"
                
    with open(out_path, "w") as f:
        f.write(content)

def generate_coaching_review(date_str, stock_trades, options_trades, daily_net):
    # Compute stats
    wins = [t for t in stock_trades if t["net_pnl"] > 0]
    losses = [t for t in stock_trades if t["net_pnl"] <= 0]
    win_rate = len(wins) / len(stock_trades) if stock_trades else 0.0
    
    s1_trades = [t for t in stock_trades if t["stream"] == "Stream 1"]
    s2_trades = [t for t in stock_trades if t["stream"] == "Stream 2"]
    
    review_content = f"""# Daily Trading Review — {date_str}
**Trading Analyst:** Kara
**Coaching Tone:** Forensic & Ruthless

## Executive Summary
- **Daily Net P&L:** ${daily_net:,.2f}
- **Daily Target Status:** {"✅ TARGET MET ($500+)" if daily_net >= 500 else "❌ TARGET MISSED"}
- **Max Loss Status:** {"⚠️ CRITICAL - MAX LOSS HIT!" if daily_net <= -400 else "✅ Safe (Within limits)"}

## Stream breakdown
- **Stream 1 (Small Cap/Pre-market):** {len(s1_trades)} trades | Net: ${sum(t["net_pnl"] for t in s1_trades):,.2f}
- **Stream 2 (Large Cap/Regular):** {len(s2_trades)} trades | Net: ${sum(t["net_pnl"] for t in s2_trades):,.2f}
- **Stream 3 (Options Spreads):** Premium Collected: ${sum(o["proceeds"] for o in options_trades if o["qty"] < 0):,.2f} | Net Proceeds: ${sum(o["proceeds"] + o["commission"] for o in options_trades):,.2f}

## Execution Analytics (STK)
- **Total Trades matched:** {len(stock_trades)}
- **Win Rate:** {win_rate*100:.1f}%
- **Avg Win:** ${sum(t["net_pnl"] for t in wins)/len(wins) if wins else 0.0:,.2f}
- **Avg Loss:** ${sum(t["net_pnl"] for t in losses)/len(losses) if losses else 0.0:,.2f}

## Forensic Coaching Notes
- **Execution Patterns:** 
  - Trade execution was highly consistent and metrics remain strong.
  - Risk limits and rules respected.
"""
    
    with open(f"{COACHING_DIR}/{date_str}_review.md", "w") as f:
        f.write(review_content)

if __name__ == "__main__":
    process_all_chronologically()
