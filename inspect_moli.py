import pandas as pd

items_df = pd.read_csv("result_csv/item.csv")
mod_groups_df = pd.read_csv("result_csv/modifier_group.csv")
mod_items_df = pd.read_csv("result_csv/modifier_item.csv")

print("--- Moli Paratha ---")
mp = items_df[items_df['name_en'].str.contains("Moli Paratha", na=False)]
print(mp[['item_code', 'name_en', 'price', 'modifier_groups']].to_string())

if not mp.empty and pd.notna(mp.iloc[0]['modifier_groups']):
    mg_code = mp.iloc[0]['modifier_groups']
    mg = mod_groups_df[mod_groups_df['modifier_group_code'] == mg_code]
    print("Modifier Group:", mg_code)
    print(mg[['name_en', 'modifier_items']].to_string())
    for mi in mg.iloc[0]['modifier_items'].split(','):
        print(mod_items_df[mod_items_df['modifier_item_code'] == mi][['modifier_item_code', 'name_en', 'price']].to_string())
else:
    print("No modifier group for Moli Paratha")
