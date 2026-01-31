import csv

# Read the CSV
changes = []
with open('ADOH - BOSS ITEMS - REBALANCE - Purple Items.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        item_name = row.get('Item Name', '').strip()
        new_col = row.get('NEW', '').strip()
        if item_name and new_col and new_col.lower() != 'unchanged':
            changes.append({
                'name': item_name,
                'change': new_col
            })

# Print all weapons with changes
for i, change in enumerate(changes, 1):
    print(f"{i}. {change['name']}")
    change_preview = change['change'][:100] + "..." if len(change['change']) > 100 else change['change']
    print(f"   {change_preview}")
    print()

