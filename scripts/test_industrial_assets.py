"""Contratos do download: integridade, retomada e proteção de arquivos existentes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import fetch_industrial_assets as assets


class AssetDownloadTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='casa-assets-test-')
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.content=b'asset-fixture-validado'
        self.downloads=0
        self.bad_md5=False

    def response(self,url):
        if url.startswith('https://api.polyhaven.com/'):
            asset=url.rsplit('/',1)[1]
            item={'url':'https://dl.polyhaven.org/'+asset+'.bin','size':len(self.content),
                'md5':'0'*32 if self.bad_md5 else hashlib.md5(self.content).hexdigest()}
            if asset=='slate_floor_03':
                data={'Diffuse':{'2k':{'jpg':item}},'Rough':{'2k':{'jpg':dict(item,url=item['url']+'rough')}},'nor_gl':{'2k':{'exr':dict(item,url=item['url']+'normal')}}}
            else:data={'blend':{'2k':{'blend':item}}}
            return json.dumps(data).encode()
        self.downloads+=1
        return self.content

    def test_verified_files_are_reused_without_download_or_rewrite(self):
        with patch.object(assets,'FOLDER',self.folder),patch.object(assets,'ROOT',self.folder),patch.object(assets,'request',side_effect=self.response):
            assets.main();first=self.downloads
            files={p:p.stat().st_mtime_ns for p in self.folder.rglob('*') if p.is_file() and p.name!='manifesto.json'}
            assets.main()
            self.assertEqual(self.downloads,first)
            self.assertEqual({p:p.stat().st_mtime_ns for p in files},files)

    def test_changed_local_file_is_preserved_and_rejected(self):
        with patch.object(assets,'FOLDER',self.folder),patch.object(assets,'ROOT',self.folder),patch.object(assets,'request',side_effect=self.response):
            assets.main()
            model=self.folder/'modern_arm_chair_01/modern_arm_chair_01_2k.blend'
            model.write_bytes(b'alteracao-local')
            with self.assertRaises(AssertionError):assets.main()
            self.assertEqual(model.read_bytes(),b'alteracao-local')

    def test_bad_upstream_hash_does_not_create_a_model(self):
        self.bad_md5=True
        with patch.object(assets,'FOLDER',self.folder),patch.object(assets,'ROOT',self.folder),patch.object(assets,'request',side_effect=self.response):
            with self.assertRaises(AssertionError):assets.main()
            self.assertEqual(list(self.folder.rglob('*.blend')),[])

    def test_untrusted_endpoint_is_rejected_before_network(self):
        with self.assertRaises(AssertionError):assets.request('https://example.com/asset')


if __name__=='__main__':unittest.main()
