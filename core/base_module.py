"""Contrat abstrait que tout module Dynamic Island doit respecter."""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

from PyQt6.QtWidgets import QWidget

# PyQt6 : QWidget utilise la metaclass sip, incompatible avec ABCMeta.
# On en combine les deux pour garder la signature "BaseModule(QWidget, ABC)"
# tout en rendant les methodes abstraites effectives.
_ModuleMeta = type("_ModuleMeta", (type(QWidget), ABCMeta), {})


class BaseModule(QWidget, ABC, metaclass=_ModuleMeta):
    """Base abstraite pour les modules de la Dynamic Island.

    Les widgets retournes par get_reduced_widget / get_expanded_widget sont
    possedes par le module ; la fenetre les reparente dans son QStackedLayout.
    """

    module_id: str = "base_module"
    display_name: str = "Module de base"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    @abstractmethod
    def get_reduced_widget(self) -> QWidget:
        """Retourne le widget affiche dans l'etat reduit (200 x 60 par defaut)."""

    @abstractmethod
    def get_expanded_widget(self) -> QWidget:
        """Retourne le widget affiche dans l'etat etendu (400 x 160 par defaut)."""

    @abstractmethod
    def get_reduced_size(self) -> tuple[int, int]:
        """Retourne (largeur, hauteur) de l'etat reduit."""

    @abstractmethod
    def get_expanded_size(self) -> tuple[int, int]:
        """Retourne (largeur, hauteur) de l'etat etendu."""

    @abstractmethod
    def on_click(self) -> None:
        """Action declenchee par un clic sur la pilule, avant la bascule."""
