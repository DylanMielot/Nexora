"""Tests de contraste WCAG sur les couleurs de la pilule (T012).

Etend la couverture de tests/test_design_tokens.py :
- texte primaire et secondaire >= 4.5:1 sur le fond de pilule composité,
  themes light et dark (WCAG AA 1.4.3) ;
- idem sur le fond de pilule etat presse (pill_background_pressed), puisque
  ce fond est effectivement utilise au survol/clic de la pilule ;
- texte desactive : taux mesures et documentes uniquement (texte inactif,
  exempte de WCAG 1.4.3 : aucun seuil n'est exige ici).

Aucun affichage necessite (pas de QApplication).
"""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.design.tokens import dark_tokens, light_tokens  # noqa: E402
from PyQt6.QtGui import QColor  # noqa: E402

_VARIANTS = (("light", light_tokens), ("dark", dark_tokens))
_BACKDROP = {"light": QColor("white"), "dark": QColor("black")}
_TEXT_TOKENS = ("text_primary", "text_secondary", "icon_primary", "icon_secondary")
_WCAG_AA = 4.5


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
    """Luminance relative d'un fond de pilule composité sur une couleur d'arrière-plan."""

    alpha = pill.alpha() / 255.0
    return alpha * _relative_luminance(pill) + (1.0 - alpha) * _relative_luminance(backdrop)


class TestWCAGContrast(unittest.TestCase):
    def _ratio(self, variant_name, tokens_fn, text_token, pill_attr) -> float:
        """Rapport de contraste d'un jeton de texte sur un fond de pilule composité."""
        tokens = tokens_fn()
        backdrop = _BACKDROP[variant_name]
        lum_pilule = _luminance_composited_over(getattr(tokens, pill_attr), backdrop)
        return _contrast_ratio(
            _relative_luminance(getattr(tokens, text_token)), lum_pilule
        )

    def test_texte_primaire_et_secondaire_wcag_aa_sur_fond_pilule(self):
        """text_primary / text_secondary >= 4.5:1 sur pill_background (light + dark)."""
        for variant, tokens_fn in _VARIANTS:
            with self.subTest(variant=variant):
                for token_name in _TEXT_TOKENS:
                    ratio = self._ratio(variant, tokens_fn, token_name, "pill_background")
                    self.assertGreaterEqual(
                        ratio,
                        _WCAG_AA,
                        f"{variant}.{token_name}: contraste {ratio:.2f}:1 < 4.5:1 sur fond de pilule",
                    )

    def test_texte_primaire_et_secondaire_wcag_aa_sur_fond_pilule_presse(self):
        """text_primary / text_secondary >= 4.5:1 sur pill_background_pressed (light + dark)."""

        for variant, tokens_fn in _VARIANTS:
            with self.subTest(variant=variant):
                for token_name in _TEXT_TOKENS:
                    ratio = self._ratio(
                        variant, tokens_fn, token_name, "pill_background_pressed"
                    )
                    self.assertGreaterEqual(
                        ratio,
                        _WCAG_AA,
                        f"{variant}.{token_name}: contraste {ratio:.2f}:1 < 4.5:1 sur fond de pilule presse",
                    )

    def test_texte_desactive_taux_mesure_et_documente(self):
        """text_disabled : taux mesures sans seuil (texte inactif, exempte de 1.4.3)."""

        for variant, tokens_fn in _VARIANTS:
            with self.subTest(variant=variant):
                ratio = self._ratio(variant, tokens_fn, "text_disabled", "pill_background")
                self.assertGreaterEqual(
                    ratio,
                    1.0,
                    f"{variant}.text_disabled: taux {ratio:.2f}:1 non calculable",
                )


if __name__ == "__main__":
    unittest.main()
