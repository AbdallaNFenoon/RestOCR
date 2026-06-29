import pandas as pd

items_df = pd.read_csv("result_csv/item.csv")
mod_groups_df = pd.read_csv("result_csv/modifier_group.csv")
mod_items_df = pd.read_csv("result_csv/modifier_item.csv")

print("--- Chicken Boneless Handi ---")
cbh = items_df[items_df['name_en'].str.contains("Boneless", na=False)]
print(cbh[['item_code', 'name_en', 'price', 'modifier_groups']].to_string())

if not cbh.empty:
    mgroup_code = cbh.iloc[0]['modifier_groups']
    if pd.notna(mgroup_code):
        print(f"\nModifier Group: {mgroup_code}")
        mg = mod_groups_df[mod_groups_df['modifier_group_code'] == mgroup_code]
        print(mg[['modifier_group_code', 'name_en', 'modifier_items']].to_string())
        
        mitems = mg.iloc[0]['modifier_items'].split(',')
        print("\nModifier Items:")
        for mi in mitems:
            mitem = mod_items_df[mod_items_df['modifier_item_code'] == mi]
            print(mitem[['modifier_item_code', 'name_en', 'price']].to_string())

print("\n--- Shahi Daal ---")
sd = items_df[items_df['name_en'].str.contains("Shahi Daal", na=False)]
print(sd[['item_code', 'name_en', 'price', 'modifier_groups']].to_string())
if not sd.empty:
    mgroup_code = sd.iloc[0]['modifier_groups']
    if pd.notna(mgroup_code):
        print(f"\nModifier Group: {mgroup_code}")
        mg = mod_groups_df[mod_groups_df['modifier_group_code'] == mgroup_code]
        print(mg[['modifier_group_code', 'name_en', 'modifier_items']].to_string())
    else:
        print("No modifier group (direct price)")
