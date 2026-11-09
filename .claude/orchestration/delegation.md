# Politique de délégation

## Autorité

Seule la session principale (orchestrateur) lance les subagents. Les spécialistes n'ont pas l'outil `Agent` dans leur liste d'outils.

Un spécialiste peut demander une délégation via `delegation_requests` dans son rapport. L'orchestrateur accepte, refuse ou reformule.

## Critères d'acceptation

Accepter seulement si :
- la sous-tâche est distincte et utile ;
- le livrable est vérifiable ;
- le périmètre est explicite ;
- elle ne duplique pas une mission existante ;
- ses dépendances sont satisfaites ;
- le plafond de trois subagents actifs le permet ;
- le coût de coordination est justifié.

Refuser ou reformuler si la tâche est triviale, vague, redondante, circulaire ou plus coûteuse à déléguer qu'à traiter directement.

## Profondeur

La profondeur Claude Code est fixée à `1` dans `.claude/settings.json`. Les agents de premier niveau ne peuvent donc pas lancer d'agents imbriqués. Cette limite technique renforce la règle de délégation centralisée.

Les missions secondaires sont créées par l'orchestrateur comme de nouvelles missions de premier niveau, avec `parent_id` renseigné pour conserver leur filiation logique.

## Capacité

Trois subagents actifs maximum, tous types confondus dans cette session. Vérifier les agents déjà actifs avant chaque lancement.

## Attribution

- architecture, contrats, dépendances : `architect`
- implémentation et correction : `coder`
- audit indépendant : `reviewer`
- scénarios et exécution de tests : `tester`

Ne lance pas plusieurs agents sur le même fichier en écriture.
