"""Gestionnaire de decoupage dynamique et de chargement des modules.

Convention : modules/<module_id>/__init__.py +
modules/<module_id>/<module_id>.py exposant une classe publique heritant de
BaseModule.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from types import ModuleType
from typing import Optional

from core.base_module import BaseModule

logger = logging.getLogger(__name__)


class ModuleManager:
    """Decouvre, importe et instancie les modules sous modules/<id>/.

    Les erreurs d'import ou d'instantiation sont isolees par module : un
    module defectueux n'empeche pas les autres de se charger.
    """

    def __init__(self, modules_dir: str | None = None) -> None:
        if modules_dir is None:
            modules_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"
            )
        self.modules_dir = os.path.abspath(modules_dir)
        self._modules: dict[str, BaseModule] = {}
        self._errors: list[tuple[str, str]] = []

    def discover(self) -> list[type[BaseModule]]:
        """Scan les sous-dossiers immediats de modules/ et collecte les classes.

        Retourne les classes non abstraites heritant de BaseModule (a
        l'exclusion de BaseModule elle-meme).
        """
        classes: list[type[BaseModule]] = []
        if not os.path.isdir(self.modules_dir):
            return classes

        for entry in sorted(os.listdir(self.modules_dir)):
            pkg_dir = os.path.join(self.modules_dir, entry)
            init_py = os.path.join(pkg_dir, "__init__.py")
            module_py = os.path.join(pkg_dir, f"{entry}.py")
            if (
                not os.path.isdir(pkg_dir)
                or not os.path.isfile(init_py)
                or not os.path.isfile(module_py)
            ):
                continue

            module_name = f"modules.{entry}.{entry}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_py)
                if spec is None or spec.loader is None:
                    raise ImportError(f"pas de spec de chargement pour {module_py}")
                module = ModuleType(module_name)
                module.__file__ = module_py
                sys.modules[module_name] = module
                spec.loader.exec_module(module)  # type: ignore[union-attr]
            except Exception as exc:  # isolation par module
                logger.exception("Erreur d'import du module %s", entry)
                self._errors.append((entry, str(exc)))
                sys.modules.pop(module_name, None)
                continue

            for candidate in vars(module).values():
                if (
                    isinstance(candidate, type)
                    and issubclass(candidate, BaseModule)
                    and candidate is not BaseModule
                ):
                    classes.append(candidate)  # type: ignore[arg-type]

        return classes

    def instantiate(self, cls: type[BaseModule]) -> Optional[BaseModule]:
        """Instancie une classe de module, ou retourne None en cas d'erreur."""
        module_id = getattr(cls, "module_id", cls.__name__)
        try:
            module = cls()
        except Exception as exc:
            logger.exception("Erreur d'instantiation du module %s", module_id)
            self._errors.append((module_id, str(exc)))
            return None
        return module

    def load_all(self) -> dict[str, BaseModule]:
        """Decouvre puis instancie tous les modules.

        Retourne une copie du cache indexe par module_id.
        """
        self._modules = {}
        self._errors = []
        for cls in self.discover():
            module = self.instantiate(cls)
            if module is None:
                continue
            module_id = module.module_id
            if module_id in self._modules:
                logger.warning(
                    "Identifiant de module duplique '%s' (classe %s) : "
                    "le module est ignore",
                    module_id,
                    cls.__name__,
                )
                self._errors.append((module_id, f"module_id duplique : {module_id}"))
                continue
            self._modules[module_id] = module
        return dict(self._modules)

    def get(self, module_id: str) -> Optional[BaseModule]:
        """Retourne le module instancie correspondant, ou None."""
        return self._modules.get(module_id)

    def list_ids(self) -> list[str]:
        """Retourne les identifiants des modules charges."""
        return list(self._modules.keys())

    @property
    def errors(self) -> list[tuple[str, str]]:
        """Liste des (identifiant, message) d'erreurs survenues."""
        return list(self._errors)
