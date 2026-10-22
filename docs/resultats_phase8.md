# Phase 8 : RAG et documents fictifs

Machine : i5-1135G7, 7,7 Go de RAM, sans GPU dédié. Modèle de décision : qwen2.5:1.5b-instruct, prompt v1 figé.

## Corpus et récupération

- 24 documents fictifs (bulletins, communiqués, rumeurs, presse, témoignages, notes), avec identifiant, jour simulé, source et contenu.
  Les champs `verite` (vrai, faux, partiel) et `tags` servent uniquement à l'évaluation : les agents ne les voient jamais.
- Recherche lexicale BM25 en Python pur, avec filtre temporel (aucun document futur). Choix justifié par la taille du corpus et la mémoire disponible.
- Évaluation sur 11 questions, pertinence définie par des thèmes attribués par les auteurs : précision@3 = 0,82 ; rappel@3 = 0,88 ; 0 document futur retrouvé.
- Défaut observé : décalage de vocabulaire (« se transmet » contre « passe d'une personne à l'autre »), correspondances parasites entre racines proches.

## Dans la simulation (graine 0, 25 tours, Ilse seule avec RAG)

- 91 documents retrouvés pour 25 décisions : 88 pertinents, 15 faux, 22 partiels ; 13 décisions sur 25 exposées à au moins un document faux.
- Tours passés à la Maison par Ilse : sans RAG 1, avec RAG 18, règles 23 (une seule partie, indicatif).
- Raisons données par le modèle : 18 sur 25 font trois mots ou moins (« sortir »), donc inexploitables pour évaluer la pertinence.

## Ablation (8 situations x 4 ordres, 32 décisions par condition)

| Condition | Maison /32 | Puits /32 | Conformes /32 |
|---|---|---|---|
| sans documents | 4 | 1 | 26 |
| tous les documents retrouvés | 12 | 2 | 22 |
| documents vrais seulement | 32 | 0 | 20 |
| documents faux seulement | 18 | 2 | 14 |
| tous + confiance par source | 22 | 1 | 20 |
| vrais + confiance par source | 31 | 0 | 20 |

« Conformes » : bonnes réponses définies par nous, qui ne tiennent pas compte des documents.

## Constats

- Le contenu des documents modifie le comportement (vrais et faux n'ont pas le même effet) : ce n'est pas un effet de simple présence.
- Avec les documents fiables seuls, l'agent reste chez lui dans 8 situations sur 8, y compris en situation calme et pour l'agent sceptique : le conseil « restez chez vous en cas de fièvre » est appliqué à tous, le profil est ignoré.
- Avec tous les documents, l'agent devient moins prudent en épidémie grave (4/4 Maison sans documents, 0/4 avec) : exposition mesurée à la désinformation.
- Présenter la confiance de l'agent envers chaque source n'a pas rétabli de comportement dépendant de la situation (critères fixés avant l'essai non atteints).
- Le maillon faible est l'usage des documents par le petit modèle, pas la récupération.

## Limites

Un seul modèle, un seul prompt, corpus écrit par nous (plus propre que la réalité), pertinence définie par nos propres étiquettes, 8 situations, résultats non reproductibles à l'identique, confiance par source fondée sur une hypothèse de modélisation.

## Suite décidée

Phase 9 : faire passer les documents par les croyances de l'agent (règle transparente tenant compte de la confiance dans la source), puis laisser le modèle décider à partir de ses croyances mises à jour.
