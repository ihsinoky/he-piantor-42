"""Bounded independent structured-file reader for visible non-copper primitives.
Expected records are frozen read-only historical NON-copper comparisons;
authoring consumes fresh source instead. Unsupported primitives fail.
"""
import json,math,collections,sys
from pathlib import Path
import sexpdata as sx
ROOT=Path(__file__).resolve().parent
def kids(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def one(n,k):
    xs=kids(n,k);assert len(xs)==1,(k,len(xs));return xs[0]
def mm(x):return round(x,6)
def world(x,y):return (mm(100+x),mm(100-y))
def signature(kind,layer,**fields):
    def numeric(x):
        if isinstance(x,bool):return x
        if isinstance(x,(int,float)):return float(mm(x))
        if isinstance(x,list) or isinstance(x,tuple):return [numeric(v) for v in x]
        if isinstance(x,dict):return {k:numeric(v) for k,v in x.items()}
        return x
    return json.dumps(numeric(dict(kind=kind,layer=layer,**fields)),sort_keys=True)
def line(a,z,layer,width):return signature('line',layer,points=sorted([list(a),list(z)]),width=mm(width))
def expected():
    result=[]
    for e in json.loads((ROOT/'auxiliary-contract-v2.json').read_text())['records']:
        kind=e['type'];layer='F.SilkS' if e.get('layer')=='top' else 'B.SilkS'
        if kind in ['pcb_silkscreen_path','pcb_courtyard_outline']:
            pts=e['route'] if kind=='pcb_silkscreen_path' else e['outline'];pts=[world(x['x'],x['y']) for x in pts]
            if kind=='pcb_courtyard_outline':pts.append(pts[0]);layer='F.CrtYd'
            result.extend(line(a,z,layer,e.get('stroke_width',.05)) for a,z in zip(pts,pts[1:]))
        elif kind in ['pcb_silkscreen_rect','pcb_courtyard_rect']:
            x,y=e['center']['x'],e['center']['y'];w,h=e['width'],e['height'];angle=e.get('ccw_rotation',0)
            assert angle in [0,90]
            if angle==90:w,h=h,w
            pts=[world(x+dx,y+dy) for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
            if kind=='pcb_courtyard_rect':layer='F.CrtYd'
            result.extend(line(a,z,layer,e.get('stroke_width',.05)) for a,z in zip(pts,pts[1:]+pts[:1]))
        elif kind=='pcb_silkscreen_text':
            result.append(signature('text',layer,text=e['text'],position=world(e['anchor_position']['x'],e['anchor_position']['y']),size=[e['font_size']]*2,angle=e.get('ccw_rotation',0)))
        elif kind=='pcb_solder_paste':
            layer='F.Paste' if e['layer']=='top' else 'B.Paste';x,y=e['x'],e['y']
            if e['shape']=='rect':result.append(signature('rect',layer,bounds=sorted([list(world(x-e['width']/2,y-e['height']/2)),list(world(x+e['width']/2,y+e['height']/2))]),width=0,filled=True))
            elif e['shape']=='circle':result.append(signature('circle',layer,center=world(x,y),radius=e['radius'],width=0,filled=True))
            elif e['shape']=='oval':
                w,h=e['width'],e['height'];dx,dy=max(w-h,0)/2,max(h-w,0)/2;result.append(line(world(x-dx,y-dy),world(x+dx,y+dy),layer,min(w,h)))
            else:raise AssertionError('unsupported expected paste')
    return collections.Counter(result)
def actual(path):
    root=sx.loads(Path(path).read_text());result=[]
    aliases={'F.Silkscreen':'F.SilkS','B.Silkscreen':'B.SilkS','F.Courtyard':'F.CrtYd','B.Courtyard':'B.CrtYd'}
    for n in root:
        if not isinstance(n,list) or not str(n[0]).startswith('gr_'):continue
        kind=str(n[0]);layer=one(n,'layer')[1];layer=aliases.get(layer,layer)
        if layer=='Edge.Cuts':continue
        assert layer in ['F.SilkS','B.SilkS','F.CrtYd','B.CrtYd','F.Paste','B.Paste'],('unexpected conductive/artwork layer',layer)
        if kind=='gr_line':result.append(line(one(n,'start')[1:3],one(n,'end')[1:3],layer,one(one(n,'stroke'),'width')[1]))
        elif kind=='gr_rect':result.append(signature('rect',layer,bounds=sorted([one(n,'start')[1:3],one(n,'end')[1:3]]),width=one(one(n,'stroke'),'width')[1],filled=str(one(n,'fill')[1])=='yes'))
        elif kind=='gr_circle':
            center=one(n,'center')[1:3];end=one(n,'end')[1:3];result.append(signature('circle',layer,center=center,radius=mm(math.dist(center,end)),width=one(one(n,'stroke'),'width')[1],filled=str(one(n,'fill')[1])=='yes'))
        elif kind=='gr_text':
            pos=one(n,'at');font=one(one(n,'effects'),'font');result.append(signature('text',layer,text=n[1],position=pos[1:3],size=one(font,'size')[1:3],angle=pos[3] if len(pos)>3 else 0))
        else:raise AssertionError(('unsupported actual primitive',kind))
    # Added default CAD reference/value ink would be unrequested extra artwork.
    for fp in kids(root,'footprint'):
        for prop in kids(fp,'property'):
            if prop[1] in ['Reference','Value']:assert str(one(prop,'hide')[1])=='yes'
    return collections.Counter(result)
if __name__=='__main__':
    exp,got=expected(),actual(sys.argv[1]);diff=dict(missing=list((exp-got).elements()),added=list((got-exp).elements()))
    Path(sys.argv[2]).write_text(json.dumps(dict(primitives=sum(got.values()),difference=diff,scope='Exact visible primitive/content/size/angle/layer reconciliation at KiCad nanometre grid. Native text uses KiCad stroke glyphs; original tscircuit font designation remains in oracle and is a declared renderer distinction, not copper or footprint substitution.'),indent=2)+'\n')
    assert not diff['missing'] and not diff['added'],diff
    print('all visible auxiliary primitives individually reconciled')
