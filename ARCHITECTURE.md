# ARCHITECTURE — Dynamic Island Windows Core

## Vue d'ensemble

Application "Dynamic Island" pour Windows, construite avec PyQt6. Le Core fournit une fenêtre pilule (pill-shape) sans bordure, toujours au-dessus, transparente, hébergeant des modules Plug-and-Play découverts dynamiquement sous `modules/`.

## Objectif

Fournir un socle extensible prêt à accueillir des modules complexes (compagnon IA animé, widgets système, etc.) avec un contrat de module strict, un chargement isolé par module et une animation fluide entre états réduit et étendu.

## Structure des fichiers

```
D:\project\windows Dynamic Island\
├── main.py                      # Point d'entrée : QApplication, ModuleManager, fenêtre pilule
├── ARCHITECTURE.md              # Ce document (mémoire de transmission)
├── CLAUDE.md                    # Règles de l'équipe d'orchestration
├── core/
│   ├── __init__.py              # Package core
│   ├── base_module.py           # Contrat abstrait BaseModule (5 méthodes)
│   ├── module_manager.py        # Découverte, import, instanciation des modules
│   └── window.py                # Fenêtre pilule, animation, QStackedLayout
├── modules/
│   └── clock_module/            # Module démo : Horloge
│       ├── __init__.py          # Exposition de ClockModule
│       └── clock_module.py      # Implémentation de l'horloge
└── tests/
    ├── __init__.py
    ├── qt_helper.py             # Helper QApplication offscreen partagé
    ├── test_base_module.py      # Contrat BaseModule
    ├── test_clock_module.py     # Module horloge
    ├── test_main.py             # Point d'entrée
    ├── test_module_manager.py   # Gestionnaire de modules
    └── test_window.py           # Fenêtre pilule
```

## Contrat BaseModule (core/base_module.py)

Toute classe de module doit hériter de `BaseModule(QWidget, ABC)` et implémenter les 5 méthodes abstraites suivantes :

| Méthode | Retour | Rôle |
|---------|--------|------|
| `get_reduced_widget()` | `QWidget` | Widget affiché en état réduit (200 × 60 par défaut) |
| `get_expanded_widget()` | `QWidget` | Widget affiché en état étendu (400 × 160 par défaut) |
| `get_reduced_size()` | `tuple[int, int]` | Dimensions (largeur, hauteur) de l'état réduit |
| `get_expanded_size()` | `tuple[int, int]` | Dimensions (largeur, hauteur) de l'état étendu |
| `on_click()` | `None` | Action déclenchée par un clic sur la pilule, avant la bascule |

Attributs de classe :
- `module_id: str` — identifiant unique du module (défaut `"base_module"`)
- `display_name: str` — nom lisible (défaut `"Module de base"`)

Le module reste propriétaire des widgets qu'il retourne ; la fenêtre les réparent dans son `QStackedLayout`.

Une méthode optionnelle `cleanup()` peut être définie pour libérer les ressources (ex. arrêter un `QTimer`) avant que le module soit retiré.

## Gestionnaire de modules (core/module_manager.py)

`ModuleManager` découvre, importe et instancie tous les modules sous `modules/<module_id>/`.

Convention de découverte :
- Sous-dossier immédiat de `modules/`
- Contient `__init__.py` et `<module_id>.py`
- Le module expose une classe publique héritant de `BaseModule`

Comportement :
- Les erreurs d'import ou d'instantiation sont isolées par module : un module défectueux n'empêche pas les autres de se charger
- Les erreurs sont enregistrées dans `self.errors` (liste de `(module_id, message)`)
- Les `module_id` dupliqués sont détectés : un warning est logged, le duplicata est ignoré, une erreur est enregistrée
- `load_all()` retourne un dictionnaire indexé par `module_id`
- `discover()` retourne la liste des classes non abstraites héritant de `BaseModule`

## Fenêtre pilule (core/window.py)

`DynamicIslandWindow(QWidget)` héberge un module via un `QStackedLayout` (index 0 = réduit, index 1 = étendu).

Constantes de design :
- `REDUCED_SIZE = (200, 60)`
- `EXPANDED_SIZE = (400, 160)`
- `ANIMATION_DURATION_MS = 300`
- `PILL_COLOR = QColor(25, 25, 30, 210)`

Drapeaux de fenêtre :
- `FramelessWindowHint` — sans bordure
- `WindowStaysOnTopHint` — toujours au-dessus
- `WA_TranslucentBackground` — fond transparent

Cycle de vie :
1. `set_module(module)` — installe un module, nettoie le module sortant (`cleanup()`, `removeWidget()`, `deleteLater()`), répare les widgets dans la pile, définit la taille réduite initiale
2. `expand()` / `collapse()` — bascule entre états avec animation de taille
3. `toggle()` — bascule réduit/étendu ; appelle `on_click()` du module avant la bascule ; ignoré si aucun module

Animation :
- `QVariantAnimation` (300 ms, courbe `InOutQuad`)
- `setFixedSize()` animée entre la taille actuelle et la cible
- `_regenerate_mask()` régénère le masque QBitmap en pilule à chaque changement de taille
- Si une animation est interrompue, on snap à sa taille finale avant d'en relancer une nouvelle

Position :
- Centrée horizontalement sur l'écran principal, bord supérieur aligné en haut
- Re-positionnée à chaque `showEvent`

## Point d'entrée (main.py)

`main()` crée l'application, charge les modules via `ModuleManager`, affiche les avertissements pour les modules en erreur, sélectionne le module "clock" (ou le premier disponible), crée la fenêtre pilule avec ce module et lance `app.exec()`.

## État d'avancement

| Mission | Objectif | Statut |
|---------|----------|--------|
| T001 | Spécification technique (contrat BaseModule, découverte, pilule/animations, extensions) | COMPLETED |
| T002 | Implémentation Core (base_module, module_manager, window, main) | COMPLETED |
| T003 | Module démo Horloge | COMPLETED |
| T004 | Tests unitaires/fonctionnels (36 tests, tous passés) | COMPLETED |
| T005 | Revue indépendante (défauts M1-M4 identifiés) | COMPLETED |
| T006 | Mémoire de transmission : ARCHITECTURE.md | COMPLETED |
| T007 | Correction des défauts M1-M4 (déjà présents dans le code) | COMPLETED |

## Spécification de la prochaine brique : Compagnon IA animé

Le prochain module à développer est un "compagnon IA animé" qui s'affichera dans la pilule Dynamic Island.

Contraintes architecturales :
- Doit hériter de `BaseModule` et implémenter les 5 méthodes abstraites
- Doit fournir un `module_id` unique (ex. `"ai_companion"`)
- Les widgets d'animation appartiennent au module ; la fenêtre les réparent dans son `QStackedLayout`
- Doit implémenter `cleanup()` pour arrêter proprement les timers/animations à la désinstallation
- L'état réduit affiche une représentation compacte (ex. icône ou avatar statique)
- L'état étendu affiche l'animation complète et les interactions (ex. bulle de dialogue, expressions faciales)
- `on_click()` peut déclencher une interaction (ex. réveil, changement d'expression)

Points d'extension du Core déjà prêts :
- `ModuleManager.discover()` détecte automatiquement tout nouveau dossier sous `modules/`
- `set_module()` gère le nettoyage du module sortant et l'installation du nouveau
- L'animation de taille s'adapte automatiquement aux dimensions retournées par `get_reduced_size()` / `get_expanded_size()`

## Tests

Suite de tests : 36 tests, tous passés (`python -m unittest discover -v tests/`).
- `test_base_module.py` — contrat BaseModule (abstraction, signatures, instanciation)
- `test_clock_module.py` — module horloge (tailles, widgets, formats, timer, on_click)
- `test_main.py` — point d'entrée
- `test_module_manager.py` — découverte, instanciation, isolation d'erreurs, répertoire inexistant
- `test_window.py` — fenêtre pilule (taille, drapeaux, masque, animation, bascule, position, clavier)

Les tests utilisent `QT_QPA_PLATFORM=offscreen` (pas de serveur d'affichage requis).