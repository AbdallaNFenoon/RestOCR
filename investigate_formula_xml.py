import zipfile
import xml.etree.ElementTree as ET

def investigate_formulas(xlsx_path):
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        for sheet_name in ['xl/worksheets/sheet2.xml', 'xl/worksheets/sheet4.xml']:
            print(f"\n--- Investigating {sheet_name} ---")
            try:
                with z.open(sheet_name) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    # Namespaces usually involved
                    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    formulas = root.findall('.//main:f', ns)
                    print(f"Found {len(formulas)} formula tags.")
                    
                    # Print the first 10 formula tags
                    for i, f_tag in enumerate(formulas[:10]):
                        parent = root.find(f".//main:f[.='{f_tag.text}']/..", ns)
                        cell_ref = parent.attrib.get('r', 'Unknown') if parent is not None else 'Unknown'
                        print(f"Cell {cell_ref}:")
                        print(f"  Type attribute (t): {f_tag.attrib.get('t', 'None')}")
                        print(f"  Formula text: {f_tag.text}")
                        
                        # Check the <v> tag (value) if it exists
                        if parent is not None:
                            v_tag = parent.find('main:v', ns)
                            if v_tag is not None:
                                print(f"  Value <v>: {v_tag.text}")
                            else:
                                print("  Value <v>: MISSING")
            except Exception as e:
                print(f"Error reading {sheet_name}: {e}")

if __name__ == '__main__':
    investigate_formulas('test_output_final.xlsx')
