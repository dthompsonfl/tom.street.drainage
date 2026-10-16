import importlib.util
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).with_name('acquire_question_sources.py')
M = None
if P.exists():
    spec = importlib.util.spec_from_file_location('research', P)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)

class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(M, 'The audited acquisition module has not been implemented')

    def test_rejects_unapproved_host_or_protocol(self):
        for url in ['http://services.arcgis.com/x', 'https://evil.example/x',
                    'https://services.arcgis.com.evil.example/x',
                    'https://user:pass@services.arcgis.com/x']:
            with self.assertRaises(ValueError):
                M.check_url(url)

    def test_accepts_official_fixed_service(self):
        self.assertEqual(M.check_url(M.STREETS), M.STREETS)

    def test_json_api_error_not_success(self):
        with self.assertRaises(ValueError):
            M.parse_capture(b'{"error":{"code":403}}')

    def test_error_html_not_json(self):
        with self.assertRaises(ValueError):
            M.parse_capture(b'<html>login</html>')

    def test_empty_search_is_not_absence_finding(self):
        obj = M.parse_capture(b'{"features":[]}')
        self.assertEqual(M.classify(obj), 'EMPTY_SEARCH_NOT_ABSENCE_PROOF')

    def test_truncation_not_complete(self):
        self.assertEqual(M.classify({'features': [], 'exceededTransferLimit': True}),
                         'PARTIAL_TRANSFER_LIMIT')

    def test_capture_preserves_bytes_and_refuses_overwrite(self):
        raw = b'{"features": [ ]}\n'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'capture.json'
            M.write_once(p, raw)
            self.assertEqual(p.read_bytes(), raw)
            with self.assertRaises(FileExistsError):
                M.write_once(p, b'changed')

if __name__ == '__main__':
    unittest.main()
