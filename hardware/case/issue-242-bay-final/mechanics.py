"""Transparent screening calculations, N/mm/MPa; not FEA or a physical test."""
import json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
 # Worst-case assume only two of four retainers react a 10 N lid pull.
 P=10.;F=P/2;D=8.;hole=2.2;roof=1.6;slot=4.2
 ligaments=(D-slot)*roof
 # Skin screened as a simply supported strip across pocket's short span.
 L=7.75;b=21.35;E=69000.;Q=10.
 skin=[]
 for t in (.25,.22):
  I=b*t**3/12;Z=b*t*t/6
  skin.append(dict(thickness_mm=t,ten_newton_deflection_mm=Q*L**3/(48*E*I),ten_newton_bending_stress_MPa=Q*L/(4*Z),material_yield_screen_MPa=240,margin_to_yield=240/(Q*L/(4*Z))))
 result=dict(design_load_N=P,reacting_retainer_count=2,per_retainer_N=F,load_path='North: lid countersink -> M2x6 screw -> captured nut -> pocket roof -> OD8 pillar -> tray floor. South: lid countersink -> M2x10 screw -> existing Main H2/H3 boss threads -> tray floor. Downward south load passes through a removable POM spacer and original Main washer/PCB/boss stack.',screw_nominal_core_diameter_mm=1.6,screw_tension_MPa=F/(math.pi*.8**2),nut_roof_ligament_area_mm2=ligaments,nut_roof_stress_MPa=F/ligaments,printed_case_screen_allowable_MPa=3,roof_screen_factor=3/(F/ligaments),pillar_annulus_area_mm2=math.pi*(D*D-hole*hole)/4,pillar_axial_stress_MPa=F/(math.pi*(D*D-hole*hole)/4),south_boss_thread_engagement_mm=3.8,south_boss_thread_shear_area_mm2=math.pi*2*3.8/2,south_boss_thread_screen_stress_MPa=F/(math.pi*2*3.8/2),south_spacers_mm=dict(OD=4.5,ID=2.2,height=3.0,bottom_Z=11.7,top_Z=14.7),nut_AF_mm=4,nut_thickness_mm=1.6,nut_slot_mm=[4.2,1.7],roof_ligament_mm=roof,screw='2 x ISO 10642 M2x6 north + 2 x M2x10 south; minor shaft1.6, head OD4 x1.0. South pair replaces original Main H2/H3 M2x6; other Main screw unchanged.',nuts='2 x ISO 4032 M2, AF4, t1.6, captured without adhesive; south threads engage existing printed Main bosses.',skin_screen=skin,polymer_E_screen_MPa=2000,polymer_nominal_skin_deflection_mm=Q*L**3/(48*2000*(b*.25**3/12)),whole_cover_load_qualified=False,qualification_limit='Local strip and retention checks do not qualify the full perforated/pocketed panel, printed layer strength or 10N deflection of the unsupported centre. The colliding assembly cannot certify service/inversion. No gate5 PASS.',cost_USD=dict(one_off_cover_range=[85,290],batch10_per_cover_range=[25,80],retention_parts_range=[1,4],modified_trays_incremental_material_range=[.1,.5],basis='Planning only: 1.0–2.0 shop hours at $60–120/h; stock/fixture/finish $25–50. Batch amortizes setup. Not supplier quotations; no order proposed.'),material='6061-T6 aluminium, machined from supported stock to 1.50 nominal / 0.25 GH skin. 5052-H32 Wing stock is a comparison, not an automatic pocket machining qualification.',sources=[dict(url='https://srd.nist.gov/NSRDS/NSRDS-NBS-61-V.pdf',purpose='6061-T6 material context; E69GPa and 240MPa yield are explicit conservative study inputs, not lot certificates.'),dict(url='https://www.protolabs.com/media/iw0mfa0k/datasheet-sm-aluminum5052-h32.pdf',purpose='Wing-style 5052 comparison: typical E70.3GPa/yield193MPa; supplier cautions typical data is not for design.')])
 (HERE/'mechanics.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
