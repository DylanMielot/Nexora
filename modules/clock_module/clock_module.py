"""Module de démonstration « Horloge » pour le Core Dynamic Island.

Affiche l'heure courante dans deux modes :

* réduit : ``HH:MM`` sur un QLabel centré avec une grande police ;
* étendu : ``HH:MM:SS`` suivi de la date complète en français
  (exemple : ``Lundi 9 Novembre 2026``).

Un QTimer rafraîchit l'affichage chaque seconde. Les widgets renvoyés par
``get_reduced_widget()`` et ``get_expanded_widget()`` appartiennent au module
(qui en conserve la propriété et le cycle de vie).
"""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.base_module import BaseModule


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


class ClockModule(BaseModule):
    """Horloge : implémentation du contrat BaseModule pour la démonstration."""

    module_id = "clock"
    display_name = "Horloge"

    _REDUCED_SIZE = (200, 60)
    _EXPANDED_SIZE = (400, 160)

    def __init__(self) -> None:
        super().__init__()

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
        """Arrête le timer avant que le Core retire le module."""
        self._timer.stop()

    # -- Fabrication des widgets ------------------------------------------

    def _create_reduced_widget(self) -> QLabel:
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setPointSize(28)
        label.setFont(font)
        # Le module reste propriétaire du widget ; on arrête le timer si le
        # widget est détruit avant le module.
        label.destroyed.connect(self._timer.stop)
        return label

    def _create_expanded_widget(self) -> QLabel:
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setPointSize(22)
        label.setFont(font)
        label.destroyed.connect(self._timer.stop)
        return label

    # -- Mise à jour de l'affichage ---------------------------------------

    def _refresh(self) -> None:
        now = datetime.now()
        self._reduced_widget.setText(now.strftime("%H:%M"))
        self._expanded_widget.setText(
            f"{now.strftime('%H:%M:%S')}\n{_french_date_string(now)}"
        )


def _french_date_string(now: datetime) -> str:
    """Date complète en français : « Lundi 9 Novembre 2026 »."""
    day_name = _FRENCH_DAYS[now.weekday()]  # lundi = 0
    month_name = _FRENCH_MONTHS[now.month - 1]
    return f"{day_name} {now.day} {month_name} {now.year}"
