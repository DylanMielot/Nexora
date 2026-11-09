"""Helper commun aux tests Qt : plateforme offscreen, chemin du projet, QApplication partage.

Ce module est importe par chaque fichier de tests qui a besoin de Qt.
"""

import os
import sys
from pathlib import Path

# Le dossier racine du projet (celui qui contient core/ et modules/) doit etre
# importable depuis les tests.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Qt sans serveur d'affichage. Doit etre pose AVEC tout import de PyQt6.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication  # noqa: E402

_app = None


def qapp() -> QApplication:
    """Retourne l'instance QApplication de la session de tests, en la creant si besoin."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication([])
    return _app
