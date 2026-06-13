import os
import xml.etree.ElementTree as ET

WORKSPACE = "/Users/sychong/.hermes/workspace-kara"
IMPORTS_DIR = f"{WORKSPACE}/trades/imports"
xml_files = sorted([f for f in os.listdir(IMPORTS_DIR) if f.startswith("Kara") and f.endswith(".xml")])

# We will calculate net stock position at the end of each day
daily_positions = {}

all_execs = []
for fn in xml_files:
    date_str = fn[4:12]
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    filepath = os.path.join(IMPORTS_DIR, fn)
    tree = ET.parse(filepath)
    root = tree.getroot()
    elements = root.findall(".//TradeConfirm") + root.findall(".//Trade")
    
    day_execs = []
    for el in elements:
        attrib = el.attrib
        if attrib.get("assetCategory") == "STK":
            day_execs.append({
                "symbol": attrib.get("symbol"),
                "qty": int(attrib.get("quantity")),
                "price": float(attrib.get("price", attrib.get("tradePrice", "0"))),
                "dateTime": attrib.get("dateTime")
            })
            
    # Sort chronologically
    day_execs.sort(key=lambda x: x["dateTime"])
    all_execs.extend(day_execs)
    
    # Calculate running positions at the end of this day
    running_qty = {}
    running_cost = {}
    
    for ex in all_execs:
        sym = ex["symbol"]
        qty = ex["qty"]
        price = ex["price"]
        
        current_qty = running_qty.get(sym, 0)
        new_qty = current_qty + qty
        
        if current_qty == 0:
            running_cost[sym] = price
        elif (current_qty > 0 and qty > 0) or (current_qty < 0 and qty < 0):
            # Same side, average cost basis
            running_cost[sym] = (running_cost[sym] * abs(current_qty) + price * abs(qty)) / abs(new_qty)
        else:
            # Opposite side (closing or reducing position)
            if abs(new_qty) == 0:
                running_cost[sym] = 0.0
            elif abs(qty) > abs(current_qty):
                # Flipped side
                running_cost[sym] = price
                
        running_qty[sym] = new_qty
        
    daily_positions[formatted_date] = {
        "qty": {k: v for k, v in running_qty.items() if v != 0},
        "cost": {k: v for k, v in running_cost.items() if running_qty.get(k, 0) != 0}
    }

# Let's generate open_positions.md as of the end of June 11 (the latest date)
latest_date = sorted(daily_positions.keys())[-1]
pos_data = daily_positions[latest_date]

with open(f"{WORKSPACE}/equities/open_positions.md", "w") as f:
    f.write("# Open Equity Positions\n\n")
    f.write("| Symbol | Stream | Qty | Avg Entry | Entry Date | Current Cost Basis |\n")
    f.write("|--------|--------|-----|-----------|------------|---------------------|\n")
    for sym, qty in pos_data["qty"].items():
        avg_entry = pos_data["cost"][sym]
        stream = "Stream 1" if sym in ["ASTC", "CRWD"] else "Stream 2"
        f.write(f"| {sym} | {stream} | {qty} | ${avg_entry:.2f} | 2026-06-01 | ${avg_entry:.2f} |\n")

print(f"open_positions.md updated as of {latest_date}!")
print("Net positions:", pos_data["qty"])
