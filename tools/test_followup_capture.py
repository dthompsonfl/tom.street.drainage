import importlib.util
import unittest
from pathlib import Path

class FollowupCaptureTests(unittest.TestCase):
    def module(self):
        path=Path(__file__).with_name('acquire_followup_sources.py')
        self.assertTrue(path.is_file(), 'Followup capture implementation missing')
        spec=importlib.util.spec_from_file_location('followup',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        return m
    def test_pdf_magic_not_extension(self):
        m=self.module()
        self.assertEqual(m.validate_payload(b'%PDF-1.7\nverified syntax later','pdf'),'PDF_BYTES_NOT_YET_REVIEWED')
        with self.assertRaises(ValueError):m.validate_payload(b'<html>login</html>','pdf')
    def test_json_error_and_truncated_search(self):
        m=self.module()
        with self.assertRaises(ValueError):m.validate_payload(b'{"error":{"code":403}}','json')
        self.assertEqual(m.validate_payload(b'{"features":[],"exceededTransferLimit":true}','json'),'PARTIAL_TRANSFER_LIMIT')
        self.assertEqual(m.validate_payload(b'{"features":[]}','json'),'EMPTY_SEARCH_NOT_ABSENCE_PROOF')
    def test_html_remains_context_not_plan(self):
        m=self.module()
        self.assertEqual(m.validate_payload(b'<html><title>County portal</title></html>','html'),'HTML_CAPTURE_NOT_PLAN_VERIFICATION')
        with self.assertRaises(ValueError):m.validate_payload(b'','html')
    def test_hosts_and_transport_locked(self):
        m=self.module()
        for url in ('http://santarosa.fl.gov/x','https://evil.example/x','https://santarosa.fl.gov.evil.example/x','https://u:p@santarosa.fl.gov/x'):
            with self.assertRaises(ValueError):m.check_url(url)
        self.assertEqual(m.check_url('https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/12483/1396775/pdf'),'https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/12483/1396775/pdf')
    def test_fixed_inventory_unique_safe_names(self):
        m=self.module(); names=[x[0] for x in m.ITEMS]
        self.assertEqual(len(names),len(set(names)))
        self.assertTrue(all(__import__('re').fullmatch('[A-Z0-9_]+',n) for n in names))
        for _,url,_ in m.ITEMS:m.check_url(url)

if __name__=='__main__':unittest.main()
