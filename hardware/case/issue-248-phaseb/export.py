"""Manufacturing and fitted preview exports, including rejected candidates."""
from common import *
def mesh_absolute(q,path):
 from OCP.BRepMesh import BRepMesh_IncrementalMesh
 from OCP.StlAPI import StlAPI_Writer
 BRepTools.Clean_s(q.wrapped)
 mesh=BRepMesh_IncrementalMesh(q.wrapped,.005,False,.025,True);mesh.Perform()
 writer=StlAPI_Writer();writer.ASCIIMode=False;assert writer.Write(q.wrapped,str(path))
 data=path.read_bytes();header=f'PROVISIONAL plateau Z{TOP:.2f}; Junana q=1.50; absolute mesh 0.005 mm'.encode().ljust(80,b' ')
 path.write_bytes(header+data[80:])
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);groups={}
 for n,k,s in raw:groups.setdefault(n,[]).append(s)
 assembly=[];prints=[]
 for n,ss in groups.items():
  if n.startswith('USB-reference-'):continue
  q=ss[0] if len(ss)==1 else Compound(children=ss);q.label=n+'-PROVISIONAL-q1.50';assembly.append(q)
  if not n.startswith(('tray-','post-','splice-','shell-central','strip-left','strip-right')) or '-screw-' in n:continue
  folder=out/'manufacturing';folder.mkdir(exist_ok=True)
  stem=n+'-PROVISIONAL'
  q.parent=None;export_step(q,folder/(stem+'.step'))
  mesh_absolute(import_step(folder/(stem+'.step')),folder/(stem+'.stl'))
  b=bounds(q);size=[b[1][i]-b[0][i] for i in range(3)];brim=[size[0]+10,size[1]+10,size[2]]
  prints.append(dict(name=n,filename=stem,bounds_mm=b,valid=q.is_valid,solids=len(ss),volume_mm3=q.volume,with_5mm_brim_xyz_mm=brim,envelope_passed=brim[0]<=220 and brim[1]<=220 and brim[2]<=250,manufacturing_geometry_passed=q.is_valid and len(ss)==1,step_sha256=sha(folder/(stem+'.step')),stl_sha256=sha(folder/(stem+'.stl'))))
  print(pitch,'export',n,len(ss),'solids',flush=True)
 for q in assembly:q.parent=None
 export_step(Compound(children=assembly),out/'fitted-assembly-PROVISIONAL.step')
 save(out/'manufacturing.json',dict(status=P['status'],parts=prints,preview_sha256=sha(out/'fitted-assembly-PROVISIONAL.step')))
 print(pitch,'preview exported',flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
