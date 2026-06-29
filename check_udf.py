import zipfile
import re

with zipfile.ZipFile('backend/template.xlsx', 'r') as z:
    for name in z.namelist():
        if name.startswith('xl/worksheets/'):
            text = z.read(name).decode('utf-8')
            if 'DUMMY' in text or '__xl' in text:
                print(f"Found UDF reference in {name}!")
                print(re.findall(r'__xl[^<"\' ]*', text))
