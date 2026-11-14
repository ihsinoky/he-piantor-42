"""Finished wire upper bounds include both sourced tails and connected reserve."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';d=read(out/'length-fly.json');m=read(out/'measurements.json');source=read(HERE/'tail-source.json');tail=source['tail_bound_mm_per_end']
 for r in d['conductors']:
  full=r['longest_mm']+2*tail;dressed=r['dressed_longest_mm']+2*tail
  r.update(cut_length_upper_mm=full,cut_length_upper_margin_to_200_mm=200-full,dressed_cut_length_upper_mm=dressed,dressed_finished_margin_to_164_8_mm=164.8-dressed,internal_wire_bound_mm_per_end=tail,complete_cut_length_verified=True,tail_source='tail-source.json',qualification=source['qualification'],passed=full<=200 and r['minimum_reserve_mm']>=30 and all(a['minimum_bend_radius_mm']>=5-1e-7 and a['minimum_straight_slack_mm']>0 for a in r['all_conductors']))
 d['tail_source']=source;d['dressed_164_8_reference_only']=True
 save(out/'length-fly.json',d)
if __name__=='__main__':run(int(sys.argv[1]))
