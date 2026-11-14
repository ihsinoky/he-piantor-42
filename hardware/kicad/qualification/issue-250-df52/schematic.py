"""Main symbol identity replacement, retaining every existing electrical wire.
Wing intentionally has no invented passive-only schematic/ERC substitute.
"""
from pathlib import Path
import json,re,hashlib
E=Path(__file__).resolve().parent;src=E.parent/'issue-240-main-rev7/schematic';w=E/'main'
def end(s,start):
 d=0;quote=False;escape=False
 for i in range(start,len(s)):
  c=s[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':d+=1
  elif c==')':
   d-=1
   if not d:return i+1
 raise ValueError('unbalanced')
def update(s,ref):
 needle='(symbol "'+ref+'"';i=s.index(needle);j=end(s,i);block=s[i:j]
 block=block.replace('SM14B-GHS-TB(LF)(SN)','DF52-14S-0.8H(21)').replace('(number "15"','(number "MP"')
 return s[:i]+block+s[j:]
s=(src/'main.kicad_sch').read_text()
for ref in ('Rev4:J2','Rev4:J3'):
 s=update(s,ref)
 needle='(symbol (lib_id "'+ref+'")';i=s.index(needle);j=end(s,i);block=s[i:j].replace('SM14B-GHS-TB(LF)(SN)','DF52-14S-0.8H(21)').replace('(property "Footprint" "'+ref+'"','(property "Footprint" "DF52:DF52-14S-0.8H_14"')
 s=s[:i]+block+s[j:]
(w/'main.kicad_sch').write_text(s)
s=(src/'review.kicad_sym').read_text()
# Frozen library has unqualified names.
for ref in ('J2','J3'):s=update(s,ref)
(w/'review.kicad_sym').write_text(s)
(w/'sym-lib-table').write_text((src/'sym-lib-table').read_text())
