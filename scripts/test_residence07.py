"""Regressões contra mistura de tipologias e retorno das dimensões estimadas."""
import copy
import math
import unittest

import residence07_geometry as geo


class Residence07Tests(unittest.TestCase):
    def setUp(self):self.cfg=geo.load()

    def test_reject_other_unit(self):
        self.cfg['unit']='01'
        with self.assertRaises(AssertionError):geo.validate(self.cfg)

    def test_reject_opening_outside_wall(self):
        self.cfg['walls'][1]['openings'][0]['start']=20
        with self.assertRaises(AssertionError):geo.validate(self.cfg)

    def test_reject_overlapping_openings(self):
        wall=next(w for w in self.cfg['walls'] if w['id']=='S-fundos-banheiros')
        wall['openings'][1]['start']=.50
        with self.assertRaises(AssertionError):geo.validate(self.cfg)

    def test_reject_unclosed_vertical_levels(self):
        self.cfg['dimensions']['clear_height']=2.70
        with self.assertRaises(AssertionError):geo.validate(self.cfg)

    def test_outline_is_stepped(self):
        ground,upper=self.cfg['levels']
        self.assertEqual(min(y for x,y in upper['outline']),-1.2)
        self.assertIn([3.3,6.5],upper['outline'])
        self.assertIn([3.3,7.2],upper['outline'])
        self.assertIn([3.3,5.7],ground['outline'])
        self.assertLess(geo.area(upper['outline']),6.35*8.4)

    def test_gross_footprints_match_source_area_schedule(self):
        self.assertAlmostEqual(geo.area(self.cfg['levels'][0]['slabs'][0]),40.77)
        self.assertAlmostEqual(geo.area(self.cfg['levels'][1]['outline']),51.03)

    def test_winders_fill_the_turn(self):
        polys=geo.stair_polygons(self.cfg)
        self.assertEqual(len(polys),16)
        for p in polys:self.assertGreater(geo.area(p),0)
        # Leque ocupa o retângulo de 0,90 x 2,00 m, sem lacunas no retorno.
        self.assertAlmostEqual(sum(geo.area(p) for p in polys[5:11]),.90*2.0,places=7)
        self.assertAlmostEqual(sum(geo.area(p) for p in polys),2*1.25*.9+.9*2,places=7)

    def test_door_and_window_openings_have_no_solid(self):
        for wall in self.cfg['walls']:
            cells=list(geo.wall_cells(wall,2.55))
            for op in wall.get('openings',[]):
                mid=op['start']+op['width']/2;z=op.get('sill',0)+op['height']/2
                self.assertFalse(any(a<mid<b and z0<z<z1 for a,b,z0,z1 in cells),op['id'])

    def test_diagonal_has_true_metric_width(self):
        wall=next(w for w in self.cfg['walls'] if w['id']=='T-entrada-diagonal')
        op=wall['openings'][0]
        self.assertAlmostEqual(math.dist(geo.point(wall,op['start']),geo.point(wall,op['start']+op['width'])),.8)

    def test_all_cameras_have_distinct_organized_destinations(self):
        paths=[geo.artifact_path(v['id']) for v in self.cfg['views']]
        self.assertEqual(len(paths),len(set(paths)))
        for path in paths:self.assertNotEqual(path.parent,geo.ROOT/'renders/original')

    def test_structural_3d_has_own_folder(self):
        self.assertIn('02-estrutura/3d',str(geo.artifact_path('estrutura-terreo-3d')))
        self.assertIn('02-estrutura/2d',str(geo.artifact_path('estrutura-terreo','pdf')))

    def test_previews_are_separate(self):
        self.assertIn('_trabalho/previas',str(geo.preview_path('suite')))
        self.assertNotEqual(geo.preview_path('suite'),geo.artifact_path('suite'))

    def test_new_artifact_needs_explicit_category(self):
        with self.assertRaises(ValueError):geo.artifact_path('arquivo-sem-categoria')


if __name__=='__main__':unittest.main()
