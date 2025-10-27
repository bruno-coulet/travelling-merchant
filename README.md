# travelling-merchant
Problème du Voyageur de Commerce (TSP), un défi mathématique et algorithmique consistant à trouver le chemin le plus court permettant de visiter un ensemble donné de villes une seule fois avant de revenir au point de départ. 


## 🐍 Projet Python avec uv

Ce projet utilise [uv](https://github.com/astral-sh/uv), un gestionnaire de dépendances rapide pour Python.  
Installation (si besoin) : `pip install uv` ou `pipx install uv`

Création et synchronisation de l’environnement :<br>
`uv sync`  

Activation :<br>
```shell
# sous macOS/Linux
source .venv/bin/activate
# sous windows
.venv\Scripts\Activate.ps1
```

Lancer le projet :<br>
```shell
uv run main.py
```

## modélisation, résolution et analyse comparative

1. Modélisation du Problème :
○ Récupération des positions géographiques de 20 villes
françaises
○ Représentation du réseau des villes et des routes de la carte de Théobald sous la forme d’un graphe.
Ici, les sommets représentent les villes et les arêtes représentent les
routes entre ces villes avec des distances associées.
○ Il faut utiliser la **distance de Haversine** <br>

2. Résolution avec l'Algorithme de Christofides :
○ Implémentation de l'**algorithme de Christofides** pour trouver l’itinéraire
le plus court pour Théobald.<br>
○ Quelle est la distance totale de la solution presque optimale ?<br>
Affichage de l'itinéraire sur la carte du marchand.
○ Explication des étapes de l'algorithme
○ Pourquoi cet algorithme est pertinent dans ce contexte.<br>

3. Résolution avec les Algorithmes Génétiques :
○ Implémentation d'un algorithme génétique pour trouver l’itinéraire le
plus court pour Théobald.<br>

On considère ici que les individus
étudiés sont les parcours différents (ou des Theobalds d’univers
parallèles).
○ Définissez les paramètres de l'algorithme : taille de la population,
système de sélection, système de reproduction, taux de mutation,
nombre de générations, etc.

○ Testez différentes configurations de l'algorithme génétique pour
observer comment elles affectent la qualité des solutions.
○ Quelle est la distance totale de votre solution presque optimale ?
Affichez l'itinéraire sur la carte du marchand.
4. Analyse comparative
○ Comparez la solution obtenue par l'algorithme génétique avec
celle obtenue par l'algorithme de Christofides , terme de distance
totale, du temps d’exécution de facilité d’implémentation et de
robustesse de solution.
○ Discutez des avantages et des inconvénients de chaque
approche dans le contexte spécifique de Théobald.
5. Conclusion
○ Proposez une recommandation sur la méthode la plus
appropriée pour Théobald en fonction de votre analyse
comparative.
