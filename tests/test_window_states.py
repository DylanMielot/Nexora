"""Tests des etats interactifs de DynamicIslandWindow (T012).

Couvre :
- enterEvent / leaveEvent (survol) et pill_background variant plus claire ;
- mousePressEvent / mouseReleaseEvent (pression) et pill_background_pressed ;
- l'eventFilter sur les widgets enfants (clic transmis par un enfant) ;
- les evenements de focus : toleres sans planter et sans modifier la couleur
  de la pilule (aucun etat visuel dedie au focus dans l'implementation courante).

Necessite une QApplication (plateforme offscreen) car DynamicIslandWindow est un QWidget.
"""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.window import DynamicIslandWindow  # noqa: E402
from PyQt6.QtCore import QEvent, QPointF, Qt  # noqa: E402
from PyQt6.QtGui import QEnterEvent, QFocusEvent, QMouseEvent  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402


class TestDynamicIslandWindowStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = qapp()

    def _create_window(self):
        window = DynamicIslandWindow()  # aucun module : toggle() reste sans effet
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        return window

    def _press_event(self, pos=QPointF(10, 10)) -> QMouseEvent:
        return QMouseEvent(
            QEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

    def _release_event(self, pos=QPointF(10, 10)) -> QMouseEvent:
        return QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

    def test_etat_initial_repos(self):
        window = self._create_window()
        self.assertFalse(window._hovered)
        self.assertFalse(window._pressed)
        self.assertEqual(
            window._pill_background_color(), window._tokens.pill_background
        )

    def test_enter_event_active_le_survol(self):
        window = self._create_window()
        window.enterEvent(QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10)))
        self.assertTrue(window._hovered)
        attendu = DynamicIslandWindow._lighter_variant(window._tokens.pill_background)
        self.assertEqual(window._pill_background_color(), attendu)
        self.assertNotEqual(window._pill_background_color(), window._tokens.pill_background)

    def test_leave_event_desactive_le_survol(self):
        window = self._create_window()
        window.enterEvent(QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10)))
        window.leaveEvent(QEvent(QEvent.Type.Leave))
        self.assertFalse(window._hovered)
        self.assertEqual(window._pill_background_color(), window._tokens.pill_background)

    def test_mouse_press_event_active_la_pression(self):
        window = self._create_window()
        window.mousePressEvent(self._press_event())
        self.assertTrue(window._pressed)
        self.assertEqual(
            window._pill_background_color(), window._tokens.pill_background_pressed
        )

    def test_mouse_release_event_desactive_la_pression(self):
        window = self._create_window()
        window.mousePressEvent(self._press_event())
        window.mouseReleaseEvent(self._release_event())
        self.assertFalse(window._pressed)
        self.assertEqual(window._pill_background_color(), window._tokens.pill_background)

    def test_eventfilter_enfant_presse_mets_la_fenetre_en_pression(self):
        window = self._create_window()
        enfant = QWidget(window)
        window.eventFilter(enfant, self._press_event())
        self.assertTrue(window._pressed)
        self.assertEqual(
            window._pill_background_color(), window._tokens.pill_background_pressed
        )
        window.eventFilter(enfant, self._release_event())
        self.assertFalse(window._pressed)
        self.assertEqual(window._pill_background_color(), window._tokens.pill_background)

    def test_evenements_focus_ne_modifient_pas_la_couleur_de_pilule(self):
        """FocusIn/FocusOut sont toleres : aucun etat visuel dedie au focus aujourd'hui.

        La couleur de la pilule et les drapeaux survol/pression doivent rester inchanges.
        """
        window = self._create_window()
        couleur_avant = window._pill_background_color()
        for type_evenement in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            with self.subTest(event=type_evenement):
                QApplication.instance().sendEvent(
                    window,
                    QFocusEvent(type_evenement, Qt.FocusReason.MouseFocusReason),
                )
        self.assertFalse(window._hovered)
        self.assertFalse(window._pressed)
        self.assertEqual(window._pill_background_color(), couleur_avant)
        self.assertEqual(window._pill_background_color(), window._tokens.pill_background)


if __name__ == "__main__":
    unittest.main()
