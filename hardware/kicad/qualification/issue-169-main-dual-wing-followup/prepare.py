"""Author Stage 2 board from #155, fixed original component coordinates.
Power seeds are deliberate engineering paths; D-019 signal routing remains unchanged.
"""
from common import *
import pcbnew as p, math, shutil, csv
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
assert not (E/'frozen-inputs.json').exists(), 'Never overwrite frozen inputs or restart attempts'
w=E/'inputs/global';w.mkdir(parents=True,exist_ok=True)
source=R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final'
assert digest(source/'main.kicad_pcb')=='fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
shutil.copyfile(source/'main.kicad_pro',w/'main.kicad_pro')
b=p.LoadBoard(str(source/'main.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
drawings=b.GetDrawings(); zones=list(b.Zones())
original={r:dict(x=p.ToMM(f.GetPosition().x),y=p.ToMM(f.GetPosition().y),angle=f.GetOrientationDegrees(),pads={a.GetNumber():a.GetNetname() for a in f.Pads()}) for r,f in fps.items()}
for d in drawings:
 if d.GetLayer()!=p.Edge_Cuts:continue
 for get,setter in [(d.GetStart,d.SetStart),(d.GetEnd,d.SetEnd)]:
  v=get()
  if v.y==p.FromMM(78):setter(p.VECTOR2I(v.x,p.FromMM(70)))
for z in zones:
 if z.GetIsRuleArea():continue
 z.UnFill();poly=z.Outline();poly.RemoveAllContours();poly.NewOutline()
 for x,y in [(76,70),(124,70),(124,122),(76,122)]:q=V(x,y);poly.Append(q.x,q.y)
removed=[];removed_native=[]
for t in list(b.GetTracks()):
 # Preserve original MCU power and QSPI as complete networks plus three USB bonds.
 if t.GetNetname() in {'V1V1','V3V3','QSPI_SD0','QSPI_SD1','QSPI_SD2','QSPI_SD3','QSPI_SCLK','QSPI_SS_MCU','QSPI_SS_FLASH'} or (not isinstance(t,p.PCB_VIA) and abs(p.ToMM(t.GetWidth())-.2)<1e-9):continue
 removed.append(t.m_Uuid.AsString());removed_native.append(t);b.Remove(t)
nets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
def net(n):
 if n not in nets:
  a=p.NETINFO_ITEM(b,n);b.Add(a);nets[n]=a
 return nets[n]
def padnet(f,num,n):
 for a in f.Pads():
  if a.GetNumber()==str(num):a.SetNet(net(n))
def clone(src,ref,x,y,n1=None,n2=None,value=None):
 f=fps[src].Duplicate();f.SetReference(ref);f.SetPosition(V(x,y));f.SetOrientationDegrees(0);b.Add(f);fps[ref]=f
 f.SetFPID(p.LIB_ID('Stage169',ref));f.Reference().SetVisible(False);f.Value().SetVisible(False)
 if value:f.SetValue(value)
 if n1 is not None:padnet(f,1,n1)
 if n2 is not None:padnet(f,2,n2)
 return f
# Frozen connector pin contract, GPIO6 and explicit pull-down.
f=clone('J2','J3',105,73,value='BM14B-GHS-TBT(LF)(SN)');padnet(f,7,'MUX_EN1')
padnet(fps['U1'],8,'MUX_EN1')
clone('R6','R16',94,109,'MUX_EN1','GND','100k')
# Datasheet RNM0015A land pattern, TI drawing 4222000/B 03/2020.
# Pads 7/8 and 12/13 are same-net pairs; connecting bar is retained explicitly.
f=p.FOOTPRINT(b);f.SetReference('U6');f.SetValue('TPS63070RNMR');f.SetFPID(p.LIB_ID('Stage169','U6'));f.SetAttributes(p.FP_SMD);f.Reference().SetVisible(False);f.Value().SetVisible(False)
def land(num,x,y,sx,sy,n):
 ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.F_Mask);ls.AddLayer(p.F_Paste)
 a=p.PAD(f);a.SetNumber(str(num));a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_RECT);a.SetSize(V(sx,sy));a.SetPosition(V(x,y));a.SetLayerSet(ls);a.SetNet(net(n));f.Add(a)
for num,y,n in [(1,-.75,'GND'),(2,-.25,'RAIL_PG'),(3,.25,'VAUX'),(4,.75,'GND')]:land(num,-1.15,y,.6,.25,n)
for num,x,n in [(15,-.725,'GND'),(14,-.225,'HALL_PWR_EN'),(13,.275,'VBUS'),(12,.775,'VBUS')]:land(num,x,-1.4,.25,.6,n)
for num,x,n in [(5,-.725,'FB_5V2'),(6,-.225,'GND'),(7,.275,'V5V2'),(8,.775,'V5V2')]:land(num,x,1.4,.25,.6,n)
land(12,.525,-1.225,.75,.25,'VBUS');land(7,.525,1.225,.75,.25,'V5V2')
for num,x,y,sx,n in [(9,.6,.5,1.35,'SW2'),(10,.425,0,1.7,'GND'),(11,.6,-.5,1.35,'SW1')]:land(num,x,y,sx,.25,n)
f.SetPosition(V(85,73.5));b.Add(f);fps['U6']=f
# Inductor: Coilcraft XFL4020-152MEC, 4x4mm, 1.5uH; 1.2..1.8uH tolerance.
f=p.FOOTPRINT(b);f.SetReference('L1');f.SetValue('1.5uH XFL4020-152MEC');f.SetFPID(p.LIB_ID('Stage169','L1'));f.SetAttributes(p.FP_SMD);f.Reference().SetVisible(False);f.Value().SetVisible(False)
for num,x,n in [(1,-1.55,'SW1'),(2,1.55,'SW2')]:land(num,x,0,1.3,3.6,n)
f.SetPosition(V(89.5,74));b.Add(f);fps['L1']=f
# Converter input/VAUX/output and precision 55k/10k feedback divider.
# Local bulk selected independently from existing 1uF C18 which stays at USB input.
clone('C14','C23',82,71.7,'VBUS','GND','22uF 16V X6S 0805')
clone('C14','C24',89.5,71,'VBUS','GND','22uF 16V X6S 0805')
clone('C15','C25',81.5,74.5,'VAUX','GND','100nF')
for ref,x,y in [('C26',91.8,77.5),('C27',93,80),('C28',96.2,80)]:clone('C14',ref,x,y,'V5V2','GND','22uF 16V X6S 0805')
clone('R6','R17',81.8,77,'V5V2','FB_5V2','54.9k 0.1% 25ppm/K')
clone('R6','R18',78.8,78,'FB_5V2','GND','10k 0.1% 25ppm/K')
clone('R6','R19',94.5,84.5,'V3V3','RAIL_PG','100k')
# U6 enable shares common default-off command, after USB configuration permission.
# U5 blocks Hall load and U6 disconnects VIN in shutdown. No unpermitted always-on rail.
padnet(fps['U5'],1,'V5V2')
# Deliberate low-resistance seeds. Signal routing must retain these exact paths.
seeds=[]
def path(n,layer,width,points):
 for (x1,y1),(x2,y2) in zip(points,points[1:]):
  if x1==x2 and y1==y2:continue
  t=p.PCB_TRACK(b);t.SetStart(V(x1,y1));t.SetEnd(V(x2,y2));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(net(n));b.Add(t);seeds.append(t.m_Uuid.AsString())
def via(n,x,y):
 a=p.PCB_VIA(b);a.SetPosition(V(x,y));a.SetWidth(p.FromMM(.6));a.SetDrill(p.FromMM(.3));a.SetViaType(p.VIATYPE_THROUGH);a.SetLayerPair(p.F_Cu,p.B_Cu);a.SetNet(net(n));b.Add(a);seeds.append(a.m_Uuid.AsString())
# U5 small pins escape narrowly, then paired vias / 3mm back-layer branches.
path('HALL_5V',p.F_Cu,.3,[(82.84,106.35),(83.55,106.35),(83.55,105)])
path('HALL_5V',p.F_Cu,.6,[(83.55,105),(84.35,105)])
for x in [83.55,84.35]:via('HALL_5V',x,105)
path('HALL_5V',p.B_Cu,1,[(83.55,105),(84.35,105),(86,105)])
path('HALL_5V',p.B_Cu,3,[(86,105),(90,101),(90,87.5),(110,87.5),(115.5,81),(115.5,72.2)])
path('HALL_5V',p.B_Cu,.6,[(115.5,72.2),(113.125,72.2),(113.125,71.3)])
via('HALL_5V',113.125,71.3);path('HALL_5V',p.F_Cu,.5,[(113.125,71.3),(113.125,73)])
path('HALL_5V',p.B_Cu,3,[(86,105),(86,120),(118.125,120),(121.5,116.625),(121.5,113),(118.125,113)])
via('HALL_5V',118.125,113);path('HALL_5V',p.F_Cu,.5,[(118.125,113),(118.125,116)])
# Ground pad escapes provide actual barrel contact to In1; no signal tracks on In1.
for ref in ['J2','J3']:
 for a in fps[ref].Pads():
  if a.GetNetname()!='GND':continue
  x,y=p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)
  yy=y+1.5
  via('GND',x,yy);path('GND',p.F_Cu,.3,[(x,y),(x,yy)])
# Main supply from local V5V2 bulk to U5, separate from Hall branch copper.
path('V5V2',p.F_Cu,.3,[(81.16,106.35),(80.65,106.35),(80,105.85)])
path('V5V2',p.F_Cu,.6,[(80,105.85),(80,105.05)])
via('V5V2',80,105.05)
path('V5V2',p.In2_Cu,1,[(80,105.85),(80,105.05)])
via('V5V2',80,105.85)
path('V5V2',p.In2_Cu,1,[(80,105.85),(82.5,103.35)])
path('V5V2',p.In2_Cu,2.4,[(82.5,103.35),(83,102.85),(83,87),(92,87),(92,77),(90,77),(85.275,75.9)])
via('V5V2',90,77)
via('V5V2',85.275,75.9)
path('V5V2',p.F_Cu,.25,[(85.275,74.9),(85.275,75.9)])
path('SW1',p.F_Cu,.4,[(85.6,73),(86.7,72.7),(87.95,72.7)])
path('SW2',p.F_Cu,.4,[(85.6,74),(86.7,74),(86.7,76.4),(91.05,76.4),(91.05,74)])
# GND near load switch and converter, outside same-net pin pitch keepout.
for ref,num,x,y in [('U5','2',79.5,107),('U6','4',83.15,74.25)]:
 a=next(a for a in fps[ref].Pads() if a.GetNumber()==num)
 via('GND',x,y);path('GND',p.F_Cu,.25,[(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)),(x,y)])
mpns={**{r:'GRM21BC81C226ME44L' for r in ['C23','C24','C26','C27','C28']},'C25':'GRM155R71E104KE14D','R17':'TNPW060354K9BEEA','R18':'TNPW060310K0BEEA','U6':'TPS63070RNMR','L1':'XFL4020-152MEC','J3':'BM14B-GHS-TBT(LF)(SN)'}
for ref in set(fps)-set(original):
 f=fps[ref]
 for key,value in [('SourceID','Issue169 explicit addition '+ref)]+([('MPN',mpns[ref])] if ref in mpns else []):
  field=f.GetFieldByName(key) if f.HasFieldByName(key) else f.AddField(p.PCB_FIELD(f,f.GetNextFieldId(),key))
  field.SetText(value);field.SetVisible(False)
# Store reference library snapshots, avoid cached library overrides in independent DRC.
lib=E/'Stage169.pretty';lib.mkdir(exist_ok=True);io=p.PCB_IO_KICAD_SEXPR()
for f in b.GetFootprints():
 f.SetFPID(p.LIB_ID('Stage169',f.GetReference()));io.FootprintSave(str(lib),f)
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Stage169")(type "KiCad")(uri "${KIPRJMOD}/../../Stage169.pretty")(options "")(descr "Frozen source footprints")))\n')
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
# Circuit intent is a separately reviewed explicit extension of the unchanged source pad contract.
rows=[]
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
 for a in f.Pads():rows.append(dict(ref=f.GetReference(),value=f.GetValue(),pin=a.GetNumber(),net=a.GetNetname(),intentional_nc=not a.GetNetname(),x_mm=p.ToMM(a.GetPosition().x),y_mm=p.ToMM(a.GetPosition().y)))
save(E/'circuit-intent.json',dict(original=original,pad_contract=rows,source_hash=digest(source/'main.kicad_pcb'),forced_pwm='U6.1=GND',converter_enable='U6.14=HALL_PWR_EN; common default-off; no rail before configuration',feedback='0.8*(1+54.9k/10k)=5.192V; 5.2V target unchanged',output_switch='U5.1=V5V2; U5.6=HALL_5V; branches start near U5',mounting_holes_unchanged=True))
save(E/'routing-scope.json',dict(frozen_utc=now(),max_global_attempts=2,global_timeout_seconds=2400,max_local_repair_attempts=0,local_timeout_seconds=0,local_repair_only_if_global_has_specific_diagnosed_failures=False,manual_preflight_revision_limit=6,condition_args=ARGS,removed_copper_uuids=removed,seed_copper_uuids=seeds,original_0200mm_bonds_retained=3,signal_layer_policy='F.Cu/In2.Cu/B.Cu; In1.Cu GND only',no_width_clearance_layer_or_escalation_relaxation=True))
print('Stage169 prepared',len(fps),'footprints',len(rows),'pads',len(seeds),'power/ground seeds')
