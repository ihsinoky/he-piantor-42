import copy
import unittest
from analyze import distance_point_segment, extract

class AnalysisTests(unittest.TestCase):
    def record(self, gap=.115, typ='pcb_via_trace_clearance_error'):
        return dict(record_id='R',type=typ,actual_minimum_spacing_mm=gap,required_clearance_mm=.2,cluster_ids=['C1','C2'],
            objects=[dict(id='v',kind='pcb_via',nets=['A'],pcb_trace_id='own',stock_autorouted=True,x=0,y=.4+gap,outer_diameter=.6,hole_diameter=.3),
                     dict(id='t',kind='pcb_trace',nets=['B'],stock_autorouted=True,source_trace_id='s',source_ports=[])],
            violating_primitive_pairs=[dict(gap_mm=gap,layer='top',geometry=[dict(object_id='t',a=[-1,0],b=[1,0],radius=.1)])])
    def test_distance_endpoints_and_degenerate(self):
        self.assertEqual(distance_point_segment([2,0],[0,0],[1,0]),1)
        self.assertEqual(distance_point_segment([3,4],[0,0],[0,0]),5)
        self.assertAlmostEqual(distance_point_segment([.5,.515],[0,0],[1,0]),.515)
    def test_signature_type_and_band(self):
        d=extract([self.record(),self.record(.11529),self.record(.11531),self.record(typ='pcb_trace_error')])
        self.assertEqual(d['summary']['raw_records'],2)
    def test_shared_ids_not_independent_counts(self):
        a=self.record();b=copy.deepcopy(a);b['record_id']='R2'
        d=extract([a,b]);s=d['summary']
        self.assertEqual((s['raw_records'],s['distinct_vias'],s['distinct_traces'],s['distinct_net_pairs'],s['physical_clusters']),(2,1,1,1,2))
        self.assertEqual(d['records'][0]['same_via_signature_records'],2)
    def test_bad_accepted_geometry_rejected(self):
        a=self.record();a['objects'][0]['outer_diameter']=.5
        with self.assertRaises(AssertionError):extract([a])

if __name__=='__main__':unittest.main()
