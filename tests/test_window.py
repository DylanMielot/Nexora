"""Tests de la fenetre pilule core.window.DynamicIslandWindow (criteres T002-3 et T002-4)."""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.window import (  # noqa: E402
    ANIMATION_DURATION_MS,
    DynamicIslandWindow,
    EXPANDED_SIZE,
    REDUCED_SIZE,
    module_size,
)
from modules.clock_module.clock_module import ClockModule  # noqa: E402
from PyQt6.QtCore import QEvent, QPointF, QSize, QEasingCurve, Qt  # noqa: E402
from PyQt6.QtGui import QEnterEvent, QKeyEvent, QMouseEvent  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402


class TestDynamicIslandWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = qapp()

    def _create_with_clock(self):
        return DynamicIslandWindow(module=ClockModule())

    def test_sans_module_taille_reduite(self):
        window = DynamicIslandWindow()
        try:
            self.assertEqual(window.size(), QSize(*REDUCED_SIZE))
            self.assertFalse(window.is_expanded)
        finally:
            window.close()
            window.deleteLater()

    def test_drapeaux_fenetre_pilule(self):
        window = DynamicIslandWindow()
        try:
            flags = window.windowFlags()
            self.assertTrue(flags & Qt.WindowType.FramelessWindowHint)
            self.assertTrue(flags & Qt.WindowType.WindowStaysOnTopHint)
            self.assertTrue(window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        finally:
            window.close()
            window.deleteLater()

    def test_masque_pilule_non_vide(self):
        window = DynamicIslandWindow()
        try:
            self.assertFalse(window.mask().isEmpty())
        finally:
            window.close()
            window.deleteLater()

    def test_avec_module_taille_reduite_du_module(self):
        window = self._create_with_clock()
        try:
            self.assertEqual(window.size(), QSize(200, 60))
            self.assertFalse(window.is_expanded)
            self.assertEqual(window._stack.currentIndex(), 0)
        finally:
            window.close()
            window.deleteLater()

    def test_configuration_animation(self):
        window = DynamicIslandWindow()
        try:
            self.assertEqual(window._animation.duration(), ANIMATION_DURATION_MS)
            self.assertEqual(
                window._animation.easingCurve().type(), QEasingCurve.Type.InOutQuad
            )
        finally:
            window.close()
            window.deleteLater()

    def test_etendre_et_reduire_animent_la_taille(self):
        window = self._create_with_clock()
        try:
            window.expand()
            QTest.qWait(350)  # laisse l'animation de 300 ms atteindre sa fin
            self.assertTrue(window.is_expanded)
            self.assertEqual(window.size(), QSize(*EXPANDED_SIZE))
            self.assertEqual(window._stack.currentIndex(), 1)

            window.collapse()
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
            self.assertEqual(window.size(), QSize(*REDUCED_SIZE))
            self.assertEqual(window._stack.currentIndex(), 0)
        finally:
            window.close()
            window.deleteLater()

    def test_bascule_et_appel_on_click(self):
        window = self._create_with_clock()
        try:
            window.toggle()
            QTest.qWait(350)
            self.assertTrue(window.is_expanded)

            window.toggle()
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
        finally:
            window.close()
            window.deleteLater()

    def test_position_centre_haut_ecran_principal(self):
        screen = self._app.primaryScreen()
        geometry = screen.availableGeometry()
        window = DynamicIslandWindow()
        try:
            window._position_on_primary_screen()
            self.assertEqual(window.y(), geometry.top())
            self.assertEqual(
                window.x(), geometry.x() + (geometry.width() - window.width()) // 2
            )
        finally:
            window.close()
            window.deleteLater()

    def test_touche_echap_ferme(self):
        window = DynamicIslandWindow()
        try:
            event = QKeyEvent(
                QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier
            )
            window.keyPressEvent(event)
            self.assertTrue(window.isHidden())
        finally:
            window.close()
            window.deleteLater()

    def test_clic_gauche_bascule(self):
        """T020 : le clic ne pilote plus l'etat ; le survol declenche l'agrandissement.

        mousePressEvent ne bascule plus la fenetre : un clic gauche laisse la
        pilule reduite. C'est enterEvent (survol) qui agrandit, et leaveEvent
        qui reduit.
        """
        window = self._create_with_clock()
        try:
            # Un clic gauche ne declenche plus l'agrandissement de la pilule.
            event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                QPointF(10, 10),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            window.mousePressEvent(event)
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
            self.assertEqual(window.size(), QSize(200, 60))

            # Le survol (enter) agrandit la pilule.
            window.enterEvent(
                QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
            )
            QTest.qWait(350)
            self.assertTrue(window.is_expanded)
            self.assertEqual(window.size(), QSize(*EXPANDED_SIZE))
            self.assertEqual(window._stack.currentIndex(), 1)

            # La sortie de la souris (leave) reduit la pilule.
            window.leaveEvent(QEvent(QEvent.Type.Leave))
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
            self.assertEqual(window.size(), QSize(*REDUCED_SIZE))
            self.assertEqual(window._stack.currentIndex(), 0)
        finally:
            window.close()
            window.deleteLater()

    def test_module_size_helper(self):
        self.assertEqual(module_size(None, False), (200, 60))
        self.assertEqual(module_size(None, True), (400, 160))
        module = ClockModule()
        self.assertEqual(module_size(module, False), (200, 60))
        self.assertEqual(module_size(module, True), (400, 160))
