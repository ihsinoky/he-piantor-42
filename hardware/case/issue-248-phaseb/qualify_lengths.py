"""Do not claim a full conductor cut length from outlet-to-outlet routing alone."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';d=read(out/'length-fly.json');m=read(out/'measurements.json')
 for r in d['conductors']:
  routed=r['longest_mm'];dressed=r['dressed_longest_mm']
  r.update(routed_budget_passed=routed<=200 and dressed<=164.8,cut_length_upper_mm=routed+11.4,cut_length_upper_margin_to_200_mm=200-routed-11.4,dressed_cut_length_upper_mm=dressed+11.4,internal_wire_bound_mm_per_end=5.7,complete_cut_length_verified=False,qualification='Routed curves terminate at nominal outlet dress planes. B1 GHR-14V-S plug axial bound 5.70 mm/end conservatively bounds internal straight wire, not a sourced crimp reference plane. Full cut-length gate remains failed; the routed-only margin is not a finished conductor margin.',passed=False)
 for w in m['wings']:
  w.update(unmodeled_length_mm=None,routed_curve_only=True,terminal_internal_bound_mm_per_end=5.7,terminal_internal_length_verified=False)
 save(out/'length-fly.json',d);save(out/'measurements.json',m)
if __name__=='__main__':run(int(sys.argv[1]))
