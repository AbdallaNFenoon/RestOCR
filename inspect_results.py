import os
import pandas as pd
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def inspect_folder(folder):
    print(f"\n================= {folder} =================")
    if not os.path.exists(folder):
        print("Folder does not exist")
        return
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            path = os.path.join(folder, file)
            df = pd.read_csv(path)
            print(f"\nFile: {file}")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            if len(df) > 0:
                print("First 3 rows:")
                print(df.head(3).to_string())

inspect_folder("template_csv")
inspect_folder("result_csv")
inspect_folder("menu_csv")
