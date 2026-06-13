import os
import csv

WORKSPACE = "/Users/sychong/.hermes/workspace-kara"
MASTER_CSV = f"{WORKSPACE}/trades/all_trades.csv"

# Let's read all trades and calculate net open positions
positions = {}

if os.path.exists(MASTER_CSV):
    with open(MASTER_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row["ticker"]
            qty = int(row["qty"])
            status = row["status"]
            side = row["side"]
            
            # Since this master CSV only has MATCHED/CLOSED rows, let's check what the XML files themselves have!
            # Let's find all XML files and sum BUY and SELL quantities to find the absolute net open position at the end.
            
import xml.etree.ElementTree as ET
from datetime import datetime

IMPORTS_DIR = f"{WORKSPACE}/trades/imports"
xml_files = sorted([f for f in os.listdir(IMPORTS_DIR) if f.startswith("Kara") and f.endswith(".xml")])

all_executions = []
for fn in xml_files:
    filepath = os.path.join(IMPORTS_DIR, fn)
    tree = ET.parse(filepath)
    root = tree.getroot()
    elements = root.findall(".//TradeConfirm") + root.findall(".//Trade")
    for el in elements:
        attrib = el.attrib
        if attrib.get("assetCategory") == "STK":
            symbol = attrib.get("symbol")
            qty = int(attrib.get("quantity"))
            price = float(attrib.get("price", attrib.get("tradePrice", "0")))
            dateTime = attrib.get("dateTime")
            all_executions.append({
                "symbol": symbol,
                "qty": qty,
                "price": price,
                "dateTime": dateTime
            })

# Sort executions chronologically
all_executions.sort(key=lambda x: x["dateTime"])

# Calculate net shares per symbol
net_shares = {}
for ex in all_executions:
    sym = ex["symbol"]
    net_shares[sym] = net_shares.get(sym, 0) + ex["qty"]
    
print("Net stock positions at the end of June 11:")
for sym, net in net_shares.items():
    print(f"  {sym}: {net} shares")
