"""Tests du point d'entree main.py (critere T002-5)."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import main  # noqa: E402


class TestMain(unittest.TestCase):
    @patch("main.QApplication")
    @patch("main.DynamicIslandWindow")
    def test_main_charge_horloge_retourne_code_exec(
        self, mock_window_cls, mock_app_cls
    ):
        mock_app = MagicMock()
        mock_app.exec.return_value = 0
        mock_app_cls.return_value = mock_app
        mock_window = MagicMock()
        mock_window_cls.return_value = mock_window

        rc = main.main()

        self.assertEqual(rc, 0)
        mock_app_cls.assert_called_once()
        # Une fenetre est creee avec le module horloge charge par le gestionnaire.
        mock_window_cls.assert_called_once()
        self.assertEqual(
            mock_window_cls.call_args.kwargs["module"].module_id, "clock"
        )
        mock_window.show.assert_called_once()
        mock_app.exec.assert_called_once()

    def test_main_est_appelable(self):
        self.assertTrue(callable(main.main))
