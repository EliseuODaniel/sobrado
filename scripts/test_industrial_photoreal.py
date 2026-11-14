"""Contratos de preservação e de pares diurnos/noturnos."""
import json
import unittest

import industrial_photoreal_data as data


class PhotorealContracts(unittest.TestCase):
    def test_original_cameras_are_preserved(self):
        base = json.loads((data.ROOT / 'arquivos/versoes-anteriores-2026-11-14/relatorios/industrial-v05/modelo.json').read_text())
        new = {j['id']: j for j in data.validate()}
        for job in base['jobs']:
            for key in ['pos', 'target', 'mode']:
                self.assertEqual(new[job['id']][key], job[key])

    def test_day_night_pairs_use_exact_same_camera(self):
        jobs = data.validate()
        pilots = [j for j in jobs if j.get('pilot')]
        self.assertEqual(len(pilots), 6)
        for day in [j for j in pilots if j['lighting'] == 'day']:
            night = next(j for j in pilots if j['id'] == day['id'].replace('-dia', '-noite'))
            for key in ['pos', 'target', 'lens', 'mode', 'source_scene']:
                self.assertEqual(day[key], night[key])

    def test_no_historical_architecture_dependency(self):
        self.assertTrue((data.ROOT / data.CFG['base_blend']).is_file())
        self.assertFalse((data.ROOT / 'projeto/industrial-v04').exists())
        self.assertTrue((data.ROOT / 'arquivos/versoes-anteriores-2026-11-14/projeto/fontes/mobiliario-industrial.blend').is_file())

    def test_final_format_and_independent_destination(self):
        self.assertEqual(data.CFG['resolution'], [3840, 2880])
        self.assertNotEqual(data.CFG['base_blend'], data.CFG['output_blend'])
        self.assertLess(data.CFG['night_world_strength'], data.CFG['day_world_strength'])


if __name__ == '__main__':
    unittest.main()
