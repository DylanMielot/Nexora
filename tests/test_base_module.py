"""Tests du contrat abstrait Core : core.base_module.BaseModule (critere T002-1)."""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.qt_helper import qapp  # noqa: E402
from core.base_module import BaseModule  # noqa: E402
from PyQt6.QtWidgets import QWidget  # noqa: E402

ABSTRACT_METHODS = [
    "get_reduced_widget",
    "get_expanded_widget",
    "get_reduced_size",
    "get_expanded_size",
    "on_click",
]


class _ConcreteModule(BaseModule):
    """Implantation minimale et concrete du contrat, uniquement pour les tests."""

    def get_reduced_widget(self) -> QWidget:
        return QWidget()

    def get_expanded_widget(self) -> QWidget:
        return QWidget()

    def get_reduced_size(self) -> tuple[int, int]:
        return (10, 10)

    def get_expanded_size(self) -> tuple[int, int]:
        return (20, 20)

    def on_click(self) -> None:
        return None


class TestBaseModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = qapp()

    def test_ne_sert_pas_directement(self):
        """BaseModule est abstrait : l'instantiation directe leve TypeError."""
        with self.assertRaises(TypeError):
            BaseModule()

    def test_attributs_de_classe(self):
        self.assertEqual(BaseModule.module_id, "base_module")
        self.assertEqual(BaseModule.display_name, "Module de base")

    def test_cinq_methodes_abstraites(self):
        """Les cinq methodes obligatoires sont declares abstraits."""
        abstracts = set(BaseModule.__abstractmethods__)
        self.assertEqual(abstracts, set(ABSTRACT_METHODS))
        for name in ABSTRACT_METHODS:
            self.assertTrue(hasattr(BaseModule, name), f"{name} manquante")

    def test_signatures_precises(self):
        """Signatures exactes des methodes abstraites et du constructeur."""
        expected = {
            "get_reduced_widget": (["self"], "QWidget"),
            "get_expanded_widget": (["self"], "QWidget"),
            "get_reduced_size": (["self"], "tuple[int, int]"),
            "get_expanded_size": (["self"], "tuple[int, int]"),
            "on_click": (["self"], "None"),
        }
        for name, (params, ret) in expected.items():
            sig = __import__("inspect").signature(getattr(BaseModule, name))
            self.assertEqual(list(sig.parameters), params, f"signature {name}")
            self.assertEqual(sig.return_annotation, ret, f"retour {name}")

        init_sig = __import__("inspect").signature(BaseModule.__init__)
        self.assertEqual(list(init_sig.parameters), ["self", "parent"])
        self.assertIs(init_sig.parameters["parent"].default, None)
        self.assertEqual(init_sig.return_annotation, "None")

    def test_constructeur_accepte_parent(self):
        """__init__(parent=None) : parent None par defaut, ou widget donne."""
        module = _ConcreteModule()
        self.assertIsNone(module.parent())

        parent = QWidget()
        module_with_parent = _ConcreteModule(parent=parent)
        self.assertIs(module_with_parent.parent(), parent)

    def test_sous_classe_concrete_instantiable(self):
        """Une sous-classe impliquant les cinq methodes est instantiable."""
        module = _ConcreteModule()
        self.assertIsInstance(module, BaseModule)
        self.assertEqual(module.get_reduced_size(), (10, 10))
        self.assertEqual(module.get_expanded_size(), (20, 20))
