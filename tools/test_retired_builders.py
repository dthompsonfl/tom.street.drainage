#!/usr/bin/env python3
"""Ensure historical register/output builders cannot clobber current registers.

This is an AST-only check. It NEVER imports or executes a legacy builder.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = (
    '00_CONTROL/tools/build_registers.py',
    '00_CONTROL/tools/build_registers2.py',
    '00_CONTROL/tools/build_canonical_registers.py',
    '00_CONTROL/tools/build_claim_source_links.py',
    '00_CONTROL/tools/build_public_extracts.py',
    '00_CONTROL/tools/build_packet_pdfs.py',
)


def is_main_conditional(node: ast.If) -> bool:
    comp = node.test
    if not isinstance(comp, ast.Compare) or len(comp.ops) != 1 or not isinstance(comp.ops[0], ast.Eq):
        return False
    pieces = [comp.left, *comp.comparators]
    return any(isinstance(x, ast.Name) and x.id == '__name__' for x in pieces) and \
        any(isinstance(x, ast.Constant) and x.value == '__main__' for x in pieces)


class RetiredBuilderTests(unittest.TestCase):
    def test_all_historical_builder_entrypoints_fail_before_writing(self):
        for rel in HISTORICAL:
            with self.subTest(path=rel):
                file = ROOT / rel
                self.assertTrue(file.is_file())
                tree = ast.parse(file.read_text(encoding='utf-8'), filename=rel)
                mains = [n for n in tree.body if isinstance(n, ast.If) and is_main_conditional(n)]
                self.assertEqual(len(mains), 1, f'{rel} must have exactly one main entrypoint')
                self.assertTrue(mains[0].body and isinstance(mains[0].body[0], ast.Raise),
                                f'{rel} must raise immediately on CLI entry before any register writes')
                raise_expr = mains[0].body[0].exc
                self.assertTrue(isinstance(raise_expr, ast.Call) and
                                isinstance(raise_expr.func, ast.Name) and raise_expr.func.id == 'SystemExit',
                                f'{rel} must use explicit SystemExit for its retirement guard')

    def test_current_generators_are_not_treated_as_legacy(self):
        for rel in ('tools/build_reconciled_packet.py', 'tools/build_neighbor_toolkit.py'):
            self.assertTrue((ROOT/rel).is_file(), f'current generator absent: {rel}')
            self.assertNotIn(rel, HISTORICAL)


if __name__ == '__main__':
    unittest.main()
