"""Gestionnaire de theme singleton (Qt) de la Dynamic Island Windows.

Détecte le thème système Windows via la valeur AppsUseLightTheme de
HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize
(1 = clair, 0 = sombre), avec repli sur le thème clair en cas d'échec.

Pas de réglage thème dans l'application (HIG Dark Mode : l'application doit
respecter le réglage système, pas le dupliquer). Le changement à chaud n'est
pas implémenté en T009 : la variante est lue au démarrage uniquement.
"""

from __future__ import annotations

import logging

try:
    import winreg
except ImportError:  # pragma: no cover - plateformes non Windows
    winreg = None  # type: ignore[assignment]

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget

from .tokens import DesignTokens, dark_tokens, light_tokens

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """Singleton : une seule instance par application.

    Signaux:
        theme_changed(str): émis quand la variante active change
            ("light" | "dark").
    """

    theme_changed = pyqtSignal(str)

    _instance: "ThemeManager | None" = None

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._variant: str = self.detect_system_variant()
        self._tokens: dict[str, DesignTokens] = {
            "light": light_tokens(),
            "dark": dark_tokens(),
        }
        logger.info("Theme systeme detecte : %s", self._variant)

    @classmethod
    def instance(cls, parent=None) -> "ThemeManager":
        """Retourne l'instance unique, en la créant à la demande.

        Le premier parent fourni est utilisé ; les appels suivants ignorent
        le parent (comportement singleton).
        """
        if cls._instance is None:
            if parent is None:
                parent = QApplication.instance()
            cls._instance = cls(parent)
        return cls._instance

    @staticmethod
    def detect_system_variant() -> str:
        """Détecte la variante système Windows via le registre.

        Lit AppsUseLightTheme (1 = clair, 0 = sombre). Repli sur "light"
        si le registre est indisponible (plateforme non Windows, clé
        absente, erreur d'accès).
        """
        if winreg is None:
            return "light"
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            try:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value == 1 else "dark"
            finally:
                winreg.CloseKey(key)
        except OSError:
            return "light"

    # ------------------------------------------------------------------ API

    def variant(self) -> str:
        """Variante active : "light" ou "dark"."""
        return self._variant

    def tokens(self) -> DesignTokens:
        """Jetons de design de la variante active."""
        return self._tokens[self._variant]

    def apply_to_window(self, window) -> None:
        """Applique le thème actif à une fenêtre pilule (bordure).

        Hook temporaire T009 : une feuille de style best-effort est appliquée
        sans toucher au comportement existant de la fenêtre. Le dessin de la
        pilule (paintEvent) passera directement par les jetons dans le cadre
        de T010.
        """
        if window is None:
            return
        tokens = self.tokens()
        try:
            window.setStyleSheet(
                "DynamicIslandWindow {"
                "background-color: transparent;"
                f"border: 1px solid {tokens.pill_border.name(QColor.NameFormat.HexArgb)};"
                "}"
            )
        except Exception:  # pragma: no cover - défensif, la fenêtre ne doit pas planter
            logger.exception("Échec de l'application du thème à la fenêtre")

    def apply_to_module(self, module) -> None:
        """Propage la police du thème aux widgets d'un module (hook optionnel).

        Les modules restent propriétaires de leurs widgets ; seule la famille
        de police est appliquée ici, les tailles de police définies par le
        module sont préservées. À étendre dans T010+.
        """
        if module is None:
            return
        font = QFont(self.tokens().font_family)
        widgets: list[QWidget] = [module] if isinstance(module, QWidget) else []
        widgets.extend(module.findChildren(QWidget))  # type: ignore[arg-type]
        for widget in widgets:
            try:
                widget.setFont(font)
            except Exception:  # pragma: no cover - défensif par widget
                pass
