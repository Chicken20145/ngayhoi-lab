"""The measured conservative threshold must reject a borderline unrelated question."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hoi import tra_loi

class MeasuredThreshold(unittest.TestCase):
    def test_borderline_score_does_not_trigger_generation_by_default(self):
        docs = [(0.59, {'nguon': 'Điều 2', 'noi_dung': 'Đăng ký tham gia'})]
        with patch('hoi.tim', return_value=docs), patch('hoi.requests.post') as generate:
            generate.return_value.json.return_value = {'response': 'Quy chế không đề cập.'}
            result = tra_loi('Có được vay tiền sinh viên không?')
        self.assertTrue(result['tu_choi'])
        self.assertFalse(result['goi_mo_hinh'])
        generate.assert_not_called()

    def test_model_refusal_variants_are_canonical_and_marked(self):
        docs = [(0.9, {'nguon': 'Điều 7', 'noi_dung': 'CV phải là PDF.'})]
        for answer in ['Quy chế không đề cập. [Điều 7]', 'Quy chế không đề cập [Điều 7].']:
            with self.subTest(answer=answer), patch('hoi.tim', return_value=docs), patch('hoi.requests.post') as generate:
                generate.return_value.json.return_value = {'response': answer}
                result = tra_loi('Câu hỏi ngoài nguồn', seed=42)
                self.assertTrue(result['tu_choi'])
                self.assertEqual('Quy chế không đề cập.', result['tra_loi'])
                self.assertEqual(0, generate.call_args.kwargs['json']['options']['temperature'])

    def test_missing_or_invented_citation_falls_back_to_visible_source(self):
        docs = [(0.9, {'nguon': 'Điều 7. Hồ sơ', 'noi_dung': '## Điều 7. Hồ sơ\nCV phải ở định dạng PDF.'})]
        for answer in ['Không', 'Có thể gửi Word. [Điều 99]']:
            with self.subTest(answer=answer), patch('hoi.tim', return_value=docs), patch('hoi.requests.post') as generate:
                generate.return_value.json.return_value = {'response': answer}
                result = tra_loi('CV gửi Word được không?')
                self.assertTrue(result.get('can_kiem_tra'))
                self.assertIn('CV phải ở định dạng PDF.', result['tra_loi'])
                self.assertIn('[Điều 7]', result['tra_loi'])
                self.assertNotIn('Điều 99', result['tra_loi'])

if __name__ == '__main__':
    unittest.main()
