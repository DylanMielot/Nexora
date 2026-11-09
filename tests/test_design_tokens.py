"""Tests des jetons de design core.design.tokens (hors Qt : pas d'affichage requis).

Vérifie la structure figée, les valeurs de la spécification T008 et les
rapports de contraste WCAG AA sur le fond de pilule de chaque thème.
"""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.design.tokens import DesignTokens, dark_tokens, light_tokens  # noqa: E402
from PyQt6.QtCore import QEasingCurve, QSize  # noqa: E402
from PyQt6.QtGui import QColor, QFont  # noqa: E402

_EXPECTED_FIELDS = (
    "pill_background", "pill_background_pressed", "pill_border", "pill_shadow",
    "text_primary", "text_secondary", "text_disabled",
    "icon_primary", "icon_secondary", "accent_primary", "separator",
    "pill_padding_h", "pill_padding_v", "pill_edge_margin", "element_gap",
    "touch_target_min",
    "pill_radius_ratio", "button_radius",
    "pill_radius_top", "pill_radius_bottom",
    "font_family", "font_reduced_primary_pt", "font_reduced_secondary_pt",
    "font_expanded_primary_pt", "font_expanded_secondary_pt",
    "font_weight_primary", "font_weight_secondary",
    "anim_duration_expand_ms", "anim_duration_hover_ms", "anim_duration_pressed_ms",
    "easing_expand",
)

_COLOR_FIELDS = (
    "pill_background", "pill_background_pressed", "pill_border", "pill_shadow",
    "text_primary", "text_secondary", "text_disabled",
    "icon_primary", "icon_secondary", "accent_primary", "separator",
)

# Couleurs de référence pour le compositing du fond de pilule translucide.
_BACKDROP = {"light": QColor("white"), "dark": QColor("black")}


def _relative_luminance(color: QColor) -> float:
    """Luminance relative WCAG d'une couleur sRGB (canal alpha ignoré)."""

    def linear(channel: int) -> float:
        c = channel / 255.0
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    return (
        0.2126 * linear(color.red())
        + 0.7152 * linear(color.green())
        + 0.0722 * linear(color.blue())
    )


def _contrast_ratio(lum_a: float, lum_b: float) -> float:
    """Rapport de contraste WCAG entre deux luminances relatives."""
    light = max(lum_a, lum_b)
    dark = min(lum_a, lum_b)
    return (light + 0.05) / (dark + 0.05)


def _luminance_composited_over(pill: QColor, backdrop: QColor) -> float:
    """Luminance relative du fond de pilule composité sur une couleur d'arrière-plan.

    La luminance relative est linéaire, donc le compositing alpha s'applique
    directement sur les luminances.
    """
    alpha = pill.alpha() / 255.0
    return alpha * _relative_luminance(pill) + (1.0 - alpha) * _relative_luminance(backdrop)


class TestDesignTokens(unittest.TestCase):
    def test_sont_des_dataclasses_figes(self):
        tokens = light_tokens()
        self.assertIsInstance(tokens, DesignTokens)
        with self.assertRaises(FrozenInstanceError):
            tokens.pill_background = QColor("white")  # type: ignore[assignment]

    def test_exposent_tous_les_champs_specifies(self):
        for variant_fn in (light_tokens, dark_tokens):
            tokens = variant_fn()
            for name in _EXPECTED_FIELDS:
                self.assertTrue(hasattr(tokens, name), f"champ manquant : {name}")

    def test_champs_couleurs_sont_des_qcolor(self):
        tokens = light_tokens()
        for name in _COLOR_FIELDS:
            self.assertIsInstance(getattr(tokens, name), QColor, msg=name)

    def test_valeurs_light_conformes_specification(self):
        tokens = light_tokens()
        self.assertEqual(tokens.pill_background, QColor(242, 242, 244, 238))
        self.assertEqual(tokens.pill_background_pressed, QColor(225, 225, 230, 238))
        self.assertEqual(tokens.pill_border, QColor(160, 160, 170, 140))
        self.assertEqual(tokens.pill_shadow, QColor(0, 0, 0, 70))
        self.assertEqual(tokens.text_primary, QColor("#1C1C1E"))
        self.assertEqual(tokens.text_secondary, QColor("#5A5A64"))
        self.assertEqual(tokens.text_disabled, QColor("#8E8E93"))
        self.assertEqual(tokens.icon_primary, QColor("#1C1C1E"))
        self.assertEqual(tokens.icon_secondary, QColor("#5A5A64"))
        self.assertEqual(tokens.accent_primary, QColor("#0078D7"))
        self.assertEqual(tokens.separator, QColor(180, 180, 186, 120))
        # Espacements
        self.assertEqual(tokens.pill_padding_h, 16)
        self.assertEqual(tokens.pill_padding_v, 12)
        self.assertEqual(tokens.pill_edge_margin, 8)
        self.assertEqual(tokens.element_gap, 8)
        self.assertEqual(tokens.touch_target_min, QSize(28, 28))
        # Rayons
        self.assertEqual(tokens.pill_radius_ratio, 0.5)
        self.assertEqual(tokens.button_radius, 8)
        self.assertEqual(tokens.pill_radius_top, 0)
        self.assertEqual(tokens.pill_radius_bottom, 20)
        # Typographie
        self.assertEqual(tokens.font_family, "Segoe UI")
        self.assertEqual(tokens.font_reduced_primary_pt, 20)
        self.assertEqual(tokens.font_reduced_secondary_pt, 10)
        self.assertEqual(tokens.font_expanded_primary_pt, 22)
        self.assertEqual(tokens.font_expanded_secondary_pt, 11)
        self.assertEqual(tokens.font_weight_primary, QFont.Weight.DemiBold)  # 600
        self.assertEqual(tokens.font_weight_secondary, QFont.Weight.Normal)  # 400
        # Animations
        self.assertEqual(tokens.anim_duration_expand_ms, 300)
        self.assertEqual(tokens.anim_duration_hover_ms, 120)
        self.assertEqual(tokens.anim_duration_pressed_ms, 100)
        self.assertEqual(tokens.easing_expand, QEasingCurve.Type.InOutQuad)

    def test_valeurs_dark_conformes_specification(self):
        tokens = dark_tokens()
        self.assertEqual(tokens.pill_background, QColor(15, 15, 15, 250))
        self.assertEqual(tokens.text_primary, QColor("#F5F5F7"))
        self.assertEqual(tokens.accent_primary, QColor("#0A84FF"))
        self.assertEqual(tokens.font_weight_primary, QFont.Weight.DemiBold)
        self.assertEqual(tokens.pill_radius_top, 0)
        self.assertEqual(tokens.pill_radius_bottom, 20)

    def test_variantes_light_et_dark_differentes(self):
        self.assertNotEqual(light_tokens(), dark_tokens())

    def test_espacements_et_rayons_positifs(self):
        for tokens in (light_tokens(), dark_tokens()):
            self.assertGreater(tokens.pill_padding_h, 0)
            self.assertGreater(tokens.pill_padding_v, 0)
            self.assertGreater(tokens.pill_edge_margin, 0)
            self.assertGreater(tokens.element_gap, 0)
            self.assertGreater(tokens.button_radius, 0)
            self.assertGreater(tokens.pill_radius_ratio, 0.0)

    def test_touch_target_min_respecte_plancher_accessibilite(self):
        """Plancher spécifié 28x28 ; 40x44 recommandé pour le confort souris Windows."""
        for tokens in (light_tokens(), dark_tokens()):
            self.assertGreaterEqual(tokens.touch_target_min.width(), 28)
            self.assertGreaterEqual(tokens.touch_target_min.height(), 28)

    def test_contraste_wcag_aa_sur_fond_pilule(self):
        """Texte primaire et secondaire >= 4.5:1 sur la pilule (WCAG AA 1.4.3).

        Le texte désactivé est exclu : texte inactif, exempt de 1.4.3 WCAG.
        Les rapports mesurés figurent dans les messages d'échec.
        """
        for variant, tokens_fn in (("light", light_tokens), ("dark", dark_tokens)):
            tokens = tokens_fn()
            backdrop = _BACKDROP[variant]
            lum_pilule = _luminance_composited_over(tokens.pill_background, backdrop)
            for token_name in ("text_primary", "text_secondary"):
                ratio = _contrast_ratio(
                    _relative_luminance(getattr(tokens, token_name)), lum_pilule
                )
                self.assertGreaterEqual(
                    ratio,
                    4.5,
                    f"{variant}.{token_name}: contraste {ratio:.2f}:1 < 4.5:1 sur fond de pilule",
                )


if __name__ == "__main__":
    unittest.main()
