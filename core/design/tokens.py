"""Jetons de design figes (DesignTokens) de la Dynamic Island Windows.

Tous les noms sont sémantiques : aucun composant ne doit contenir de valeur
de couleur brute en dur. Deux variantes sont fabriquees par light_tokens()
et dark_tokens().

Les valeurs ci-dessous sont les valeurs indicatives de la specification
T008, à valider par mesure de contraste (voir tests/test_design_tokens.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QEasingCurve, QSize
from PyQt6.QtGui import QColor, QFont


@dataclass(frozen=True)
class DesignTokens:
    """Jetons de design figes, valeurs logiques (pixels logiques, points, ms).

    Une instance est considérée comme immuable : ne pas muter les QColor
    ou QSize qu'elle contient après sa création.
    """

    # --- Couleurs (QColor) : variantes light / dark ---------------------
    pill_background: QColor
    pill_background_pressed: QColor
    pill_border: QColor
    pill_shadow: QColor
    text_primary: QColor
    text_secondary: QColor
    text_disabled: QColor
    icon_primary: QColor
    icon_secondary: QColor
    accent_primary: QColor
    separator: QColor

    # --- Espacements (pixels logiques) ----------------------------------
    pill_padding_h: int
    pill_padding_v: int
    pill_edge_margin: int
    element_gap: int
    touch_target_min: QSize

    # --- Rayons (pixels logiques / ratio) -------------------------------
    pill_radius_ratio: float
    button_radius: int

    # --- Typographie ----------------------------------------------------
    font_family: str
    font_reduced_primary_pt: float
    font_reduced_secondary_pt: float
    font_expanded_primary_pt: float
    font_expanded_secondary_pt: float
    font_weight_primary: QFont.Weight
    font_weight_secondary: QFont.Weight

    # --- Animations (ms) ------------------------------------------------
    anim_duration_expand_ms: int
    anim_duration_hover_ms: int
    anim_duration_pressed_ms: int
    easing_expand: QEasingCurve.Type


def light_tokens() -> DesignTokens:
    """Jetons du theme clair (variante systeme par defaut)."""
    return DesignTokens(
        # Couleurs
        pill_background=QColor(242, 242, 244, 238),
        pill_background_pressed=QColor(225, 225, 230, 238),
        pill_border=QColor(160, 160, 170, 140),
        pill_shadow=QColor(0, 0, 0, 70),
        text_primary=QColor("#1C1C1E"),
        text_secondary=QColor("#5A5A64"),
        text_disabled=QColor("#8E8E93"),
        icon_primary=QColor("#1C1C1E"),
        icon_secondary=QColor("#5A5A64"),
        accent_primary=QColor("#0078D7"),
        separator=QColor(180, 180, 186, 120),
        # Espacements
        pill_padding_h=16,
        pill_padding_v=12,
        pill_edge_margin=8,
        element_gap=8,
        touch_target_min=QSize(28, 28),
        # Rayons
        pill_radius_ratio=0.5,
        button_radius=8,
        # Typographie
        font_family="Segoe UI",
        font_reduced_primary_pt=20,
        font_reduced_secondary_pt=10,
        font_expanded_primary_pt=22,
        font_expanded_secondary_pt=11,
        font_weight_primary=QFont.Weight.DemiBold,  # 600 == CSS "semibold" (Qt n'a pas de Semibold)
        font_weight_secondary=QFont.Weight.Normal,  # 400 == CSS "regular"
        # Animations
        anim_duration_expand_ms=300,
        anim_duration_hover_ms=120,
        anim_duration_pressed_ms=100,
        easing_expand=QEasingCurve.Type.InOutQuad,
    )


def dark_tokens() -> DesignTokens:
    """Jetons du theme sombre."""
    return DesignTokens(
        # Couleurs
        pill_background=QColor(25, 25, 30, 210),
        pill_background_pressed=QColor(45, 45, 50, 210),
        pill_border=QColor(90, 90, 100, 160),
        pill_shadow=QColor(0, 0, 0, 130),
        text_primary=QColor("#F5F5F7"),
        text_secondary=QColor("#AEAEB4"),
        text_disabled=QColor("#6E6E73"),
        icon_primary=QColor("#F5F5F7"),
        icon_secondary=QColor("#AEAEB4"),
        accent_primary=QColor("#0A84FF"),
        separator=QColor(90, 90, 100, 140),
        # Espacements
        pill_padding_h=16,
        pill_padding_v=12,
        pill_edge_margin=8,
        element_gap=8,
        touch_target_min=QSize(28, 28),
        # Rayons
        pill_radius_ratio=0.5,
        button_radius=8,
        # Typographie
        font_family="Segoe UI",
        font_reduced_primary_pt=20,
        font_reduced_secondary_pt=10,
        font_expanded_primary_pt=22,
        font_expanded_secondary_pt=11,
        font_weight_primary=QFont.Weight.DemiBold,
        font_weight_secondary=QFont.Weight.Normal,
        # Animations
        anim_duration_expand_ms=300,
        anim_duration_hover_ms=120,
        anim_duration_pressed_ms=100,
        easing_expand=QEasingCurve.Type.InOutQuad,
    )
