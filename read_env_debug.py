from pathlib import Path
path = Path('c:/Personales/Django/ERP/.env')
text = path.read_text()
print(repr(text))
print('--- lines ---')
for i, line in enumerate(text.splitlines(), 1):
    print(i, repr(line))
