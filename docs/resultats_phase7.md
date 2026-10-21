# Phase 7 : mesures sur les décisions LLM (Ollama, CPU)

Machine : i5-1135G7, 7,7 Go de RAM, sans GPU dédié. Modèles : qwen2.5:1.5b-instruct et qwen2.5:3b (même famille, deux tailles).
Protocole : situations d'Ilse conçues à la main (5 puis 8 puis 9), chacune posée avec 4 ordres d'options, température 0.
Le hasard est un repère approximatif, pas une mesure.

## Résultats du banc d'essai

| Prompt | 1,5b | 3b | Hasard |
|---|---|---|---|
| Un choix parmi 4 lieux, choix puis raison | 7/20 | 6/20 | ~11/20 |
| Un choix parmi 4 lieux, raison puis choix | 9/20 | 11/20 | ~11/20 |
| Deux temps (sortir/rester, puis lieu), v1 | 26/32 | 16/32 | ~20/32 |
| v2 (consigne « pèse d'abord ») | 15/32 | non testé | ~20/32 |
| v3 (enjeux orientés, lieux annotés) | 22/36 | non testé | ~22/36 |
| v4 (enjeux équilibrés, lieux annotés) | 23/36 | non testé | ~22/36 |

Seuil fixé avant les essais : 90 %. Aucun résultat ne l'atteint.

## Simulation complète (prompt v1, 1,5b, Ilse seule en LLM, 25 tours, 4 graines)

- Touchés : règles 2,2 / LLM 2,0 (différence non interprétable).
- Tours à la Maison : règles 9,2 / LLM 3,2.
- Accord LLM/règles sur « Maison ou sortir » : 74/100, contre ~76 % attendu si les décisions étaient indépendantes.
- Décisions valides : 100/100. Latence moyenne : 6,0 s.

## Constats

- Le comportement suit la formulation des enjeux plus que la situation (v3 trop prudent, v4 jamais prudent).
- Un changement de prompt corrigeant un cas (Ilse malade) n'a pas été généralisé sur une situation non réglée.
- Reproductibilité : la graine 0 jouée deux fois a donné 0 puis 1 tour à la Maison pour Ilse.

## Limites

Situations conçues par nous, une seule famille de modèles, 4 graines, un seul agent LLM, un seul prompt final, bonne réponse définie par nous.

## Suites décidées

- Enregistrer chaque sortie du LLM dans le journal d'événements pour permettre un rejeu fidèle (phase 12).
- Tester le levier RAG (phase 8) avant de conclure sur l'apport du LLM.
