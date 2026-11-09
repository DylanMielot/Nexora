# ARCHITECTURE — Dynamic Island Windows Core

## 1. Vue d'ensemble

Application "Dynamic Island" pour Windows, construite avec PyQt6. Le Core fournit une fenêtre pilule (pill-shape) thématisée (clair/sombre), sans bordure, toujours au-dessus, transparente, hébergeant des modules Plug-and-Play découverts dynamiquement sous `modules/`.

La refonte graphique (missions T008–T013) introduit un système de design centralisé (`core/design/`) : jetons immuables (`DesignTokens`), variantes thèmes clair/sombre, gestionnaire de thème Windows (`ThemeManager`), et refonte de la fenêtre pilule et du module démo Horloge pour consommer ces jetons.

## 2. Objectif

Fournir un socle extensible prêt à accueillir des modules complexes (compagnon IA animé, widgets système, etc.) avec un contrat de module strict, un chargement isolé par module, une animation fluide entre états réduit et étendu, et un système de design thématisé garantissant cohérence visuelle, contraste WCAG et respect du thème système Windows.

## 3. Structure des fichiers

```
D:\project\windows Dynamic Island\
├── main.py                      # Point d'entrée : QApplication, ModuleManager, fenêtre pilule
├── ARCHITECTURE.md              # Ce document (mémoire de transmission)
├── CLAUDE.md                    # Règles de l'équipe d'orchestration
├── core/
│   ├── __init__.py              # Package core
│   ├── base_module.py           # Contrat abstrait BaseModule (5 méthodes)
│   ├── module_manager.py        # Découverte, import, instanciation des modules
│   ├── window.py                # Fenêtre pilule : paintEvent par jetons, animation, tracé QPainterPath, anti-aliasing
│   └── design/                  # Système de design (nouveau, T008–T009)
│       ├── __init__.py          # Exposition de DesignTokens, dark_tokens, light_tokens, ThemeManager
│       ├── tokens.py            # DesignTokens (dataclass gelée, 29 champs) + light_tokens()/dark_tokens()
│       └── theme.py             # ThemeManager (singleton, registre Windows AppsUseLightTheme, signal theme_changed)
├── modules/
│   └── clock_module/            # Module démo : Horloge (refondu, T003, T011)
│       ├── __init__.py          # Exposition de ClockModule
│       └── clock_module.py      # Implémentation de l'horloge (Segoe UI, jetons, QTimer 1 s)
├── docs/
│   └── design-system/
│       └── apple-hig/           # Référence Apple HIG consultée pour la traçabilité (lecture seule)
└── tests/
    ├── __init__.py
    ├── qt_helper.py             # Helper QApplication offscreen partagé
    ├── test_base_module.py      # 6 tests — contrat BaseModule
    ├── test_clock_module.py     # 11 tests — module horloge
    ├── test_main.py             # 2 tests — point d'entrée
    ├── test_module_manager.py   # 6 tests — gestionnaire de modules
    ├── test_window.py           # 13 tests — fenêtre pilule
    ├── test_design_tokens.py    # 9 tests — jetons de design + contraste WCAG
    ├── test_theme.py            # 11 tests — gestionnaire de thème (détection registre mockée)
    ├── test_wcag_contrast.py    # 3 tests — contraste WCAG sur fond de pilule (états normal/pressé)
    └── test_window_states.py    # 7 tests — états interactifs hover/pressed/focus
```

## 4. Contrat BaseModule (core/base_module.py)

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

## 5. Gestionnaire de modules (core/module_manager.py)

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
- `get(module_id)` et `list_ids()` donnent accès aux modules chargés

## 6. Système de design (core/design/) — NOUVEAU

Toutes les valeurs de design sont centralisées dans des jetons (`DesignTokens`). Aucun composant ne doit contenir de valeur de couleur brute en dur. Les noms sont sémantiques (but de l'élément, pas son apparence).

### 6.1 DesignTokens — dataclass gelée, 29 champs

`@dataclass(frozen=True)` : une instance est considérée comme immuable ; les `QColor` et `QSize` qu'elle contient ne doivent pas être mutés après création. Valeurs logiques (pixels logiques, points, ms).

| Groupe | Champs | Rôle |
|--------|--------|------|
| Couleurs (QColor) — 11 | `pill_background`, `pill_background_pressed`, `pill_border`, `pill_shadow`, `text_primary`, `text_secondary`, `text_disabled`, `icon_primary`, `icon_secondary`, `accent_primary`, `separator` | Couleurs de la pilule, texte, icônes, accent, séparateur |
| Espacements — 5 | `pill_padding_h`, `pill_padding_v`, `pill_edge_margin`, `element_gap`, `touch_target_min` | Marges internes, marge aux bords, écart entre éléments, cible tactile minimale (`QSize`) |
| Rayons — 2 | `pill_radius_ratio`, `button_radius` | Rayon de la pilule (ratio de la hauteur), rayon des boutons |
| Typographie — 7 | `font_family`, `font_reduced_primary_pt`, `font_reduced_secondary_pt`, `font_expanded_primary_pt`, `font_expanded_secondary_pt`, `font_weight_primary`, `font_weight_secondary` | Famille de police, tailles et graisses états réduit/étendu |
| Animations — 4 | `anim_duration_expand_ms`, `anim_duration_hover_ms`, `anim_duration_pressed_ms`, `easing_expand` | Durées et courbe d'animation |

### 6.2 Variantes `light_tokens()` / `dark_tokens()` — valeurs exactes

| Champ | `light_tokens()` | `dark_tokens()` |
|-------|------------------|-----------------|
| `pill_background` | `QColor(242, 242, 244, 238)` | `QColor(25, 25, 30, 210)` |
| `pill_background_pressed` | `QColor(225, 225, 230, 238)` | `QColor(45, 45, 50, 210)` |
| `pill_border` | `QColor(160, 160, 170, 140)` | `QColor(90, 90, 100, 160)` |
| `pill_shadow` | `QColor(0, 0, 0, 70)` | `QColor(0, 0, 0, 130)` |
| `text_primary` | `#1C1C1E` | `#F5F5F7` |
| `text_secondary` | `#5A5A64` | `#AEAEB4` |
| `text_disabled` | `#8E8E93` | `#6E6E73` |
| `icon_primary` | `#1C1C1E` | `#F5F5F7` |
| `icon_secondary` | `#5A5A64` | `#AEAEB4` |
| `accent_primary` | `#0078D7` | `#0A84FF` |
| `separator` | `QColor(180, 180, 186, 120)` | `QColor(90, 90, 100, 140)` |
| `pill_padding_h` | 16 | 16 |
| `pill_padding_v` | 12 | 12 |
| `pill_edge_margin` | 8 | 8 |
| `element_gap` | 8 | 8 |
| `touch_target_min` | `QSize(28, 28)` | `QSize(28, 28)` |
| `pill_radius_ratio` | 0.5 | 0.5 |
| `button_radius` | 8 | 8 |
| `font_family` | `"Segoe UI"` | `"Segoe UI"` |
| `font_reduced_primary_pt` | 20 | 20 |
| `font_reduced_secondary_pt` | 10 | 10 |
| `font_expanded_primary_pt` | 22 | 22 |
| `font_expanded_secondary_pt` | 11 | 11 |
| `font_weight_primary` | `QFont.Weight.DemiBold` (600) | `QFont.Weight.DemiBold` (600) |
| `font_weight_secondary` | `QFont.Weight.Normal` (400) | `QFont.Weight.Normal` (400) |
| `anim_duration_expand_ms` | 300 | 300 |
| `anim_duration_hover_ms` | 120 | 120 |
| `anim_duration_pressed_ms` | 100 | 100 |
| `easing_expand` | `QEasingCurve.Type.InOutQuad` | `QEasingCurve.Type.InOutQuad` |

Notes :
- Police système Windows : `"Segoe UI"` (équivalent projet de San Francisco d'Apple ; voir section 10).
- `DemiBold` (600) : Qt n'a pas de graisse "Semibold" ; `DemiBold` est le plus proche (600 == CSS "semibold").
- `anim_duration_expand_ms=300` et courbe `InOutQuad` pour l'animation réduire/étendre de la fenêtre.

### 6.3 ThemeManager — singleton, détection thème Windows

`ThemeManager(QObject)` est un singleton (une instance par application).

- Détection du thème système Windows via la valeur `AppsUseLightTheme` du registre `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize` (`1` = clair, `0` = sombre).
- Repli sur le thème `"light"` si `winreg` est indisponible (plateforme non Windows), clé absente ou erreur d'accès.
- Aucun sélecteur de thème dans l'application : l'application respecte le réglage système (pas de bascule propre à l'app).
- Pas de hot-switch en T009–T013 : la variante est lue au démarrage uniquement. Le signal `theme_changed` est exposé pour une évolution ultérieure.
- API :
  - `ThemeManager.instance(parent=None)` — retourne/crée l'instance unique
  - `variant() -> str` — `"light"` ou `"dark"`
  - `tokens() -> DesignTokens` — jetons de la variante active
  - `theme_changed = pyqtSignal(str)` — émis quand la variante active change
  - `detect_system_variant() -> str` — lecture du registre (statique, mockable en tests)
  - `apply_to_window(window)` — hook best-effort T009 (feuille de style bordure, fond transparent)
  - `apply_to_module(module)` — hook optionnel (applique la famille de police `font_family` aux widgets du module, tailles préservées)

## 7. Fenêtre pilule (core/window.py) — MISE À JOUR

`DynamicIslandWindow(QWidget)` héberge un module via un `QStackedLayout` (index 0 = réduit, index 1 = étendu).

### Constantes de design (spécification T001, décisions D1 et D8)

- `ISLAND_SIZE_REDUCED = (200, 40)`
- `ISLAND_SIZE_EXPANDED = (600, 120)`
- `ISLAND_TOP_FLARE_PX = 2.0` (évasement concave symétrique du sommet au contact Y=0, spec T025)
- `ANIMATION_DURATION_MS = 300`

### Drapeaux de fenêtre

- `FramelessWindowHint` — sans bordure (pas de barre de titre Windows)
- `WindowStaysOnTopHint` — toujours au-dessus
- `WA_TranslucentBackground` — fond transparent

### Dessin de la pilule (`paintEvent`) via les jetons de la variante active

Le dessin s'appuie entièrement sur `self._tokens` (jetons de `ThemeManager`). Aucun masque `QBitmap`, aucun `setMask()`, aucune feuille de style QSS : la forme est peinte directement par `QPainter` sur un `QPainterPath`.

1. Chemin manuel `_island_path(rect)` : tracé continu et fermé (`closeSubpath`), symétrique gauche/droite :
   - `moveTo(x, y)` : contact haut gauche à Y=0, largeur pleine au sommet ;
   - `lineTo(x + w, y)` : arête supérieure pleine largeur ;
   - `cubicTo` concave aux deux coins hauts : flare symétrique vers l'extérieur depuis le bord de l'écran (`ISLAND_TOP_FLARE_PX = 2.0`), effet "coule" sur le bord du moniteur ;
   - flancs verticaux aux coordonnées entières `x` et `x + w` : zéro décalage de pixel, pas de ligne de découpe parasite ;
   - coins bas largement arrondis (`arcTo`, rayon `pill_radius_bottom = 20`, clampé sur `w/2` et `h/2`) ;
   - `closeSubpath()` pour fermer le contour.
2. Anti-aliasing : `painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)` explicite dans `paintEvent` (Qt6 : `HighQualityAntialiasing` indisponible).
3. Fond de la pilule selon l'état interactif (`_pill_background_color()`) :
   - pressé → `pill_background_pressed`
   - survol → variante plus claire de `pill_background` (mélange avec le blanc, facteur +30 %, `_lighter_variant`)
   - repos → `pill_background`
4. Bordure : `QPen(pill_border)` tracésur un chemin intérieur décalé de `pen.widthF() / 2` (compensation d'épaisseur du pinceau) afin que le bord extérieur du trait coïncide exactement avec le contour du chemin — aucun demi-pixel rogné sur la limite `x=0` / `y=0`.
5. Ombre intérieure discrète en bas à droite : trait `pill_shadow` sur un chemin légèrement décalé (`rect.adjusted(2, 2, 0, 0)`), donnant un effet de relief.

Aucune valeur de couleur n'est en dur dans le code de production : tous les coloris viennent des jetons (`pill_background = QColor(15, 15, 15, 250)` ≈ rgba(15,15,15,0.98) en thème sombre).

### États interactifs

- `enterEvent` / `leaveEvent` : activent/désactivent `_hovered` + `update()` (fond plus clair au survol). Le survol **déclenche** l'expansion (`expand()`), le départ de souris déclenche le repli (`collapse()`) — pas de bascule au clic (décision T020, reconduite en T022).
- `mousePressEvent` / `mouseReleaseEvent` : clic gauche active `_pressed` (fond `pill_background_pressed`) ; relâchement réinitialise `_pressed`. Le clic sur un enfant ne bascule plus l'état de la fenêtre (l'eventFilter l'intercepte).
- `eventFilter` sur les widgets enfants (et leurs descendants) : intercepte les événements souris gauche pour qu'un enfant ne les avale pas et que la fenêtre conserve la main sur ses états survol/pression.
- `keyPressEvent` : touche `Escape` ferme la fenêtre (`close()`).

### Animation et visibilité du contenu

- `QVariantAnimation`, durée `ANIMATION_DURATION_MS` (300 ms), courbe `QEasingCurve.Type.InOutQuad`.
- Anime `setFixedSize()` entre `ISLAND_SIZE_REDUCED` (200×40) et `ISLAND_SIZE_EXPANDED` (600×120).
- `expand()` / `collapse()` : `setCurrentIndex(1)` / `setCurrentIndex(0)` sur le `QStackedLayout`, puis `.hide()` sur le widget non actif, avant l'animation.
- Le contenu du module actif est masqué pendant la transition (`_set_module_content_visible(False)`), puis réaffiché à `animation.finished` pour éviter les scintillements et recalculs de texte à chaque frame.
- Si une animation est interrompue, on snap à sa taille finale avant d'en relancer une nouvelle (pas de taille intermédiaire figée).
- `module_size(module, expanded)` retourne les dimensions cibles d'un module (ou `ISLAND_SIZE_REDUCED`/`ISLAND_SIZE_EXPANDED` par défaut).

### Masque de pilule — supprimé (T026)

Le masque `QBitmap` (`_regenerate_mask()` / `setMask()`) a été supprimé : un masque bitmap 1 bit est binaire et ne supporte pas l'anti-aliasing, ce qui provoquait le crénelage de l'arête gauche dans les deux modes. La transparence est désormais assurée uniquement par `WA_TranslucentBackground` combinée au tracé vectoriel de `paintEvent`.

### Position et cycle de vie

- Centrée horizontalement sur l'écran primaire, bord supérieur aligné en haut (`_position_on_primary_screen` via `QApplication.primaryScreen().availableGeometry()`).
- Re-positionnée à chaque `showEvent`.
- `set_module(module)` : nettoie le module sortant (`cleanup()`, `removeWidget()`, `deleteLater()`), répare les widgets dans la pile, pose le filtre d'événements sur les enfants, définit la taille réduite initiale.
- `expand()` / `collapse()` / `toggle()` : bascule réduit/étendu ; `toggle()` appelle `on_click()` du module avant la bascule et est ignoré si aucun module.
- `_on_theme_changed(variant)` : recharge les jetons de la nouvelle variante et redessine (`update()`).

## 8. Point d'entrée (main.py) — INCHANGÉ

`main()` crée l'application (`QApplication`), charge les modules via `ModuleManager`, affiche les avertissements pour les modules en erreur, sélectionne le module "clock" (ou le premier disponible), crée la fenêtre pilule avec ce module, affiche la fenêtre et lance `app.exec()`.

## 9. Module démo Horloge (modules/clock_module/) — MISE À JOUR

`ClockModule(BaseModule)`, `module_id = "clock"`, `display_name = "Horloge"`. Implémente les 5 méthodes du contrat `BaseModule` :

- `get_reduced_size()` → `(200, 40)` ; `get_expanded_size()` → `(600, 120)` (élargis pour éviter le rognage du texte de la date, 160 px de haut ne rentrant pas dans 120 px de conteneur)
- `get_reduced_widget()` / `get_expanded_widget()` → les deux widgets du module (propriété du module, réparent dans la pile de la fenêtre)
- `on_click()` — démo : rafraîchit immédiatement l'affichage
- `cleanup()` — déconnecte `theme_changed` et arrête le `QTimer` avant retrait du module

### Affichage et jetons

Deux `_ClockLabel` (`QLabel` bi-segmente, rendu HTML riche) :

- État réduit : `HH:MM` — texte primaire `20 pt` **DemiBold** (`font_reduced_primary_pt` / `font_weight_primary`), couleur `text_primary`
- État étendu : `HH:MM:SS` + date complète en français (ex. `Lundi 9 Novembre 2026`) — heure `22 pt` **DemiBold** (`font_expanded_primary_pt`), date `11 pt` **Normal** (`font_expanded_secondary_pt`), couleurs `text_primary` / `text_secondary`

Toutes les polices, tailles, graisses et couleurs proviennent de `DesignTokens` du thème actif (`font_family = "Segoe UI"`). Le texte brut (`text()`) reste accessible sans balisage.

### Thème et cycle de vie

- `QTimer` à 1 s (`_refresh` chaque seconde ; démarré au constructeur).
- Abonnement à `ThemeManager.theme_changed` : `_on_theme_changed` recharge les jetons et appelle `set_tokens` sur les deux labels (re-render aux couleurs du nouveau thème).
- `cleanup()` arrête le timer et se désabonne du thème.

## 10. Conformité design et traçabilité (Apple HIG) — NOUVEAU

### 10.1 Méthode et sources

Les pages **Apple Human Interface Guidelines (HIG)** sont une **référence de conception, pas une spécification technique Windows**. Lorsqu'une recommandation Apple entre en conflit avec une contrainte Windows ou l'architecture du projet, le conflit est documenté et une adaptation Windows est proposée.

Chaque règle ci-dessous distingue explicitement :
- **(a)** le principe Apple HIG avec sa page source (fichiers sous `docs/design-system/apple-hig/`) ;
- **(b)** l'adaptation projet / Windows ;
- **(c)** la décision projet.

Aucune règle n'est attribuée à Apple si elle ne figure pas dans une source Apple citée. Les pages `README.md` et `windows-adaptation/` n'existent pas dans ce dépôt et ne sont pas citées.

Pages consultées (existantes dans le dépôt) :
- `foundations/color.md`, `foundations/dark-mode.md`, `foundations/motion.md`, `foundations/typography.md`, `foundations/materials.md`, `foundations/accessibility.md`, `foundations/layout.md`
- `components/system-experiences/live-activities.md`
- `components/presentation/windows.md`

### 10.2 Tableau de traçabilité

| # | Domaine | (a) Principe Apple HIG — page source | (b) Adaptation projet / Windows | (c) Décision projet | Implémentation code |
|---|---------|--------------------------------------|---------------------------------|---------------------|---------------------|
| 1 | Couleurs par thème clair/sombre | Toutes les couleurs doivent fonctionner en clair, sombre et contraste accru ; une couleur personnalisée doit fournir des variantes light et dark ; éviter les valeurs en dur non adaptatives (`foundations/color.md`, `foundations/dark-mode.md`) | Pas de couleur système Apple disponible sous PyQt6/Windows : le projet définit sa propre palette nommée, avec variantes `light_tokens()` / `dark_tokens()` ; détection du thème via le registre Windows `AppsUseLightTheme` au lieu de l'apparence macOS | Palette projet propre (accent `#0078D7` light / `#0A84FF` dark), fallback clair, lecture au démarrage uniquement (pas de hot-switch T009–T013, signal prêt pour plus tard) | `core/design/tokens.py`, `core/design/theme.py` |
| 2 | Contraste texte/fond ≥ 4.5:1 (WCAG AA) | WCAG Level AA : 4.5:1 jusqu'à 17 pt, 3:1 en gras ; vérifier le contraste dans les deux apparences (`foundations/accessibility.md`, `foundations/dark-mode.md`) | Les tests mesurent le contraste sur le fond de pilule **composité** (alpha sur fond blanc/noir), thèmes light et dark, pour `text_primary` et `text_secondary` | `text_disabled` exclu du seuil (texte inactif, exempt de WCAG 1.4.3) mais mesuré et documenté ; seuil appliqué comme porte-qualité projet sur Windows | `tests/test_design_tokens.py`, `tests/test_wcag_contrast.py` |
| 3 | Respect du thème système, pas de bascule propre à l'app | Éviter un réglage d'apparence spécifique à l'app : les utilisateurs attendent que l'app respecte le choix système (`foundations/dark-mode.md`) | Lecture unique au démarrage de `AppsUseLightTheme` (registre Windows) ; aucun sélecteur de thème dans l'application ; pas de hot-switch en T009–T013 | Signal `theme_changed` exposé pour un hot-switch ultérieur ; thème figé pendant la session | `core/design/theme.py` (`detect_system_variant`) |
| 4 | Aspect "matériau", translucidité et relief | Les matériaux créent profondeur et hiérarchie par superposition ; la préférence pour la translucidité sur l'opacité figure dans les considérations visionOS de `foundations/materials.md` | PyQt6 n'a pas d'API matérielle/vibrance native : la pilule utilise `WA_TranslucentBackground`, fond alpha (210 sombre / 238 clair), bordure `pill_border` et trait intérieur `pill_shadow` en bas à droite pour simuler le relief | Simulation par calque alpha + bordure + ombre intérieure ; pas de flou d'arrière-plan (backdrop blur) sous Windows | `core/window.py` (`paintEvent`, `_regenerate_mask`) |
| 5 | Animations courtes, purposeuses, interrompables | Ajouter du mouvement avec intention, pas pour le mouvement ; brièveté et précision des animations de feedback ; laisser l'utilisateur annuler (`foundations/motion.md`) | `QVariantAnimation` 300 ms `InOutQuad` pour réduire/étendre ; une animation interrompue snappe à sa taille finale avant qu'une nouvelle démarre (re-clic immédiat possible) ; tokens hover 120 ms / pressed 100 ms définis | 300 ms = choix projet dans la borne "brève" d'Apple ; ni haptique ni retour audio de remplacement sous Windows (hors périmètre) | `core/window.py` (`_animate_to`, `_animation`), `core/design/tokens.py` |
| 6 | Police système et hiérarchie typographique | Utiliser la police système de la plateforme ; éviter les graisses légères (préférer Regular/Medium/Semibold/Bold) ; taille, graisse, couleur pour exprimer la hiérarchie (`foundations/typography.md`) | `Segoe UI` (police système Windows) remplace San Francisco ; tailles et graisses dans les jetons : réduit 20 pt DemiBold / 10 pt Normal, étendu 22 pt DemiBold / 11 pt Normal ; pas de suivi de la taille de texte système (Dynamic Type) sous Windows | `DemiBold` (600) car Qt n'a pas de Semibold ; graisses et tailles figées, identiques light et dark | `core/design/tokens.py`, `modules/clock_module/clock_module.py` (`_ClockLabel`) |
| 7 | Cibles d'interaction dimensionnées | Contrôles suffisamment dimensionnés ; macOS minimum 20×20 pt, défaut 28×28 pt ; espacement entre contrôles (`foundations/accessibility.md`) | Jeton `touch_target_min = QSize(28, 28)` ; marges de pilule `pill_padding_h=16` / `pill_padding_v=12`, `pill_edge_margin=8`, `element_gap=8` | Jeton défini et documenté, pas encore imposé sur chaque élément interactif des modules (écart relevé en revue T013) | `core/design/tokens.py` |
| 8 | État clavier / focus | Navigation au clavier (Full Keyboard Access) (`foundations/accessibility.md`) | Les événements `FocusIn`/`FocusOut` sont tolérés sans planter ; la couleur de pilule ne change pas : aucun état de focus visuel dédié aujourd'hui | Écart identifié (finding **F2**, revue T013), correction reportée après le socle | `core/window.py` (`keyPressEvent`, `eventFilter`), `tests/test_window_states.py` |
| 9 | Widget glanceable réduit → étendu (Live Activities) | Informations à consulter d'un coup d'œil ; présentations compacte/minimale/étendue ; texte gros et plus gras (medium weight ou plus) (`components/system-experiences/live-activities.md`) | Windows n'a pas de Dynamic Island : pilule always-on-top centrée en haut de l'écran principal ; état réduit (`HH:MM`) / étendu (`HH:MM:SS` + date) ; bascule au clic (`on_click` avant transition) ; `Escape` ferme | Adaptation Windows du concept de widget système glanceable ; jamais présenté comme une fonctionnalité Apple | `core/window.py`, `modules/clock_module/clock_module.py`, `main.py` |
| 10 | Pas d'information par la couleur seule | Ne pas se fier uniquement à la couleur pour indiquer l'interactivité ou une information essentielle ; fournir des alternatives (`foundations/color.md`) | L'interactivité est redondée : changement de fond (survol/pression), animation de taille, texte ; aucun état ne diffère uniquement par la couleur | Règle projet appliquée aux états de la pilule | `core/window.py` (`_pill_background_color`, animation) |
| 11 | Fenêtre sans bordure / toujours au-dessus | Éviter les UI de fenêtre personnalisées ; les fenêtres système sont reconnaissibles (`components/presentation/windows.md`) | **Conflit documenté** : le concept Dynamic Island exige une fenêtre sans bordure, toujours au-dessus et en forme de pilule sous Windows ; la recommandation Apple n'est pas applicable telle quelle | Déviation délibérée et documentée : `FramelessWindowHint` + `WindowStaysOnTopHint` + masque QBitmap ; positionnement mono-écran (écart **F3**, revue T013) | `core/window.py` |

### 10.3 Règles d'implémentation du projet (design system)

- Réutiliser les tokens existants ; aucune valeur arbitraire répétée pour espacements, rayons, couleurs, typographies, ombres et durées d'animation.
- Préserver lisibilité, contraste, états clavier/souris, thème sombre/clair, scaling DPI et différentes tailles de fenêtre/écran.
- Interactions cohérentes Windows : souris, survol, clic droit, clavier, focus, écrans multiples.

## 11. État d'avancement (T001–T017)

| Mission | Objectif | Statut |
|---------|----------|--------|
| T001 | Spécification technique (contrat BaseModule, découverte, pilule/animations, extensions) | COMPLETED |
| T002 | Implémentation Core (base_module, module_manager, window, main) | COMPLETED |
| T003 | Module démo Horloge | COMPLETED |
| T004 | Tests unitaires/fonctionnels | COMPLETED |
| T005 | Revue indépendante (défauts M1-M4) | COMPLETED |
| T006 | Mémoire de transmission : ARCHITECTURE.md (version initiale) | COMPLETED |
| T007 | Correction des défauts M1-M4 | COMPLETED |
| T008 | Spécification du système de design (tokens, thèmes, composants) | COMPLETED |
| T009 | Implémentation `core/design/tokens.py` et `core/design/theme.py` + tests | COMPLETED |
| T010 | Refactor `core/window.py` consommant les jetons (paintEvent, hover/pressed, masque, filtre enfants) | COMPLETED |
| T011 | Refactor `modules/clock_module/clock_module.py` (Segoe UI, tailles/couleurs des jetons) | COMPLETED |
| T012 | Tests WCAG, états interactifs (hover/pressed/focus), suite de régression | COMPLETED |
| T013 | Revue indépendante T009–T013 — verdict APPROVÉ | COMPLETED |
| T014 | Spécification de la mise à jour d'ARCHITECTURE.md | COMPLETED |
| T015 | Réécriture d'ARCHITECTURE.md (refonte graphique) — cette mission | COMPLETED |
| T016 | Revue indépendante d'ARCHITECTURE.md réécrit | COMPLETED |
| T017 | Exécution de la suite de tests complète (confirmation des chiffres) | COMPLETED |
| T021 | Spécification : conteneur unique noir magnétisé en haut de l'écran | COMPLETED |
| T022 | Refactor visuel : conteneur unique noir, coins hauts carrés / bas arrondis, animation 200×40 ↔ 600×120, masquage contenu pendant transition | COMPLETED |
| T023 | Revue indépendante T021–T022 — verdict APPROVÉ (11/11 checkpoints CONFIRMED) | COMPLETED |
| T024 | Tests : mise à jour des attentes (66 tests, tous passés) | COMPLETED |
| T025 | Spécification technique : correction arête gauche pixelisée et courbes supérieures via QPainterPath (core/window.py) | COMPLETED |
| T026 | Implémentation : suppression masque QBitmap, _island_path symétrique, paintEvent anti-aliasing + alignement pixels (core/window.py) | COMPLETED |
| T027 | Revue indépendante : absence QSS, anti-aliasing activé, géométrie symétrique, alignement pixels, pas de régression | COMPLETED |
| T028 | Tests : mise à jour test_window.py (masque supprimé, symétrie, anti-aliasing), suite 68 tests verte | COMPLETED |
| T029 | Mise à jour ARCHITECTURE.md et registry.json (sect. 7 : tracé vectoriel, alignement pixels, masque supprimé) | COMPLETED |

## 12. Tests

Suite de tests : **68 tests au total, tous passés, zéro régression**, exécutés avec `QT_QPA_PLATFORM=offscreen` (pas de serveur d'affichage requis) :

| Fichier de tests | Nombre de tests | Couverture |
|------------------|-----------------|------------|
| `test_base_module.py` | 6 | Contrat BaseModule (abstraction, signatures, instanciation) |
| `test_clock_module.py` | 11 | Module horloge (tailles, widgets, formats, timer, on_click, cleanup) |
| `test_main.py` | 2 | Point d'entrée |
| `test_module_manager.py` | 6 | Découverte, instanciation, isolation d'erreurs, répertoire inexistant |
| `test_window.py` | 13 | Fenêtre pilule (taille, drapeaux, tracé, anti-aliasing, animation, bascule, position, clavier) |
| `test_design_tokens.py` | 9 | Jetons de design (gélure, 29 champs, valeurs exactes, contraste WCAG sur fond pilule) |
| `test_theme.py` | 11 | Gestionnaire de thème (singleton, signal, détection registre Windows mockée/réelle, hooks) |
| `test_wcag_contrast.py` | 3 | Contraste WCAG AA ≥ 4.5:1 sur fond pilule normal et pressé, light + dark |
| `test_window_states.py` | 7 | États interactifs (survol, pression, eventFilter enfants, focus) |
| **Total** | **68** | **Tous passés (OK)** |

Dernière exécution confirmée : 68 tests OK en environ 3,7 s (hôte : thème sombre détecté via le registre Windows). Suite relancée et validée dans le cadre de la mission T028.

Les tests utilisent `tests/qt_helper.py` (QApplication partagé, plateforme offscreen, chemin racine ajouté à `sys.path` avant tout import PyQt6).

## 13. Spécification de la prochaine brique : Compagnon IA animé — MISE À JOUR

Le prochain module à développer est un "compagnon IA animé" qui s'affichera dans la pilule Dynamic Island.

Contraintes architecturales :
- Doit hériter de `BaseModule` et implémenter les 5 méthodes abstraites
- Doit fournir un `module_id` unique (ex. `"ai_companion"`)
- **Les couleurs, polices, tailles et animations proviennent de `DesignTokens` (`core.design`) ; aucune valeur en dur** (police `Segoe UI`, tailles de texte, `accent_primary`, etc.)
- Les widgets d'animation appartiennent au module ; la fenêtre les réparent dans son `QStackedLayout`
- Doit implémenter `cleanup()` pour arrêter proprement les timers/animations à la désinstallation
- Doit propager `ThemeManager.theme_changed` si ses couleurs doivent suivre le thème système
- L'état réduit affiche une représentation compacte (ex. icône ou avatar statique) ; l'état étendu affiche l'animation complète et les interactions (ex. bulle de dialogue, expressions faciales)
- `on_click()` peut déclencher une interaction (ex. réveil, changement d'expression)
- Accessibilité : contraste WCAG AA ≥ 4.5:1 pour le texte sur fond de pilule, pas d'information par la couleur seule, cibles d'interaction ≥ `touch_target_min` (28×28)

Points d'extension du Core déjà prêts :
- `ModuleManager.discover()` détecte automatiquement tout nouveau dossier sous `modules/`
- `set_module()` gère le nettoyage du module sortant et l'installation du nouveau
- L'animation de taille s'adapte automatiquement aux dimensions retournées par `get_reduced_size()` / `get_expanded_size()`

## 14. Limites connues (revue T013, verdict APPROVÉ)

La revue T013 (verdict APPROVÉ, 0 critique/élevé, 12 constats dont 3 moyens, 6 bas, 3 info) identifie les limites suivantes du socle actuel :

- **F1 — Immutabilité des jetons** : `DesignTokens` est un `@dataclass(frozen=True)`, mais il contient des `QColor` et `QSize` mutables ; aucune protection runtime n'empêche la mutation des objets contenus après création.
- **F2 — Absence d'état focus visuel dédié** : les événements de focus sont tolérés sans planter, mais la couleur de la pilule ne change pas à la prise de focus clavier.
- **F3 — Positionnement mono-écran uniquement** : la fenêtre est positionnée sur l'écran primaire à chaque `showEvent` ; aucun suivi multi-écrans ni adaptation au scaling DPI n'est implémenté.

Les constats bas et info de T013 sont documentés dans le rapport de revue associé et seront traités selon la capacité de l'équipe.
