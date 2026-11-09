# Gestion du contexte

## Principe

Un subagent démarre dans un contexte isolé et ne reçoit pas l'historique complet de la conversation principale. Le prompt de délégation doit donc contenir tout ce qui est nécessaire à sa mission.

## À transmettre

- objectif global utile à la mission ;
- objectif et identifiant de la mission ;
- contexte technique vérifié ;
- décisions déjà prises et raisons ;
- fichiers et symboles concernés ;
- dépendances et leurs résultats ;
- contraintes et actions interdites ;
- livrables et critères d'acceptation ;
- hypothèses et inconnues pertinentes.

## À ne pas transmettre

- historique complet de conversation ;
- détails sans rapport ;
- suppositions présentées comme faits ;
- rapports volumineux lorsqu'un résumé et des chemins suffisent.

## Étiquettes de preuve

- `CONFIRMED` : directement vérifié dans le dépôt ou par une commande.
- `ASSUMED` : hypothèse de travail explicitement non vérifiée.
- `UNKNOWN` : information non disponible.
- `REJECTED` : hypothèse examinée et écartée, avec raison.

La répétition d'une hypothèse par plusieurs agents ne la transforme pas en fait.
