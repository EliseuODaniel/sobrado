"""Regressões da cobertura aprovada, sem variantes de acesso antigas."""
import unittest
import residence07_attic_roof as data

class CentralizedDormerTests(unittest.TestCase):

    def test_front_and_back_are_centered_on_the_house(self):
        self.assertEqual({d['id'] for d in data.CFG['dormers']}, {'frente', 'fundos'})
        for d in data.CFG['dormers']:
            self.assertEqual(d['center_x'], data.CFG['house_width'] / 2)
        self.assertEqual(data.CFG['dormers'][0]['width'], data.CFG['dormers'][1]['width'])

    def test_both_dormer_ridges_reach_the_main_ridge(self):
        junction = (data.CFG['house_width'] / 2, data.CFG['ridge_y'], data.CFG['ridge_z'])
        for d in data.CFG['dormers']:
            self.assertEqual(d['peak_z'], data.CFG['ridge_z'])
            for panel in data.dormer_panels(d):
                self.assertIn(junction, panel)
            self.assertEqual(data.opening(d)[3], list(junction[:2]))

    def test_full_center_ridge_has_no_lower_gap(self):
        for i in range(101):
            y = -0.65 + (6.15 + 0.65) * i / 100
            self.assertAlmostEqual(data.envelope_z(3.175, y), 9.4)

    def test_main_roof_partition_is_exact_without_degenerate_polygons(self):
        for d in data.CFG['dormers']:
            panels = data.roof_panels(d)
            self.assertAlmostEqual(sum((data.area(p) for p in panels)) + data.area(data.opening(d)), 6.35 * 4.35)
            for poly in panels:
                self.assertGreater(data.area(poly), 0)
                self.assertEqual(len(poly), len({tuple(p) for p in poly}))

    def test_roof_panels_cover_only_the_domain_outside_the_new_opening(self):
        for d in data.CFG['dormers']:
            start = -1.35 if d['direction'] == 1 else 3.0
            for i in range(41):
                for j in range(29):
                    point = (0.077 + i * 0.151, start + 0.061 + j * 0.148)
                    self.assertEqual(sum((data.inside(point, p) for p in data.roof_panels(d))), int(not data.inside(point, data.opening(d))))

    def test_valleys_match_the_main_roof_height(self):
        for d in data.CFG['dormers']:
            p = data.opening(d)
            for end in [p[2], p[4]]:
                for i in range(21):
                    t = i / 20
                    x = end[0] * (1 - t) + p[3][0] * t
                    y = end[1] * (1 - t) + p[3][1] * t
                    self.assertAlmostEqual(data.roof_z(y), data.dormer_z(x, d))
