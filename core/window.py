"""Fenetre principale Dynamic Island : pilule sans bordure, transparente, toujours au-dessus."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QEasingCurve, QEvent, QPoint, QRectF, QSize, QVariantAnimation, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QApplication, QStackedLayout, QVBoxLayout, QWidget

from core.base_module import BaseModule
from core.design import DesignTokens, ThemeManager

# Constantes de design (specification T001, decisions D1 et D8).
# Geometrie de l'ile : reduction (200x40) <-> etendue (600x120).
ISLAND_SIZE_REDUCED = (200, 40)
ISLAND_SIZE_EXPANDED = (600, 120)
ANIMATION_DURATION_MS = 300

# Marge de securite invisible au-dessus de l'ile (hors zone visible de l'ecran).
# La fenetre est placee virtuellement a Y = geometry.top() - 20 avec une
# hauteur de ile + 20 : seul le corps de l'ile (de fenetre Y=20 a Y=20+hauteur
# de l'ile) est visible, les 20 px superieurs etant hors ecran. Le contact haut
# visible de la pilule se situe donc a fenetre Y=20 (ecran Y=0), ce qui permet a
# la courbe de Bézier du sommet de s'eventer progressivement dans la zone
# hors-ecran (fenetre Y < 20) sans etre tronquee, et de fondre avec une
# tangente verticale au contact haut visible (ecran Y=0) :
# plus d'angle droit a 90 degres ni de ligne grise parasite au sommet.
ISLAND_TOP_PAD_PX = 20

# Debord de la courbe de Bézier superieure dans la zone hors-ecran.
# Valeur retenue : 4.0 (guidage T033 : 4.0-6.0). Le sommet de la courbe
# remonte de 4 px au-dessus du contact (fenetre Y = 16, ecran Y = -4), entierement
# dans la zone invisible de 20 px. Avec P0.x==P1.x et P2.x==P3.x, la tangente
# reste parfaitement verticale aux deux contacts hauts pour toute valeur de flare.
ISLAND_TOP_FLARE_PX = 4.0


class DynamicIslandWindow(QWidget):
    """Fenetre pilule hebergeant un module via un QStackedLayout (index 0 reduit, 1 etendu).

    Les couleurs de la pilule proviennent des jetons de design de la variante
    active de ThemeManager (pill_background, pill_border, pill_shadow).
    Les etats interactifs (survol, pression) modifient le fond de la pilule :
    pill_background_pressed pour l'etat presse, une variante plus claire de
    pill_background pour le survol.
    """

    def __init__(self, module: BaseModule | None = None, parent=None) -> None:
        super().__init__(parent)

        self._module: BaseModule | None = module
        self._expanded = False
        self._reduced_widget: QWidget | None = None
        self._expanded_widget: QWidget | None = None

        # Etats interactifs de la pilule.
        self._hovered = False
        self._pressed = False

        # Jeton de design du theme systeme actif.
        self._theme_manager = ThemeManager.instance()
        self._tokens: DesignTokens = self._theme_manager.tokens()
        self._theme_manager.theme_changed.connect(self._on_theme_changed)

        # Drapeaux de fenetre : sans bordure, toujours au dessus.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Layout : QVBoxLayout contenant un QStackedLayout. Marge superieure
        # de ISLAND_TOP_PAD_PX pour compenser le decalage hors-ecran de la
        # fenetre : les widgets enfants restent centres sur la partie visible.
        self._container = QVBoxLayout(self)
        self._container.setContentsMargins(0, ISLAND_TOP_PAD_PX, 0, 0)
        self._stack = QStackedLayout()
        self._container.addLayout(self._stack)

        # Animation de la taille fixe de la fenetre (QSize, 300 ms, InOutQuad).
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_DURATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.valueChanged.connect(self._on_animation_value_changed)
        self._animation.finished.connect(self._on_animation_finished)

        if module is not None:
            self.set_module(module)
        else:
            # Pilule vide par defaut quand aucun module n'est disponible.
            self.setFixedSize(
                ISLAND_SIZE_REDUCED[0], ISLAND_SIZE_REDUCED[1] + ISLAND_TOP_PAD_PX
            )
            self.update()
        self._position_on_primary_screen()

    # ------------------------------------------------------------------ module

    def set_module(self, module: BaseModule | None) -> None:
        """Installe un module : ses widgets sont reparentes dans la pile."""
        # Nettoyage du module sortant : pas de fenetre orpheline et
        # cleanup() appele s'il existe (ex: arret d'un QTimer).
        outgoing = self._module
        if outgoing is not None:
            cleanup = getattr(outgoing, "cleanup", None)
            if callable(cleanup):
                try:
                    cleanup()
                except Exception:  # un module ne doit pas casser la fenetre
                    logger = logging.getLogger(__name__)
                    logger.exception("Erreur dans module.cleanup()")

            while self._stack.count() > 0:
                widget = self._stack.widget(0)
                if widget is not None:
                    self._stack.removeWidget(widget)
                    widget.hide()
                    widget.deleteLater()

        self._module = module
        self._expanded = False
        self._reduced_widget = None
        self._expanded_widget = None

        if module is None:
            self.setFixedSize(
                ISLAND_SIZE_REDUCED[0], ISLAND_SIZE_REDUCED[1] + ISLAND_TOP_PAD_PX
            )
            self.update()
            self._position_on_primary_screen()
            return

        reduced = module.get_reduced_widget()
        expanded = module.get_expanded_widget()
        reduced.setParent(self)
        expanded.setParent(self)

        self._stack.addWidget(reduced)  # index 0 : reduit
        self._stack.addWidget(expanded)  # index 1 : etendu
        self._stack.setCurrentIndex(0)

        self._reduced_widget = reduced
        self._expanded_widget = expanded

        # Filtre d'evenements sur les widgets enfants : un clic n'importe ou
        # sur la pilule (y compris sur un enfant) doit basculer l'etat de la
        # fenetre plutot que d'etre avale par le widget cible.
        self._install_child_event_filter(reduced)
        self._install_child_event_filter(expanded)

        width, height = module.get_reduced_size()
        self.setFixedSize(int(width), int(height) + ISLAND_TOP_PAD_PX)
        self.update()
        self._position_on_primary_screen()

    def _install_child_event_filter(self, widget: QWidget | None) -> None:
        """Pose le filtre d'evenements de la fenetre sur un widget et ses descendants."""
        if widget is None:
            return
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    # ------------------------------------------------------------------ etats

    @property
    def is_expanded(self) -> bool:
        """True si la fenetre vise l'etat etendu."""
        return self._expanded

    def expand(self) -> None:
        """Passe a l'etat etendu avec animation.

        Sans module installe, rien a etendre : on sort silencieusement.
        L'etat etendu cache le widget reduit (.hide()).
        """
        if self._module is None:
            return
        self._stack.setCurrentIndex(1)
        if self._reduced_widget is not None:
            self._reduced_widget.hide()
        self._animate_to(
            ISLAND_SIZE_EXPANDED[0], ISLAND_SIZE_EXPANDED[1] + ISLAND_TOP_PAD_PX
        )

    def collapse(self) -> None:
        """Passe a l'etat reduit avec animation.

        Sans module installe, rien a reduire : on sort silencieusement.
        L'etat reduit cache le widget etendu (.hide()).
        """
        if self._module is None:
            return
        self._stack.setCurrentIndex(0)
        if self._expanded_widget is not None:
            self._expanded_widget.hide()
        self._animate_to(
            ISLAND_SIZE_REDUCED[0], ISLAND_SIZE_REDUCED[1] + ISLAND_TOP_PAD_PX
        )

    def toggle(self) -> None:
        """Bascule reduit/etendu : on_click du module puis animation."""
        if self._module is None:
            return
        on_click = getattr(self._module, "on_click", None)
        if callable(on_click):
            try:
                on_click()
            except Exception:  # un module ne doit pas casser la fenetre
                logger = logging.getLogger(__name__)
                logger.exception("Erreur dans module.on_click()")
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    # ------------------------------------------------------------------ position

    def _position_on_primary_screen(self) -> None:
        """Centre horizontal sur l'ecran principal, bord superieur en haut."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        width = self.width()
        height = self.height()
        x = geometry.x() + (geometry.width() - width) // 2
        y = geometry.top() - ISLAND_TOP_PAD_PX
        self.move(QPoint(x, y))

    def showEvent(self, event) -> None:  # noqa: ANN001
        super().showEvent(event)
        self._position_on_primary_screen()

    # ------------------------------------------------------------------ theme

    def _on_theme_changed(self, variant: str) -> None:  # noqa: ARG002
        """Recharge les jetons de la nouvelle variante et redessine."""
        self._tokens = self._theme_manager.tokens()
        self.update()

    # ------------------------------------------------------------------ animation

    def _set_module_content_visible(self, visible: bool) -> None:
        """Montre ou masque le widget du module actif pendant l'animation.

        Le contenu (texte HTML riche du module Horloge, etc.) ne doit etre
        affiché ni recalcule pendant la transition de taille : cela evite les
        scintillements et deformations a chaque frame. Il est affiche une
        seule fois, une fois la taille finale stable.
        """
        widget = self._expanded_widget if self._expanded else self._reduced_widget
        if widget is not None:
            widget.setVisible(visible)

    def _animate_to(self, width: int, height: int) -> None:
        """Anime la taille fixe de la fenetre vers la cible donnee."""
        self._animation.stop()
        # Une animation interrompue ne doit pas figer une taille intermediaire :
        # on snap a sa cible avant d'en relancer une nouvelle.
        end_value = self._animation.endValue()
        if isinstance(end_value, QSize) and end_value.isValid():
            self.setFixedSize(end_value.width(), end_value.height())
            self.update()
        self._animation.setStartValue(QSize(self.width(), self.height()))
        self._animation.setEndValue(QSize(int(width), int(height)))
        # Les cibles passees incluent la marge ISLAND_TOP_PAD_PX sur la hauteur.
        self._expanded = (
            int(width) != ISLAND_SIZE_REDUCED[0]
            or int(height) != ISLAND_SIZE_REDUCED[1] + ISLAND_TOP_PAD_PX
        )
        # Masque le contenu du module pour toute la transition afin d'eviter
        # tout calcul de layout / re-rendu de texte a chaque frame.
        self._set_module_content_visible(False)
        self._animation.start()

    def _on_animation_value_changed(self, value) -> None:  # noqa: ANN001
        size = QSize(value)
        self.setFixedSize(size.width(), size.height())
        self._recenter_horizontally()
        self.update()

    def _recenter_horizontally(self) -> None:
        """Recentre horizontalement sur l'ecran principal, position Y inchangee.

        Appele a chaque frame de l'animation de taille pour contrer le
        derapage vers la droite cause par l'agrandissement depuis le coin
        superieur-gauche. La formule reprend celle de
        _position_on_primary_screen :
        X = (Largeur_ecran - Largeur_actuelle_island) // 2.
        """
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2
        self.move(QPoint(x, self.y()))

    def _on_animation_finished(self) -> None:
        """Garantit la taille exacte a la fin de l'animation."""
        end = QSize(self._animation.endValue())
        self.setFixedSize(end.width(), end.height())
        self.update()
        # La taille est stable : affiche le contenu du module pour l'etat
        # final, sans risque d'artefact visuel pendant la transition.
        self._set_module_content_visible(True)

    # ------------------------------------------------------------------ dessin

    def _island_path(self, rect: QRectF) -> QPainterPath:
        """Chemin de forme de l'ile avec padding invisible au-dessus.

        La fenetre deborde de ISLAND_TOP_PAD_PX px au-dessus de la zone
        visible de l'ecran : le contact haut visible de la pilule se situe a
        fenetre Y = pad (ecran Y = 0). Le sommet n'est plus une ligne droite
        aux limites de la fenetre :

        * contact haut gauche (x, y + pad) et contact haut droit
          (x + w, y + pad) ;
        * entre les deux, une courbe de Bézier cubique (cubicTo) symetrique
          remonte dans la zone hors-ecran (fenetre Y < pad) avant de
          redescendre, avec une tangente verticale a chaque contact, pour
          fondre le flanc vertical dans le sommet sans angle ;
        * flancs verticaux nets et coins bas largement arrondis
          (rayon pill_radius_bottom, clampés) conserves en dessous de Y=pad.

        Le tracé est continu et fermé (closeSubpath).
        """
        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()
        pad = ISLAND_TOP_PAD_PX
        flare = ISLAND_TOP_FLARE_PX
        top_contact_y = y + pad
        rb = min(self._tokens.pill_radius_bottom, w / 2.0, h / 2.0)

        path = QPainterPath()
        # Contact haut gauche (fenêtre Y=pad, écran Y=0) : tangente verticale.
        path.moveTo(x, top_contact_y)
        # Courbe de Bézier cubique symétrique : elle s'evente dans la zone
        # hors-ecran (fenêtre Y < pad) entre les deux contacts hauts avec une
        # tangente verticale a chaque contact, puis redescend au contact droit.
        path.cubicTo(
            x, top_contact_y - flare,
            x + w, top_contact_y - flare,
            x + w, top_contact_y,
        )
        # Flanc droit vertical, net, jusqu'à la base du coin bas droit.
        path.lineTo(x + w, y + h - rb)
        # Coin bas droit arrondi (rayon pill_radius_bottom).
        path.arcTo(
            QRectF(x + w - 2 * rb, y + h - 2 * rb, 2 * rb, 2 * rb),
            0.0,
            -90.0,
        )
        # Fond.
        path.lineTo(x + rb, y + h)
        # Coin bas gauche arrondi (rayon pill_radius_bottom).
        path.arcTo(
            QRectF(x, y + h - 2 * rb, 2 * rb, 2 * rb),
            270.0,
            -90.0,
        )
        # Flanc gauche vertical, net, jusqu'au contact haut gauche.
        path.lineTo(x, top_contact_y)
        path.closeSubpath()
        return path

    def _pill_background_color(self) -> QColor:
        """Couleur de fond de la pilule selon l'etat interactif courant."""
        if self._pressed:
            return self._tokens.pill_background_pressed
        if self._hovered:
            return self._lighter_variant(self._tokens.pill_background)
        return self._tokens.pill_background

    @staticmethod
    def _lighter_variant(color: QColor, factor: float = 0.30) -> QColor:
        """Variante plus claire d'une couleur (melange avec le blanc)."""
        return QColor(
            min(255, int(color.red() + (255 - color.red()) * factor)),
            min(255, int(color.green() + (255 - color.green()) * factor)),
            min(255, int(color.blue() + (255 - color.blue()) * factor)),
            color.alpha(),
        )

    def paintEvent(self, event) -> None:  # noqa: ANN001
        """Dessine la pilule themee : fond, bordure et ombre interieure.

        L'antialiasing est explicite : sans masque QBitmap, le tracé vectoriel
        est regénéré à chaque paintEvent et bénéficie du rendu adouci.
        La bordure est centrée sur le tracé par QPen ; on trace donc un chemin
        intérieur décalé de la moitié de l'épaisseur du pinceau afin que le
        bord extérieur du trait coïncide exactement avec le contour du chemin
        (aucun demi-pixel rogné sur la limite x=0 / y=0).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())

        path = self._island_path(rect)

        # Fond du conteneur selon l'etat interactif (survol / pression).
        painter.fillPath(path, self._pill_background_color())

        # Bordure du conteneur, compensée d'un demi-trait vers l'intérieur.
        pen = QPen(self._tokens.pill_border)
        pen_width = pen.widthF() if pen.widthF() > 0.0 else 1.0
        inset = pen_width / 2.0
        border_path = self._island_path(rect.adjusted(inset, inset, -inset, -inset))
        painter.strokePath(border_path, pen)

        # Ombre interieure discrete en bas a droite (relief du conteneur).
        shadow_path = self._island_path(rect.adjusted(2, 2, 0, 0))
        shadow_pen = QPen(self._tokens.pill_shadow)
        painter.strokePath(shadow_path, shadow_pen)

    # ------------------------------------------------------------------ evenements

    def enterEvent(self, event) -> None:  # noqa: ANN001
        self._hovered = True
        self.update()
        self.expand()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: ANN001
        self._hovered = False
        self.update()
        self.collapse()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def eventFilter(self, watched, event) -> bool:  # noqa: ANN001
        """Intercepte les evenements souris des widgets enfants.

        Le declenchement de l'etendue reposant desormais sur le survol,
        un clic sur un enfant ne bascule plus l'etat de la fenetre ; le
        filtre intercepte toujours l'evenement pour qu'un enfant ne l'avale
        pas et que la fenetre conserve la main sur ses etats survol/pression.
        """
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseButtonDblClick,
        ) and event.button() == Qt.MouseButton.LeftButton:
            if event.type() == QEvent.Type.MouseButtonPress:
                self._pressed = True
                self.update()
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._pressed = False
                self.update()
            return True  # l'enfant n'avale pas l'interaction de la fenetre
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event) -> None:  # noqa: ANN001
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def module_size(module: BaseModule | None, expanded: bool) -> tuple[int, int]:
    """Retourne les dimensions cibles d'un module (ou les valeurs par defaut)."""
    if module is None:
        return ISLAND_SIZE_EXPANDED if expanded else ISLAND_SIZE_REDUCED
    if expanded:
        width, height = module.get_expanded_size()
    else:
        width, height = module.get_reduced_size()
    return int(width), int(height)
