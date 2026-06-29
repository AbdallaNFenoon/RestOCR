import openpyxl
from backend.excel_service import extract_dummy_function_contents

wb = openpyxl.load_workbook('backend/template.xlsx')

with open('formulas_log.txt', 'w', encoding='utf-8') as f:
    for sheet_name in ['item', 'modifier_group_option']:
        ws = wb[sheet_name]
        f.write(f"\n--- {sheet_name} ---\n")
        for r in range(2, 5):
            for c in range(1, 20):
                cell = ws.cell(row=r, column=c)
                if isinstance(cell.value, str) and cell.value.startswith('='):
                    f.write(f"Cell {cell.coordinate}:\n")
                    f.write(f"  ORIG: {cell.value}\n")
                    f.write(f"  NEW:  {extract_dummy_function_contents(cell.value)}\n")
