# Contrôle qualité

## Niveaux de contrôle

Adapte le niveau de contrôle au risque :

- faible : vérification ciblée par le codeur, test pertinent si disponible ;
- moyen : testeur ou relecture selon la nature du changement ;
- élevé : relecteur et testeur indépendants après implémentation ;
- sécurité, données, authentification ou changements transversaux : revue et tests obligatoires sauf justification explicite.

## Revue

Le relecteur est en lecture seule. Il retourne `approved` ou `changes_requested`, avec des constats vérifiables et classés par gravité.

Un constat `critical` ou `high` bloque la livraison.

## Tests

Le testeur rapporte les commandes réellement exécutées et les résultats. `not_run` ne signifie pas `passed`. Un test flaky, bloqué par l'environnement ou partiellement exécuté doit être signalé.

## Corrections

- Le codeur corrige les défauts qui lui sont attribués.
- Après correction, relancer uniquement les validations pertinentes, puis la suite de régression appropriée.
- Deux cycles de correction automatiques maximum.
- Au-delà, arrêter, résumer le blocage et demander une décision ou proposer une approche alternative.

## Validation finale

L'orchestrateur vérifie les rapports, le diff, les critères d'acceptation et les limites connues. Il est le seul à prononcer la livraison.
