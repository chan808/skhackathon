import io
import unittest
from argparse import Namespace
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

from practice.__main__ import doctor


class EnvironmentTests(unittest.TestCase):
    def test_doctor_rejects_unsupported_python_even_if_materials_work(self):
        with patch("practice.__main__.sys.version_info", (3, 9, 13)), patch("practice.__main__.platform.python_version", return_value="3.9.13"), patch("practice.__main__.save_json") as save, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(doctor(Namespace()), 2)
        report = save.call_args.args[1]
        self.assertFalse(report["supported_python"])
        self.assertEqual(report["minimum_python"], "3.11")

    def test_supported_doctor_checks_all_banks_without_model_api(self):
        with patch("practice.__main__.sys.version_info", (3, 12, 14)), patch("practice.__main__.save_json") as save, redirect_stdout(io.StringIO()):
            self.assertEqual(doctor(Namespace()), 0)
        report = save.call_args.args[1]
        self.assertTrue(report["supported_python"])
        self.assertEqual(report["backend_selected_questions"], 20)
        self.assertTrue(report["lab_validated"])
        self.assertFalse(report["external_python_packages_required"])
