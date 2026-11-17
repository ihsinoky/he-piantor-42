import re, sys
path=sys.argv[1]
s=open(path).read()
# find symbol instances with Reference J2/J3
def blocks(text, startpat):
    out=[]
    for m in re.finditer(startpat, text):
        i=m.start(); depth=0; j=i
        while j<len(text):
            if text[j]=='(': depth+=1
            elif text[j]==')':
                depth-=1
                if depth==0: break
            j+=1
        out.append((i,j+1,text[i:j+1]))
    return out
syms={}
for i,j,b in blocks(s, r'\(symbol \(lib_id'):
    ref=re.search(r'property "Reference" "(J[23])"', b)
    if ref:
        at=re.search(r'\(at ([\d.]+) ([\d.]+) (\d+)\)', b)
        mir='(mirror x)' in b or '(mirror y)' in b
        syms[ref.group(1)]=dict(at=(float(at.group(1)),float(at.group(2)),int(at.group(3))), mirror=mir, block=b)
print({k:(v['at'],v['mirror']) for k,v in syms.items()})
# lib symbol pin positions for the GH connector symbol used by J2/J3
libid=re.search(r'\(symbol \(lib_id "([^"]+)"\) \(at [\d.]+ [\d.]+ \d+\)[^)]*?property "Reference" "J2"', s)
print('lib', libid.group(1) if libid else None)
