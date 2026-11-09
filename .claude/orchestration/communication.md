# Protocole de communication

## Canal

Les subagents classiques retournent leur résultat à l'orchestrateur qui les a lancés. Dans cette équipe, les spécialistes ne se contactent pas directement. L'orchestrateur transmet les informations pertinentes d'une mission à l'autre.

Ne suppose jamais qu'un subagent connaît l'historique de la session principale ou les résultats d'un autre subagent.

## Types de message

Les échanges doivent utiliser les structures JSON de `.orchestration/templates/` lorsque c'est pertinent :

- `MISSION` : contrat envoyé par l'orchestrateur.
- `REPORT` : résultat retourné par un spécialiste.
- `DELEGATION_REQUEST` : demande d'une sous-mission.
- `BLOCKER` : obstacle empêchant de progresser.
- `DECISION` : décision prise par l'orchestrateur.
- `REVIEW` : verdict du relecteur ou du testeur.

Ces types sont des conventions de contenu, pas des outils de messagerie ou des fonctions Claude Code.

## Règles

1. Un message porte un identifiant de mission.
2. Les faits, hypothèses et inconnues sont explicitement séparés.
3. Les chemins de fichiers sont relatifs à la racine du dépôt.
4. Les résultats de commandes incluent la commande et son statut de sortie lorsque disponible.
5. Les rapports sont concis, mais autonomes.
6. Les informations nécessaires à la mission suivante sont reprises dans son prompt ; ne transmets pas toute la conversation.
7. Une décision importante est inscrite dans le registre par l'orchestrateur.
8. Une demande de délégation n'est pas une délégation autorisée.
