"""Fenetre principale Dynamic Island : pilule sans bordure, transparente, toujours au-dessus."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QEasingCurve, QPoint, QRectF, QSize, QVariantAnimation, Qt
from PyQt6.QtGui import QBitmap, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QApplication, QStackedLayout, QVBoxLayout, QWidget

from core.base_module import BaseModule

# Constantes de design (specification T001, decisions D1 et D8).
REDUCED_SIZE = (200, 60)
EXPANDED_SIZE = (400, 160)
ANIMATION_DURATION_MS = 300
PILL_COLOR = QColor(25, 25, 30, 210)


class DynamicIslandWindow(QWidget):
    """Fenetre pilule hebergeant un module via un QStackedLayout (index 0 reduit, 1 etendu)."""

    def __init__(self, module: BaseModule | None = None, parent=None) -> None:
        super().__init__(parent)

        self._module: BaseModule | None = module
        self._expanded = False
        self._reduced_widget: QWidget | None = None
        self._expanded_widget: QWidget | None = None

        # Drapeaux de fenetre : sans bordure, toujours au dessus.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Layout : QVQBoxLayout marges 0 contenant un QStackedLayout.
        self._container = QVBoxLayout(self)
        self._container.setContentsMargins(0, 0, 0, 0)
        self._stack = QStackedLayout()
        self._container.addLayout(self._stack)

        # Animation de la taille fixe de la fenêtre (QSize, 300 ms, InOutQuad).
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_DURATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.valueChanged.connect(self._on_animation_value_changed)
        self._animation.finished.connect(self._on_animation_finished)

        if module is not None:
            self.set_module(module)
        else:
            # Pilule vide par defaut quand aucun module n'est disponible.
            self.setFixedSize(*REDUCED_SIZE)
            self._regenerate_mask()
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
            self.setFixedSize(*REDUCED_SIZE)
            self._regenerate_mask()
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

        width, height = module.get_reduced_size()
        self.setFixedSize(int(width), int(height))
        self._regenerate_mask()
        self._position_on_primary_screen()

    # ------------------------------------------------------------------ etats

    @property
    def is_expanded(self) -> bool:
        """True si la fenetre vise l'etat etendu."""
        return self._expanded

    def expand(self) -> None:
        """Passe a l'etat etendu avec animation."""
        self._stack.setCurrentIndex(1)
        self._animate_to(*module_size(self._module, expanded=True))

    def collapse(self) -> None:
        """Passe a l'etat reduit avec animation."""
        self._stack.setCurrentIndex(0)
        self._animate_to(*module_size(self._module, expanded=False))

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
        y = geometry.top()
        self.move(QPoint(x, y))

    def showEvent(self, event) -> None:  # noqa: ANN001
        super().showEvent(event)
        self._position_on_primary_screen()

    # ------------------------------------------------------------------ animation

    def _animate_to(self, width: int, height: int) -> None:
        """Anime la taille fixe de la fenetre vers la cible donnee."""
        self._animation.stop()
        # Une animation interrompue ne doit pas figer une taille intermediaire :
        # on snap a sa cible avant d'en relancer une nouvelle.
        end_value = self._animation.endValue()
        if isinstance(end_value, QSize) and end_value.isValid():
            self.setFixedSize(end_value.width(), end_value.height())
            self._regenerate_mask()
            self.update()
        self._animation.setStartValue(QSize(self.width(), self.height()))
        self._animation.setEndValue(QSize(int(width), int(height)))
        self._expanded = int(width) != REDUCED_SIZE[0] or int(height) != REDUCED_SIZE[1]
        self._animation.start()

    def _on_animation_value_changed(self, value) -> None:  # noqa: ANN001
        size = QSize(value)
        self.setFixedSize(size.width(), size.height())
        self._regenerate_mask()
        self.update()

    def _on_animation_finished(self) -> None:
        """Garantit la taille exacte a la fin de l'animation."""
        end = QSize(self._animation.endValue())
        self.setFixedSize(end.width(), end.height())
        self._regenerate_mask()
        self.update()

    # ------------------------------------------------------------------ dessin

    def _regenerate_mask(self) -> None:
        """Regenerer le masque QBitmap en pilule a chaque changement de taille."""
        size = self.size()
        bitmap = QBitmap(size)
        bitmap.fill(Qt.GlobalColor.color0)
        painter = QPainter(bitmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        radius = size.height() / 2.0
        path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
        painter.fillPath(path, Qt.GlobalColor.color1)
        painter.end()
        self.setMask(bitmap)

    def paintEvent(self, event) -> None:  # noqa: ANN001
        """Dessine la pilule sombre semi-transparente."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        radius = self.height() / 2.0
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.fillPath(path, PILL_COLOR)

    # ------------------------------------------------------------------ evenements

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: ANN001
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def module_size(module: BaseModule | None, expanded: bool) -> tuple[int, int]:
    """Retourne les dimensions cibles d'un module (ou les valeurs par defaut)."""
    if module is None:
        return EXPANDED_SIZE if expanded else REDUCED_SIZE
    if expanded:
        width, height = module.get_expanded_size()
    else:
        width, height = module.get_reduced_size()
    return int(width), int(height)
