import tempfile
import unittest
from datetime import date
from pathlib import Path
from carteira import load, compare, report

ROOT = Path(__file__).resolve().parents[1]

class ComparisonTests(unittest.TestCase):
    def test_priorities_and_independent_status(self):
        events = compare(load(ROOT/'examples/antes.csv'), load(ROOT/'examples/depois.csv'), date(2026, 9, 23))
        self.assertEqual([(e['id'], e['evento']) for e in events], [
            ('AF-101', 'saiu_do_mes'), ('AF-102', 'foi_para_fim_do_mes'),
            ('AF-102', 'status_alterado'), ('AF-103', 'status_alterado'), ('AF-105', 'incluido')])
        self.assertIn('R$ 12.500,00', report(events, date(2026, 9, 23)))

    def test_duplicate_rejected_with_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'bad.csv'
            path.write_text('id,cliente,valor,vencimento,status\n1,A,1,2026-09-01,emitido\n1,A,1,2026-09-01,emitido\n')
            with self.assertRaisesRegex(ValueError, 'linha 3: ID duplicado'):
                load(path)

if __name__ == '__main__':
    unittest.main()
