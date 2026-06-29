import os
import pandas as pd

def dump_xlsx_to_csv(filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    xls = pd.ExcelFile(filename)
    print(f"Dumping {filename} into {output_dir}:")
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        csv_path = os.path.join(output_dir, f"{sheet_name}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"  - Saved {sheet_name} ({len(df)} rows)")

dump_xlsx_to_csv("template.xlsx", "template_csv")
dump_xlsx_to_csv("result.xlsx", "result_csv")
dump_xlsx_to_csv("menu.xlsx", "menu_csv")
print("Done!")
