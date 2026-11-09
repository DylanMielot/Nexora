"""Point d'entree de l'application Dynamic Island (Windows, PyQt6)."""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from core.module_manager import ModuleManager
from core.window import DynamicIslandWindow

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    """Cree l'application, charge les modules et affiche la fenetre pilule.

    Retourne le code de sortie de QApplication.exec().
    """
    app = QApplication(sys.argv)

    manager = ModuleManager()
    modules = manager.load_all()
    for module_id, message in manager.errors:
        logging.warning("Module %s ignore : %s", module_id, message)

    module = modules.get("clock") if modules else None
    if module is None and modules:
        module = next(iter(modules.values()))
    if module is None:
        logging.warning(
            "Aucun module disponible : fenetre pilule vide affichee sans module."
        )

    window = DynamicIslandWindow(module=module)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
