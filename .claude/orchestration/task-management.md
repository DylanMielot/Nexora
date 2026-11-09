# Gestion des missions et registre

## Source de vérité

`.orchestration/registry.json` est le registre de l'exécution courante. L'orchestrateur est son seul rédacteur. Les subagents retournent leurs rapports ; ils ne mettent pas à jour le registre.

## États autorisés

- `PENDING` : créée, non attribuée.
- `ASSIGNED` : attribuée, pas encore démarrée.
- `IN_PROGRESS` : en cours.
- `BLOCKED` : en attente d'une décision ou dépendance.
- `REVIEW` : revue en cours.
- `TESTING` : tests en cours.
- `COMPLETED` : livrables et critères vérifiés.
- `FAILED` : échec après analyse.
- `CANCELLED` : annulée par l'orchestrateur.

## Identifiants et dépendances

- Identifiants séquentiels : `T001`, `T002`, etc.
- Mission enfant : `parent_id` égal à la mission qui a demandé la délégation.
- Les dépendances référencent des identifiants existants.
- Ne démarre pas une mission tant que ses dépendances ne sont pas satisfaites.

## Écriture sûre

- Lire le registre avant chaque modification.
- Préserver les missions et décisions déjà enregistrées.
- Écrire un JSON strict, sans commentaires ni virgule finale.
- Mettre à jour le statut après les événements importants.
- Ne pas stocker les conversations ou chaînes de raisonnement ; uniquement les décisions, statuts, résumés et références utiles.
- Ne pas utiliser `active_agents` comme compteur faisant autorité si l'état réel des agents Claude Code est disponible ; le registre est un suivi de projet, pas un moniteur d'exécution temps réel.

## Conflits de fichiers

Attribuer un propriétaire d'écriture par fichier de production. Les missions qui écrivent dans le même fichier sont séquencées. Les missions de lecture peuvent être parallèles avec prudence.
