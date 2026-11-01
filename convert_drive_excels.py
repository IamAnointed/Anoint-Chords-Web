"""SOURCE-only Excel chord-chart converter. Python 3 standard library; no installation needed.
Usage: python convert_drive_excels.py path/to/downloaded_xlsx_folder
Output: songs-import.json and conversion-report.txt in current directory.
Review every converted chart before importing to Firebase.
"""
import sys, re, json, zipfile, pathlib, xml.etree.ElementTree as ET
N={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
CHORD=re.compile(r'^[A-G](?:#|b)?(?:m(?:aj)?|sus|dim|aug|add|M)?[0-9+#b()\-]*(?:/[A-G](?:#|b)?)?$',re.I)
SECTION=re.compile(r'^(?:intro|verse\s*\d*|chorus\s*\d*|bridge\s*\d*|pre[- ]?chorus|outro|ending|instrumental|instru|interlude|tag|refrain|vamp|bassline|solo|turnaround|breakdown|hook|coda)(?:\s*\d*x)?$',re.I)
def colnum(s):
 n=0
 for c in s:n=n*26+ord(c)-64
 return n
def read_xlsx(path):
 with zipfile.ZipFile(path) as z:
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   root=ET.fromstring(z.read('xl/sharedStrings.xml'))
   ss=[''.join(n.text or '' for n in si.findall('.//x:t',N)) for si in root.findall('x:si',N)]
  names=sorted((x for x in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$',x)),key=lambda x:int(re.search(r'sheet(\d+)',x).group(1)))
  for name in names:
   root=ET.fromstring(z.read(name)); rows=[]
   for row in root.findall('.//x:sheetData/x:row',N):
    cells={}
    for c in row.findall('x:c',N):
     ref=c.attrib.get('r',''); m=re.match(r'([A-Z]+)',ref)
     if not m:continue
     ix=colnum(m.group(1)); v=c.find('x:v',N)
     if c.attrib.get('t')=='inlineStr': val=''.join(n.text or '' for n in c.findall('.//x:t',N))
     elif v is None: continue
     elif c.attrib.get('t')=='s': val=ss[int(v.text or 0)]
     else: val=v.text or ''
     val=str(val).strip()
     if val: cells[ix]=val
    if cells:rows.append(cells)
   if rows:yield rows

def convert(rows,title,source):
 # SOURCE normally begins at column B, TRANSPOSED at T or later.
 boundary=next((col for row in rows[:14] for col,val in row.items() if val.upper()=='TRANSPOSED'),None)
 if boundary is None: boundary=20
 source_rows=[{c:v for c,v in row.items() if c<boundary} for row in rows]
 source_rows=[r for r in source_rows if r]
 key='C'; sections=[]; current=None; pending=[]; notes=[]
 for i,row in enumerate(source_rows):
  values=list(row.items())
  for c,v in values:
   if v.lower().rstrip(':')=='key':
    key=row.get(c+1) or next((vv for cc,vv in values if cc>c and cc<=c+3),'C')
  sec=next(((c,v) for c,v in values if SECTION.fullmatch(v)),None)
  if sec:
   current={'name':sec[1],'lyrics':'','rows':[]};sections.append(current)
  if current is None:continue
  # Chord columns typically every second column; numeric counts are in row before chord row.
  chords=[(c,v) for c,v in values if CHORD.fullmatch(v) and not (len(v)>12)]
  # Avoid treating key field or title as a chord.
  if chords and not any(v.lower().rstrip(':')=='key' for _,v in values):
   counts={c:v for c,v in (source_rows[i-1].items() if i>0 else []) if re.fullmatch(r'\d+(?:x)?',v)}
   # Count is often one column to the left of chord, sometimes same column.
   cells=[]
   for c,v in chords:
    count=counts.get(c-1) or counts.get(c) or '4'
    cells.append({'count':count,'chord':v})
   if cells:current['rows'].append({'cells':cells})
  # Text content not recognized as section, key, or chord is preserved as lyrics/notes.
  for c,v in values:
   if sec and c==sec[0]:continue
   if v.lower().rstrip(':') in ('key','source','transposed'):continue
   if v==key or CHORD.fullmatch(v) or re.fullmatch(r'\d+(?:x)?',v):continue
   if len(v)>2 and not (i<6 and v.lower()==title.lower()):
    if not re.fullmatch(r'\d+(?:st|nd|rd|th)',v,re.I):notes.append((current,v))
 for section,v in notes:
  if v not in section['lyrics'].splitlines():section['lyrics']+=(('\n' if section['lyrics'] else '')+v)
 sections=[s for s in sections if s['rows'] or s['lyrics']]
 return {'title':title,'key':key,'sections':sections,'sourceFile':source}

def main(folder):
 folder=pathlib.Path(folder)
 files=sorted(folder.rglob('*.xlsx'))
 out=[]; report=[]; seen=set()
 for f in files:
  try:
   candidates=[]
   for rows in read_xlsx(f):
    x=convert(rows,re.sub(r'\s*[-–]\s*(?:final|bishop|aw)\b.*$','',f.stem,flags=re.I).strip(),f.name)
    if x['sections']:candidates.append(x)
   if not candidates:report.append(f'SKIP {f.name}: no recognized SOURCE chord sections');continue
   x=max(candidates,key=lambda x:sum(len(s['rows']) for s in x['sections']))
   k=x['title'].casefold()
   if k in seen:report.append(f'SKIP duplicate title {f.name}');continue
   seen.add(k);out.append(x)
   n=sum(len(s['rows']) for s in x['sections'])
   report.append(f'OK {f.name}: key={x["key"]}; sections={len(x["sections"])}; rows={n}; lyrics/notes={sum(bool(s["lyrics"]) for s in x["sections"])}')
  except Exception as e:report.append(f'ERROR {f.name}: {e}')
 pathlib.Path('songs-import.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 pathlib.Path('conversion-report.txt').write_text('\n'.join(report)+f'\n\nConverted {len(out)} / {len(files)} xlsx files. REVIEW ALL RESULTS BEFORE IMPORT.\n',encoding='utf-8')
 print(f'Converted {len(out)} / {len(files)} files. See songs-import.json and conversion-report.txt')
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python convert_drive_excels.py FOLDER_WITH_XLSX_FILES')
 main(sys.argv[1])
