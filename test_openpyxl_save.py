import openpyxl
import os
os.chdir('d:/RestOCR')

# Load and save without ANY modifications
wb = openpyxl.load_workbook('backend/template.xlsx')
wb.save('test_load_save.xlsx')
print("Saved test_load_save.xlsx")
