"""Module de démonstration « Horloge » pour le Core Dynamic Island.

Affiche l'heure courante dans deux modes :

* réduit : ``HH:MM`` (texte primaire des jetons) ;
* étendu : ``HH:MM:SS`` suivi de la date complète en français
  (exemple : ``Lundi 9 Novembre 2026``), heure en texte primaire et date en
  texte secondaire des jetons.

Un QTimer rafraîchit l'affichage chaque seconde. Les widgets renvoyés par
``get_reduced_widget()`` et ``get_expanded_widget()`` appartiennent au module
(qui en conserve la propriété et le cycle de vie).

Les polices, tailles, graisses et couleurs proviennent des jetons de design
(:class:`core.design.DesignTokens`) du thème système actif. Si le thème
change à l'exécution, le signal :signal:`ThemeManager.theme_changed` déclenche
le rafraîchissement des couleurs des widgets.
"""

from __future__ import annotations

from datetime import datetime
from html import escape

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QLabel, QWidget

from core.base_module import BaseModule
from core.design import DesignTokens, ThemeManager

# Noms français des jours et des mois. Pas d'appel à locale.setlocale : pas
# d'effet de bord global et un résultat identique sur toutes les plateformes.
_FRENCH_DAYS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
_FRENCH_MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


class _ClockLabel(QLabel):
    """QLabel bi-segmente (primaire / secondaire) thématisé par les jetons.

    Le rendu utilise du HTML riche pour appliquer à chaque segment sa police,
    sa taille, sa graisse et sa couleur issues des jetons de design.
    ``text()`` retourne le texte brut ("primaire\\nsecondaire") afin que le
    contenu affiché reste accessible en l'état, sans balisage.
    """

    def __init__(
        self,
        tokens: DesignTokens,
        primary_pt: float,
        primary_weight: QFont.Weight,
        secondary_pt: float,
        secondary_weight: QFont.Weight,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._primary_pt = primary_pt
        self._primary_weight = primary_weight
        self._secondary_pt = secondary_pt
        self._secondary_weight = secondary_weight
        self._primary_text = ""
        self._secondary_text = ""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("")

    # -- Texte brut ----------------------------------------------------------

    def text(self) -> str:
        """Texte brut affiché : primaire, puis secondaire sur une nouvelle ligne."""
        if self._secondary_text:
            return f"{self._primary_text}\n{self._secondary_text}"
        return self._primary_text

    # -- Contenu et thème -----------------------------------------------------

    def set_content(self, primary_text: str, secondary_text: str = "") -> None:
        """Définit le contenu affiché et le re-rend avec les jetons courants."""
        self._primary_text = primary_text
        self._secondary_text = secondary_text
        self._render()

    def set_tokens(self, tokens: DesignTokens) -> None:
        """Recharge les jetons (appelé au changement de thème système)."""
        self._tokens = tokens
        self._render()

    def _render(self) -> None:
        """Construit le HTML riche à partir du texte brut et des jetons."""
        tokens = self._tokens
        blocks = [
            self._span(
                self._primary_text,
                tokens.font_family,
                self._primary_pt,
                self._primary_weight,
                tokens.text_primary,
            )
        ]
        if self._secondary_text:
            blocks.append(
                self._span(
                    self._secondary_text,
                    tokens.font_family,
                    self._secondary_pt,
                    self._secondary_weight,
                    tokens.text_secondary,
                )
            )
        super().setText("<br>".join(blocks))

    @staticmethod
    def _span(
        text: str,
        family: str,
        size_pt: float,
        weight: QFont.Weight,
        color: QColor,
    ) -> str:
        return (
            f"<span style=\"font-family:'{escape(family)}'; "
            f"font-size:{size_pt}pt; font-weight:{int(weight)}; "
            f"color:{color.name(QColor.NameFormat.HexRgb)};\">{escape(text)}</span>"
        )


class ClockModule(BaseModule):
    """Horloge : implémentation du contrat BaseModule pour la démonstration."""

    module_id = "clock"
    display_name = "Horloge"

    _REDUCED_SIZE = (200, 40)
    _EXPANDED_SIZE = (600, 120)

    def __init__(self) -> None:
        super().__init__()

        self._theme_manager = ThemeManager.instance()
        self._tokens: DesignTokens = self._theme_manager.tokens()
        self._theme_manager.theme_changed.connect(self._on_theme_changed)

        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)

        self._reduced_widget = self._create_reduced_widget()
        self._expanded_widget = self._create_expanded_widget()

        self._refresh()
        self._timer.start(1000)

    # -- Contrat BaseModule (cinq méthodes abstraites) --------------------

    def get_reduced_size(self) -> tuple[int, int]:
        return self._REDUCED_SIZE

    def get_expanded_size(self) -> tuple[int, int]:
        return self._EXPANDED_SIZE

    def get_reduced_widget(self) -> QWidget:
        return self._reduced_widget

    def get_expanded_widget(self) -> QWidget:
        return self._expanded_widget

    def on_click(self) -> None:
        """Comportement démo : rafraîchit immédiatement l'affichage."""
        self._refresh()

    def cleanup(self) -> None:
        """Arrête le timer et se désabonne du thème avant le retrait du module."""
        try:
            self._theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except (TypeError, RuntimeError):
            # Pas de connexion active (déjà nettoyé) ou objet C++ détruit :
            # rien de plus à faire.
            pass
        self._timer.stop()

    # -- Fabrication des widgets ------------------------------------------

    def _create_reduced_widget(self) -> _ClockLabel:
        tokens = self._tokens
        label = _ClockLabel(
            tokens,
            tokens.font_reduced_primary_pt,
            tokens.font_weight_primary,
            tokens.font_reduced_secondary_pt,
            tokens.font_weight_secondary,
        )
        # Le module reste propriétaire du widget ; on arrête le timer si le
        # widget est détruit avant le module.
        label.destroyed.connect(self._timer.stop)
        return label

    def _create_expanded_widget(self) -> _ClockLabel:
        tokens = self._tokens
        label = _ClockLabel(
            tokens,
            tokens.font_expanded_primary_pt,
            tokens.font_weight_primary,
            tokens.font_expanded_secondary_pt,
            tokens.font_weight_secondary,
        )
        label.destroyed.connect(self._timer.stop)
        return label

    # -- Mise à jour de l'affichage ---------------------------------------

    def _refresh(self) -> None:
        now = datetime.now()
        self._reduced_widget.set_content(now.strftime("%H:%M"))
        self._expanded_widget.set_content(
            now.strftime("%H:%M:%S"), _french_date_string(now)
        )

    def _on_theme_changed(self, variant: str) -> None:  # noqa: ARG002
        """Recharge les jetons de la nouvelle variante et rafraîchit les couleurs."""
        self._tokens = self._theme_manager.tokens()
        self._reduced_widget.set_tokens(self._tokens)
        self._expanded_widget.set_tokens(self._tokens)


def _french_date_string(now: datetime) -> str:
    """Date complète en français : « Lundi 9 Novembre 2026 »."""
    day_name = _FRENCH_DAYS[now.weekday()]  # lundi = 0
    month_name = _FRENCH_MONTHS[now.month - 1]
    return f"{day_name} {now.day} {month_name} {now.year}"
