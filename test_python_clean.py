import openpyxl
import os
os.chdir('d:/RestOCR')

wb = openpyxl.load_workbook('backend/template.xlsx')

print("Defined Names:")
names_to_delete = []
if hasattr(wb, 'defined_names'):
    for dn in wb.defined_names.definedName:
        print("  -", dn.name)
        if dn.name.startswith('Z_'):
            names_to_delete.append(dn.name)

for name in names_to_delete:
    del wb.defined_names[name]

print("\nFonts:")
for font in wb._fonts:
    if font.name and 'google' in font.name.lower():
        print(f"  Replacing font: {font.name}")
        font.name = 'Consolas'

wb.save('test_python_clean.xlsx')
print("Saved successfully!")
