"""Contratos da proposta: mesma arquitetura atual e variantes separadas."""
import json
from pathlib import Path
import unittest

import residence07_industrial_data as data


class IndustrialDataTests(unittest.TestCase):
    def test_current_source_and_independent_output(self):
        self.assertEqual(data.CFG['base_blend'],'arquivos/versoes-anteriores-2026-11-14/projeto/residencia-07-atual/casa-07-atual.blend')
        self.assertNotEqual(data.CFG['base_blend'],data.CFG['furniture_library'])
        self.assertNotEqual(data.CFG['output_blend'],data.CFG['base_blend'])

    def test_all_twenty_current_cameras_are_preserved(self):
        source=json.loads((data.ROOT/'relatorios/original/estudo-instalacoes-atico/atual-modelo.json').read_text())
        jobs={j['id']:j for j in data.jobs()}
        for original in source['jobs']:
            self.assertIn(original['id'],jobs)
            for key in ['pos','target','mode']:self.assertEqual(original[key],jobs[original['id']][key])

    def test_unique_industrial_destinations(self):
        jobs=data.jobs();self.assertEqual(len(jobs),25)
        self.assertEqual(len({j['file'] for j in jobs}),25)
        self.assertTrue(all(Path(j['file']).as_posix().startswith('arquivos/versoes-anteriores-2026-11-14/renders/industrial-v05/') for j in jobs))

    def test_office_is_an_explicit_alternative(self):
        offices={j['id'] for j in data.jobs() if j['mode']=='office'}
        self.assertEqual(offices,{'escritorio-alternativa','escritorio-reverso'})
        self.assertTrue(data.CFG['office']['alternative'])

    def test_dining_fits_available_living_width(self):
        dining=data.CFG['dining'];x,y=dining['center'];w,l,h=dining['table_size']
        self.assertGreater(x-w/2,.15);self.assertLess(x+w/2,3.30)
        self.assertGreater(y-l/2,3);self.assertLess(y+l/2,5.70)
        for cx,cy in dining['chairs']:
            self.assertGreater(cx-.24,.15);self.assertLess(cx+.24,3.30)


if __name__=='__main__':unittest.main()
