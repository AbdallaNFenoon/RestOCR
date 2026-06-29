import io
import sys
import os
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
os.chdir('d:/RestOCR')

from backend.excel_service import generate_excel_in_memory

menu_data = {'categories': [{'name_en': 'Karahi', 'name_ar': 'كراهي', 'items': [
    {'name_en': 'Chicken Karahi', 'name_ar': 'كراهي دجاج', 'price': 0, 'options': [
        {'name_en': 'Half', 'name_ar': 'نصف', 'price': 30},
        {'name_en': 'Full', 'name_ar': 'كامل', 'price': 54}
    ]},
]}]}

try:
    file_bytes = generate_excel_in_memory(menu_data, 'backend/template.xlsx')
    
    print("Verifying XML syntax in the generated file...")
    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
        for name in z.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):
                data = z.read(name)
                try:
                    ET.fromstring(data)
                except Exception as e:
                    print(f"INVALID XML in {name}: {e}")
                    
                    # Print snippet around the error if possible
                    text = data.decode('utf-8', errors='replace')
                    if 'ParseError' in str(type(e)):
                        # try to get line/col
                        import re
                        m = re.search(r'line (\d+), column (\d+)', str(e))
                        if m:
                            line, col = int(m.group(1)), int(m.group(2))
                            lines = text.split('\n')
                            if line <= len(lines):
                                err_line = lines[line-1]
                                start = max(0, col - 50)
                                end = min(len(err_line), col + 50)
                                print(f"  Snippet: {err_line[start:end]}")
                    
    print("\nXML Validation complete.")
    
    with open('test_output_final.xlsx', 'wb') as f:
        f.write(file_bytes)
    print("Saved test_output_final.xlsx")

except Exception as e:
    print(f"Error during generation: {e}")
