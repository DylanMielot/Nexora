"""Tests du module horloge (criteres T003-6 a T003-10)."""

import os
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.base_module import BaseModule  # noqa: E402
from modules.clock_module.clock_module import (  # noqa: E402
    ClockModule,
    _french_date_string,
)
from PyQt6.QtWidgets import QWidget  # noqa: E402

_EXAMPLE_DATETIME = datetime(2026, 11, 9, 15, 45, 30)  # un lundi


class _FixedDateTime(datetime):
    """Date/heure figee pour des tests déterministes sur l'affichage."""

    @classmethod
    def now(cls):
        return datetime(2026, 11, 9, 15, 45, 30)


class TestClockModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = qapp()

    def test_herite_de_base_module(self):
        self.assertTrue(issubclass(ClockModule, BaseModule))
        # Pas de methode abstraite restante : instantiable directement.
        self.assertEqual(ClockModule.__abstractmethods__, frozenset())

    def test_attributs(self):
        self.assertEqual(ClockModule.module_id, "clock")
        self.assertEqual(ClockModule.display_name, "Horloge")

    def test_instanciation(self):
        module = ClockModule()
        self.assertIsInstance(module, BaseModule)
        module.cleanup()

    def test_tailles(self):
        module = ClockModule()
        try:
            self.assertEqual(module.get_reduced_size(), (200, 60))
            self.assertEqual(module.get_expanded_size(), (400, 160))
        finally:
            module.cleanup()

    def test_widgets(self):
        module = ClockModule()
        try:
            reduced = module.get_reduced_widget()
            expanded = module.get_expanded_widget()
            self.assertIsInstance(reduced, QWidget)
            self.assertIsInstance(expanded, QWidget)
            self.assertIsNot(reduced, expanded)
        finally:
            module.cleanup()

    def test_mode_reduit_format_hhmm(self):
        with patch("modules.clock_module.clock_module.datetime", _FixedDateTime):
            module = ClockModule()
            try:
                self.assertEqual(module.get_reduced_widget().text(), "15:45")
                self.assertRegex(
                    module.get_reduced_widget().text(), r"^\d{2}:\d{2}$"
                )
            finally:
                module.cleanup()

    def test_chiffre_date_francais_exemple(self):
        """Exemple du critere : 'Lundi 9 Novembre 2026'."""
        self.assertEqual(
            _french_date_string(datetime(2026, 11, 9)), "Lundi 9 Novembre 2026"
        )
        self.assertEqual(
            _french_date_string(datetime(2026, 11, 10)), "Mardi 10 Novembre 2026"
        )

    def test_mode_etendu_format_hhmmss_date(self):
        with patch("modules.clock_module.clock_module.datetime", _FixedDateTime):
            module = ClockModule()
            try:
                text = module.get_expanded_widget().text()
                self.assertEqual(text, "15:45:30\nLundi 9 Novembre 2026")
                self.assertRegex(
                    text,
                    r"^\d{2}:\d{2}:\d{2}\n"
                    r"(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche) "
                    r"\d{1,2} "
                    r"(Janvier|Fevrier|Mars|Avril|Mai|Juin|Juillet|Aout|"
                    r"Septembre|Octobre|Novembre|Decembre) "
                    r"\d{4}$",
                )
            finally:
                module.cleanup()

    def test_timer_une_seconde(self):
        module = ClockModule()
        try:
            self.assertTrue(module._timer.isActive())
            self.assertEqual(module._timer.interval(), 1000)
        finally:
            module.cleanup()

    def test_on_click_rafraichit(self):
        with patch("modules.clock_module.clock_module.datetime", _FixedDateTime):
            module = ClockModule()
            try:
                module.on_click()
                self.assertEqual(module.get_reduced_widget().text(), "15:45")
                self.assertEqual(
                    module.get_expanded_widget().text(),
                    "15:45:30\nLundi 9 Novembre 2026",
                )
            finally:
                module.cleanup()

    def test_text_correspond_a_l_instant_present(self):
        """Le texte affiche correspond a l'heure systeme au moment de la creation."""
        module = ClockModule()
        try:
            now = datetime.now()
            self.assertEqual(module.get_reduced_widget().text(), now.strftime("%H:%M"))
            expected = (
                f"{now.strftime('%H:%M:%S')}\n{_french_date_string(now)}"
            )
            self.assertEqual(module.get_expanded_widget().text(), expected)
        finally:
            module.cleanup()
