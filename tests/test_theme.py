"""Tests du gestionnaire de theme core.design.theme (détection de thème mockée).

Nécessite une QApplication (plateforme offscreen) car ThemeManager hérite de QObject
et applique une feuille de style aux widgets.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.design.theme import ThemeManager  # noqa: E402
from modules.clock_module.clock_module import ClockModule  # noqa: E402
from PyQt6.QtCore import pyqtSignal, QObject  # noqa: E402
from PyQt6.QtGui import QColor  # noqa: E402
from PyQt6.QtWidgets import QWidget  # noqa: E402


class TestThemeManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = qapp()

    def setUp(self) -> None:
        # Le singleton est réinitialisé entre les tests pour garder chaque
        # test maître de la détection de thème qu'il souhaite simuler.
        ThemeManager._instance = None

    def tearDown(self) -> None:
        ThemeManager._instance = None

    def test_singleton_retourne_la_meme_instance(self):
        first = ThemeManager.instance()
        second = ThemeManager.instance()
        self.assertIsInstance(first, ThemeManager)
        self.assertIs(first, second)

    def test_signal_theme_changed_existe(self):
        self.assertIsInstance(ThemeManager.theme_changed, pyqtSignal)

    def test_variant_et_tokens_sont_coherents_quand_detection_mockée_dark(self):
        with patch.object(
            ThemeManager,
            "detect_system_variant",
            staticmethod(lambda: "dark"),
        ):
            manager = ThemeManager.instance()
            self.assertEqual(manager.variant(), "dark")
            self.assertEqual(manager.tokens().pill_background, QColor(15, 15, 15, 250))
            self.assertEqual(manager.tokens().accent_primary, QColor("#0A84FF"))

    def test_variant_et_tokens_sont_coherents_quand_detection_mockée_light(self):
        with patch.object(
            ThemeManager,
            "detect_system_variant",
            staticmethod(lambda: "light"),
        ):
            manager = ThemeManager.instance()
            self.assertEqual(manager.variant(), "light")
            self.assertEqual(manager.tokens().pill_background, QColor(242, 242, 244, 238))
            self.assertEqual(manager.tokens().accent_primary, QColor("#0078D7"))

    def test_detect_system_variant_registre_valeur_1_retourne_light(self):
        with patch("core.design.theme.winreg") as mock_winreg:
            mock_winreg.QueryValueEx.return_value = (1, 4)
            self.assertEqual(ThemeManager.detect_system_variant(), "light")

    def test_detect_system_variant_registre_valeur_0_retourne_dark(self):
        with patch("core.design.theme.winreg") as mock_winreg:
            mock_winreg.QueryValueEx.return_value = (0, 4)
            self.assertEqual(ThemeManager.detect_system_variant(), "dark")

    def test_detect_system_variant_cle_absente_retourne_light(self):
        with patch("core.design.theme.winreg") as mock_winreg:
            mock_winreg.OpenKey.side_effect = FileNotFoundError("clé absente")
            self.assertEqual(ThemeManager.detect_system_variant(), "light")

    def test_detect_system_variant_winreg_indisponible_retourne_light(self):
        with patch("core.design.theme.winreg", None):
            self.assertEqual(ThemeManager.detect_system_variant(), "light")

    def test_variant_dans_valeurs_attendues_sans_mock(self):
        """Lecture réelle du registre de la machine hôte (light ou dark)."""
        manager = ThemeManager.instance()
        self.assertIn(manager.variant(), ("light", "dark"))

    def test_apply_to_window_ne_plante_pas(self):
        manager = ThemeManager.instance()
        window = QWidget()
        manager.apply_to_window(window)
        window.close()
        window.deleteLater()

    def test_apply_to_module_ne_plante_pas(self):
        manager = ThemeManager.instance()
        module = ClockModule()
        try:
            manager.apply_to_module(module)
        finally:
            module.cleanup()


if __name__ == "__main__":
    unittest.main()
