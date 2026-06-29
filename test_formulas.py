import openpyxl
from backend.excel_service import extract_dummy_function_contents

wb = openpyxl.load_workbook('backend/template.xlsx')

for sheet_name in ['item', 'modifier_group_option']:
    ws = wb[sheet_name]
    print(f"\n--- {sheet_name} ---")
    for r in range(2, 5):
        for c in range(1, 20):
            cell = ws.cell(row=r, column=c)
            if isinstance(cell.value, str) and cell.value.startswith('='):
                print(f"Cell {cell.coordinate}:")
                print("  ORIG:", cell.value)
                cleaned = extract_dummy_function_contents(cell.value)
                print("  NEW: ", cleaned)
