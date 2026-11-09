"""Tests du gestionnaire de modules core.module_manager.ModuleManager (critere T002-2)."""

import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.base_module import BaseModule  # noqa: E402
from core.module_manager import ModuleManager  # noqa: E402
from modules.clock_module.clock_module import ClockModule  # noqa: E402

_GOOD_MODULE_SOURCE = textwrap.dedent(
    """
    from core.base_module import BaseModule


    class GoodModule(BaseModule):
        module_id = "good"
        display_name = "Bon module"

        def get_reduced_widget(self):
            return None

        def get_expanded_widget(self):
            return None

        def get_reduced_size(self):
            return (10, 10)

        def get_expanded_size(self):
            return (20, 20)

        def on_click(self):
            pass
    """
)


class TestModuleManager(unittest.TestCase):
    def test_discover_trouve_horloge_sur_repertoire_reel(self):
        manager = ModuleManager()
        classes = manager.discover()
        ids = {cls.module_id for cls in classes}
        self.assertEqual(ids, {"clock"})
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].module_id, "clock")
        # Charge sous le nom sys.modules 'modules.clock_module.clock_module' a
        # chaque discovery : on compare via la classe retournee, pas via l'import statique.
        self.assertTrue(all(issubclass(cls, BaseModule) for cls in classes))

    def test_load_all_instancie_et_met_en_cache(self):
        manager = ModuleManager()
        modules = manager.load_all()
        self.assertIn("clock", modules)
        clock = modules["clock"]
        self.assertIsInstance(clock, BaseModule)
        self.assertEqual(type(clock).module_id, "clock")
        self.assertIs(manager.get("clock"), clock)
        self.assertEqual(manager.list_ids(), ["clock"])
        self.assertEqual(manager.errors, [])

    def test_instantiate(self):
        manager = ModuleManager()
        instance = manager.instantiate(ClockModule)
        self.assertIsInstance(instance, ClockModule)
        self.assertEqual(instance.module_id, "clock")

    def test_instantiate_echec_isolement(self):
        """Une classe dont le constructeur echoue retourne None et enregistre l'erreur."""

        class Incomplete(BaseModule):
            module_id = "incomplete"

            pass

        manager = ModuleManager()
        self.assertIsNone(manager.instantiate(Incomplete))
        self.assertEqual(len(manager.errors), 1)
        self.assertEqual(manager.errors[0][0], "incomplete")
        self.assertIn("abstract", manager.errors[0][1].lower())

    def test_repertoire_inexistant_sans_crash(self):
        manager = ModuleManager(modules_dir="/chemin/qui/n/existe/pas")
        self.assertEqual(manager.discover(), [])
        self.assertEqual(manager.errors, [])

    def test_erreur_import_isolee_et_autres_chargent(self):
        """Un module defective ne bloque pas les autres ; l'erreur est enregistre."""
        tmp = tempfile.mkdtemp(prefix="dynamic_island_test_")
        try:
            # Module correct.
            good_dir = os.path.join(tmp, "good")
            os.mkdir(good_dir)
            with open(os.path.join(good_dir, "__init__.py"), "w", encoding="utf-8") as f:
                f.write('from .good import GoodModule\n__all__ = ["GoodModule"]\n')
            with open(os.path.join(good_dir, "good.py"), "w", encoding="utf-8") as f:
                f.write(_GOOD_MODULE_SOURCE)

            # Module dont l'import leve une exception.
            broken_dir = os.path.join(tmp, "broken")
            os.mkdir(broken_dir)
            with open(os.path.join(broken_dir, "__init__.py"), "w", encoding="utf-8") as f:
                f.write("")
            with open(os.path.join(broken_dir, "broken.py"), "w", encoding="utf-8") as f:
                f.write("raise ImportError('module casse')\n")

            # Repertoires non conformes : ignorés, sans erreur enregistre.
            os.mkdir(os.path.join(tmp, "pas_un_paquet"))
            bad2 = os.path.join(tmp, "sans_module_py")
            os.mkdir(bad2)
            with open(os.path.join(bad2, "__init__.py"), "w", encoding="utf-8") as f:
                f.write("")

            manager = ModuleManager(modules_dir=tmp)
            classes = manager.discover()
            self.assertEqual(len(classes), 1)
            self.assertEqual(classes[0].module_id, "good")
            self.assertEqual(len(manager.errors), 1)
            self.assertEqual(manager.errors[0][0], "broken")
            self.assertIn("module casse", manager.errors[0][1])

            modules = manager.load_all()
            self.assertEqual(set(modules), {"good"})
            self.assertIsInstance(modules["good"], BaseModule)
            self.assertEqual(manager.list_ids(), ["good"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
