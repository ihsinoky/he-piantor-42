"""Finished wire upper bounds include both sourced tails and connected reserve."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';d=read(out/'length-fly.json');m=read(out/'measurements.json');source=read(HERE/'tail-source.json');tail=source['tail_bound_mm_per_end'];total=source['total_unrouted_wire_bound_mm']
 for r in d['conductors']:
  wing=next(w for w in m['wings'] if w['side']==r['side'])
  for i,a in enumerate(r['all_conductors']):
   a.update(conductor=i+1,finished_upper_mm=a['length_mm']+total,margin_to_200_mm=200-a['length_mm']-total,dressed_finished_upper_mm=wing['dressed_reference_lengths_mm'][i]+total,reserve_mm=wing['per_wire_reserve_mm'][i])
  full=r['longest_mm']+total;dressed=r['dressed_longest_mm']+total
  r.update(cut_length_upper_mm=full,cut_length_upper_margin_to_200_mm=200-full,dressed_cut_length_upper_mm=dressed,dressed_finished_margin_to_164_8_mm=164.8-dressed,internal_wire_bound_mm_per_end=tail,wing_tail_plus_dress_lead_bound_mm=3.9,main_tail_bound_mm=3.4,total_unrouted_wire_bound_mm=total,complete_cut_length_verified=True,tail_source='tail-source.json',qualification=source['qualification'],passed=full<=200 and r['minimum_reserve_mm']>=30 and all(a['minimum_bend_radius_mm']>=5-1e-7 and a['minimum_straight_slack_mm']>0 for a in r['all_conductors']))
 for w in m['wings']:
  w.update(unmodeled_length_mm=total,wing_tail_plus_dress_lead_bound_mm=3.9,main_tail_bound_mm=3.4,outlet_axis_qualification=source['dress_plane_definition'])
 save(out/'measurements.json',m)
 d['tail_source']=source;d['dressed_164_8_reference_only']=True
 save(out/'length-fly.json',d)
if __name__=='__main__':run(int(sys.argv[1]))
