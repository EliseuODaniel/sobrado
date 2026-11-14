import unittest
import infrastructure_data as data


class InfrastructureTests(unittest.TestCase):
    def test_distribution_reaches_all_cold_points_through_equipment(self):
        graph = data.graph(); nodes = {n['id']: n for n in graph['nodes']}
        self.assertEqual(len(nodes), len(graph['nodes']))
        links = [(e['a'], e['b']) for e in graph['edges']]
        links += [(e['inlet'], e['outlet']) for e in graph['equipment']]
        reached = {'AF-REDE'}
        while True:
            more = {b for a, b in links if a in reached} - reached
            if not more: break
            reached |= more
        fixtures = {n['id'] for n in nodes.values() if n['kind'] == 'outlet' and n['system'] in {'cold', 'hot'}}
        self.assertTrue(fixtures)
        self.assertTrue(fixtures <= reached, fixtures-reached)

    def test_new_tank_connections_and_external_pending_ends(self):
        g = data.graph(); n = {v['id']: v for v in g['nodes']}
        self.assertAlmostEqual(n['AF-ENTRADA']['xyz'][0], 6.19)
        self.assertAlmostEqual(n['AF-ENTRADA']['xyz'][2], 6.35)
        self.assertAlmostEqual(n['AF-SAIDA']['xyz'][0], 4.51)
        self.assertEqual(n['AF-SAIDA']['xyz'][1], 3.175)
        self.assertIn(('AF-SAIDA', 'AF-DISTRIB'), {(e['a'], e['b']) for e in g['edges']})
        for prefix in ['EX', 'LP']:
            self.assertEqual(n[prefix+'-3']['kind'], 'connection_pending')
            self.assertGreater(n[prefix+'-3']['xyz'][1], 7.2)
        for e in g['edges']:
            self.assertEqual(n[e['a']]['system'], n[e['b']]['system'])

    def test_clipping_preserves_downward_direction_and_crosses_floors(self):
        self.assertEqual(data.clip_segment([1, 2, 6], [1, 2, 0], 2.7, 5.4), [[1., 2., 5.4], [1., 2., 2.7]])
        self.assertIsNone(data.clip_segment([0, 0, 8], [1, 0, 8], 0, 2.7))
        self.assertEqual(data.clip_segment([0, 0, 2], [1, 0, 2], 0, 2.7), [[0, 0, 2], [1, 0, 2]])


if __name__ == '__main__': unittest.main()
