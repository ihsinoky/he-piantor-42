"""Adversarial geometry/clustering checks, independent of the captured board."""
import copy
import unittest
from classify import spacing, group_events, shared_conflict, contains


def capsule(a, b, radius=.1):
    return dict(a=a, b=b, radius=radius, object_id=str((a, b)))


def event(a, b, layer='top', nets=('A', 'B'), required=.2):
    gap, p, q = spacing(a, b)
    return dict(shapes=[a, b], layer=layer, nets=list(nets),
                witness=[p, q], gap_mm=gap, required_mm=required)


class GeometryTests(unittest.TestCase):
    def test_parallel_spacing(self):
        self.assertAlmostEqual(spacing(capsule((0, 0), (2, 0)), capsule((0, .3), (2, .3)))[0], .1)

    def test_crossing_copper_contact(self):
        self.assertLess(spacing(capsule((0, 0), (2, 0)), capsule((1, -1), (1, 1)))[0], 0)

    def test_zero_length_via_and_trace(self):
        self.assertAlmostEqual(spacing(capsule((0, 0), (0, 0), .3), capsule((.5, -1), (.5, 1)))[0], .1)

    def test_rectangle_edge(self):
        pad = dict(polygon=[(-1, -1), (1, -1), (1, 1), (-1, 1)], object_id='pad')
        self.assertAlmostEqual(spacing(pad, capsule((1.4, -2), (1.4, 2)))[0], .3)

    def test_hole_intrusion_not_an_unrelated_net_short(self):
        pad = dict(polygon=[(-1, -1), (1, -1), (1, 1), (-1, 1)], object_id='pad')
        hole = capsule((0, 0), (0, 0), .15)
        self.assertAlmostEqual(spacing(pad, hole)[0], -.15)

    def test_repeated_copper_under_different_ids(self):
        e = event(capsule((0, 0), (2, 0)), capsule((0, .3), (2, .3)))
        duplicate = copy.deepcopy(e)
        duplicate['shapes'][0]['object_id'] = 'another trace id'
        self.assertEqual(len(group_events([e, duplicate])[0]), 1)

    def test_same_nets_distant_faults_remain_separate(self):
        e = event(capsule((0, 0), (2, 0)), capsule((0, .3), (2, .3)))
        f = event(capsule((10, 0), (12, 0)), capsule((10, .3), (12, .3)))
        self.assertEqual(len(group_events([e, f])[0]), 2)

    def test_layers_do_not_merge(self):
        e = event(capsule((0, 0), (2, 0)), capsule((0, .3), (2, .3)))
        f = copy.deepcopy(e)
        f['layer'] = 'bottom'
        self.assertFalse(shared_conflict(e, f))

    def test_net_pairs_do_not_merge(self):
        e = event(capsule((0, 0), (2, 0)), capsule((0, .3), (2, .3)))
        f = copy.deepcopy(e)
        f['nets'] = ['A', 'C']
        self.assertFalse(shared_conflict(e, f))

    def test_continuous_route_joint_merges(self):
        a = capsule((0, 0), (2, 0))
        e = event(a, capsule((0, .3), (1, .3)))
        f = event(a, capsule((1, .3), (2, .3)))
        self.assertEqual(len(group_events([e, f])[0]), 1)

    def test_joint_proof_preserves_net_side_orientation(self):
        fixed = capsule((0, .3), (2, .3))
        e = event(fixed, capsule((0, 0), (1, 0)))
        f = event(fixed, capsule((1, 0), (2, 0)))
        proof = shared_conflict(e, f)
        self.assertTrue(proof)
        p, q = proof['points']
        for original in (e, f):
            self.assertTrue(contains(original['shapes'][0], p))
            self.assertTrue(contains(original['shapes'][1], q))

    def test_shared_via_different_sides_do_not_merge(self):
        via = capsule((0, 0), (0, 0), .3)
        e = event(via, capsule((.5, -.5), (.5, .5)))
        f = event(via, capsule((-.5, -.5), (-.5, .5)))
        self.assertEqual(len(group_events([e, f])[0]), 2)

    def test_pad_and_attached_trace_share_conflict(self):
        pad = dict(polygon=[(-1, -.1), (1, -.1), (1, .1), (-1, .1)], object_id='pad')
        trace = capsule((-1, 0), (1, 0))
        other = capsule((0, .35), (1, .35))
        self.assertEqual(len(group_events([event(pad, other), event(trace, other)])[0]), 1)

    def test_nearby_distinct_copper_never_merges_by_distance(self):
        a = capsule((0, 0), (.01, 0), .001)
        b = capsule((0, .003), (.01, .003), .001)
        c = capsule((.0121, 0), (.0221, 0), .001)
        d = capsule((.0121, .003), (.0221, .003), .001)
        self.assertEqual(len(group_events([event(a, b), event(c, d)])[0]), 2)


if __name__ == '__main__':
    unittest.main()
