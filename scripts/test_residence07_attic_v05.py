import unittest
import residence07_geometry as geo
import residence07_attic_v05_data as data


class StackedStairTests(unittest.TestCase):
    def test_all_sixteen_treads_have_exact_same_xy(self):
        for i,(old,new) in enumerate(zip(geo.stair_polygons(geo.load()),data.steps())):
            self.assertEqual(old,new['polygon']);self.assertAlmostEqual(new['top']-(i+1)*.16875,2.7)

    def test_small_landing_stays_over_first_two_steps_with_clearance(self):
        self.assertTrue(data.on_floor(4.2,3.7));self.assertTrue(data.on_floor(4.5,3.7));self.assertFalse(data.on_floor(4.7,3.7))
        self.assertAlmostEqual(data.validate()['minimum_stair_clearance_m'],2.2125)

    def test_front_opening_closed_and_l_shaped_opening_cut(self):
        self.assertTrue(data.on_floor(5,.5));self.assertFalse(data.on_floor(5,2.6));self.assertFalse(data.on_floor(5,3.7))
        cells=data.floor_cells()
        self.assertTrue(any(a<5<b and c<.5<d for a,b,c,d in cells))
        self.assertFalse(any(a<5<b and c<2.6<d for a,b,c,d in cells))

    def test_relocated_tank_is_clear_of_both_stair_flights(self):
        tank=data.CFG['tank'];self.assertLess(tank['center_xy'][0]+.9,min(x for s in data.steps() for x,y in s['polygon']))
        self.assertEqual(tank['base_z'],5.45);self.assertEqual(tank['capacity_liters'],1000)

    def test_all_views_share_one_layout_and_new_stair_exit_is_at_existing_xy(self):
        self.assertEqual(data.CFG['stair']['upper_exit'],[4.1,2.6,5.4])
        jobs=data.jobs();self.assertEqual(sum(j['group']=='main' for j in jobs),18)
        self.assertEqual(sum(j['group']=='detail' for j in jobs),6);self.assertEqual(sum(j['group']=='orbit' for j in jobs),24)


if __name__=='__main__':unittest.main()
