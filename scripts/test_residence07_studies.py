"""Contratos geométricos das extensões; alturas e posições documentadas."""
import math
import unittest

import residence07_geometry as geo
import residence07_studies_data as data


class StudyGeometryTests(unittest.TestCase):
    def test_graph_has_valid_endpoints_and_same_system(self):
        graph=data.pipe_points();nodes={n['id']:n for n in graph['nodes']}
        self.assertEqual(len(nodes),len(graph['nodes']))
        for e in graph['edges']:
            self.assertEqual(nodes[e['a']]['system'],nodes[e['b']]['system'])
            self.assertEqual(e['system'],nodes[e['a']]['system'])
            self.assertTrue(0<e['nominal_diameter_m']<=.1)

    def test_zero_length_junctions_are_not_rendered_as_pipes(self):
        graph=data.pipe_points();nodes={n['id']:n for n in graph['nodes']}
        for e in graph['edges']:
            self.assertEqual(math.dist(nodes[e['a']]['xyz'],nodes[e['b']]['xyz'])<.001,e['geometry']=='junction')

    def test_documented_water_point_heights(self):
        nodes={n['id']:n for n in data.pipe_points()['nodes']}
        for key,z in [('AF-cozinha',.6),('AF-lavabo-vaso',.2),('AF-banho-suite-lavatorio',3.3),('AF-banho-social-chuveiro',4.8)]:
            self.assertAlmostEqual(nodes[key]['xyz'][2],z)

    def test_documented_electrical_heights(self):
        nodes=data.pipe_points()['nodes']
        for n in nodes:
            if n['kind']=='socket':self.assertTrue(any(abs(n['xyz'][2]-(level*2.7+h))<1e-8 for level in [0,1] for h in [.3,1.1,2.2]))
            if n['kind']=='switch':self.assertTrue(any(abs(n['xyz'][2]-(level*2.7+1.1))<1e-8 for level in [0,1]))

    def test_attic_opening_avoids_entire_tank(self):
        a=data.CFG['attic'];t=data.CFG['tank'];x,y=t['center_xy'];r=t['display_diameter']/2;h=a['floor_hole']
        self.assertTrue(h[1]<x-r or h[0]>x+r or h[3]<y-r or h[2]>y+r)
        self.assertGreater(min(data.roof_z(y-r),data.roof_z(y+r))-.08,t['base_z']+t['display_height']+.5)

    def test_attic_roof_envelope_preserved(self):
        self.assertAlmostEqual(data.roof_z(-1.35),5.4)
        self.assertAlmostEqual(data.roof_z(3),9.4)
        self.assertAlmostEqual(data.roof_z(7.35),5.4)

    def test_views_have_unique_destinations_and_four_shared_structures(self):
        views=data.views();paths=[data.output_path(v) for v in views]
        self.assertEqual(len(paths),len(set(paths)))
        self.assertEqual(sum(v['kind']=='structure' for v in views),4)
        self.assertEqual(sum(v['transparent'] for v in views),16)

    def test_unknown_render_source_is_rejected(self):
        self.assertFalse(geo.valid_render_record({'source_blend':'projeto/qualquer.blend','id':'estrutura-terreo-3d'}))
        self.assertFalse(geo.valid_render_record({'source_blend':data.CFG['services_blend'],'id':'sala'}))


if __name__=='__main__':unittest.main()
