"""Tests de la fenetre pilule core.window.DynamicIslandWindow (criteres T002-3 et T002-4)."""

import os
import sys
import unittest
from unittest import mock
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.window import (  # noqa: E402
    ANIMATION_DURATION_MS,
    DynamicIslandWindow,
    ISLAND_SIZE_EXPANDED,
    ISLAND_SIZE_REDUCED,
    module_size,
)
import core.window as core_window  # noqa: E402
from modules.clock_module.clock_module import ClockModule  # noqa: E402
from PyQt6.QtCore import (  # noqa: E402
    QEvent,
    QPointF,
    QRect,
    QRectF,
    QSize,
    QEasingCurve,
    Qt,
)
from PyQt6.QtGui import (  # noqa: E402
    QEnterEvent,
    QKeyEvent,
    QMouseEvent,
    QPaintEvent,
    QPainter,
)
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
            self.assertEqual(window.size(), QSize(*ISLAND_SIZE_REDUCED))
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

    def test_aucun_masque_qbitmap_sur_pilule(self):
        """T026 : le masque QBitmap a ete supprime de core/window.py ;
        le widget ne porte plus de masque de forme (QBitmap vide)."""
        window = DynamicIslandWindow()
        try:
            self.assertTrue(window.mask().isEmpty())
        finally:
            window.close()
            window.deleteLater()

    def test_avec_module_taille_reduite_du_module(self):
        window = self._create_with_clock()
        try:
            self.assertEqual(window.size(), QSize(200, 40))
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
            self.assertEqual(window.size(), QSize(*ISLAND_SIZE_EXPANDED))
            self.assertEqual(window._stack.currentIndex(), 1)

            window.collapse()
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
            self.assertEqual(window.size(), QSize(*ISLAND_SIZE_REDUCED))
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
            self.assertEqual(window.size(), QSize(200, 40))

            # Le survol (enter) agrandit la pilule.
            window.enterEvent(
                QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
            )
            QTest.qWait(350)
            self.assertTrue(window.is_expanded)
            self.assertEqual(window.size(), QSize(*ISLAND_SIZE_EXPANDED))
            self.assertEqual(window._stack.currentIndex(), 1)

            # La sortie de la souris (leave) reduit la pilule.
            window.leaveEvent(QEvent(QEvent.Type.Leave))
            QTest.qWait(350)
            self.assertFalse(window.is_expanded)
            self.assertEqual(window.size(), QSize(*ISLAND_SIZE_REDUCED))
            self.assertEqual(window._stack.currentIndex(), 0)
        finally:
            window.close()
            window.deleteLater()

    def test_module_size_helper(self):
        self.assertEqual(module_size(None, False), ISLAND_SIZE_REDUCED)
        self.assertEqual(module_size(None, True), ISLAND_SIZE_EXPANDED)
        module = ClockModule()
        self.assertEqual(module_size(module, False), ISLAND_SIZE_REDUCED)
        self.assertEqual(module_size(module, True), ISLAND_SIZE_EXPANDED)

    def test_chemin_ile_symmetrique_autour_du_centre_horizontal(self):
        """T025/T026 : _island_path est un miroir gauche/droite parfait,
        pour la taille reduite, etendue et les tailles intermediaires
        de l'animation."""
        window = self._create_with_clock()
        try:
            pas = 0.5
            # Decalage de la grille d'echantillonnage pour ne jamais tomber
            # exactement sur un bord du tracé (flancs, arrêtes d'arcs),
            # dont QPainterPath.contains traite les points selon la direction
            # du contour.
            decal_x, decal_y = 0.37, 0.21

            def positions(longueur, decal):
                return [
                    decal + i * pas
                    for i in range(__import__("math").ceil((longueur - 2 * decal) / pas))
                ]

            def miroir_x(x, centre_x):
                return 2.0 * centre_x - x

            for largeur, hauteur in (
                ISLAND_SIZE_REDUCED,
                ISLAND_SIZE_EXPANDED,
                (400, 80),
            ):
                with self.subTest(taille=(largeur, hauteur)):
                    rect = QRectF(0, 0, largeur, hauteur)
                    chemin = window._island_path(rect)
                    centre_x = largeur / 2.0

                    # Balayage d'une grille strictement interieure au tracé :
                    # un point et son miroir selon l'axe x = centre_x doivent
                    # etre simultanement dedans ou dehors du tracé.
                    for px in positions(largeur, decal_x):
                        px_miroir = miroir_x(px, centre_x)
                        for py in positions(hauteur, decal_y):
                            self.assertEqual(
                                chemin.contains(QPointF(px, py)),
                                chemin.contains(QPointF(px_miroir, py)),
                                f"asymetrie gauche/droite en ({px}, {py}) "
                                f"pour {largeur}x{hauteur}",
                            )
                    # Flanc gauche net : le remplissage touche exactement x = 0
                    # et ne depasse pas a x < 0 (pas de decalage de pixel).
                    self.assertTrue(chemin.contains(QPointF(0.5, 10.0)))
                    self.assertFalse(chemin.contains(QPointF(-0.5, 10.0)))
        finally:
            window.close()
            window.deleteLater()

    def test_paint_event_definit_conseil_rendu_antialiasing(self):
        """T026 : paintEvent active explicitement l'antialiasing du QPainter."""
        window = self._create_with_clock()
        try:
            appels = []

            class EspionPeintre(QPainter):
                """QPainter espion qui enregistre les appels a setRenderHint."""

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    EspionPeintre.derniere_instance = self

                def setRenderHint(self, hint, on=True):  # noqa: A002
                    appels.append((hint, bool(on)))
                    super().setRenderHint(hint, on)

            EspionPeintre.derniere_instance = None
            appels.clear()

            with mock.patch.object(core_window, "QPainter", EspionPeintre):
                window.paintEvent(QPaintEvent(QRect(window.rect())))

            self.assertIn(
                (QPainter.RenderHint.Antialiasing, True),
                appels,
                "setRenderHint(Antialiasing, True) doit etre appele dans paintEvent",
            )
        finally:
            window.close()
            window.deleteLater()
