# Ecole 2600 - Maths - Projet 2 - Turingtoy

L'objectif de ce projet est d'implémenter un interpreteur de machines de Turing.

# Mise en place

Ce projet nécessite l'installation de [poetry](https://python-poetry.org/), un outil de gestion de dépendance python plus haut niveau que `pip`.

Vous pouvez suivre la documentation pour installer poetry: [Introduction | Documentation | Poetry - Python dependency management and packaging made easy](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) ⏳ 4m

Après installation, placez vous dans le repertoire du projet et lancez la commande suivante:

```bash
poetry install
```

Vous pouvez ensuite activer le script `.devenv/bash_init.sh` pour activer l'environnement virtuel python du projet:

```bash
source .devenv/bash_init.sh
```

Le projet implémente des tests dans `tests/tests_turing.py` qui doivent passer après votre implémentation. Vous pouvez lancer les tests de deux manières:

- Simplement via la commande `pytest`
- Ou via le runner nox: `nox -s tests`. Cette méthode est utilisé pour la CI gitlab et lancer également un test de coverage qui doit passer à 100% après votre implémentation. Il vous faudra probablement rajouter des tests pour couvrir à 100% votre code.

# Instructions

Les tests de `tests/test_turing.py` donne des informations sur la fonction à implémenter et le format de données.

La fonction à implémenter dans le fichier `src/turingtoy/__init__.py` à la signature suivante:

```python
def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]
```

La machine de turing est donc représenter par un dictionnaire donc le format est décrit plus bas. Vous pouvez également voir des exemples définis dans les tests, ou en json dans les fichiers sous le dossier `tests/data`.

L'input contient une chaine représentant le contenu de la bande en début d'execution, et la variable `steps` optionelle indique un nombre maximal de transitions à effectuer. Si non spécifié la machine doit être executé jusqu'a blockage, acceptation ou bien tourner à l'infini.

La fonction doit renvoyer un tuple de 3 valeurs:

- Une chaine représentant l'état de la bande en sortie, c'est l'output. Il faudra retirer les symboles vide en début et fin de chaine avant de renvoyer la valeur.
- Un historique d'execution indiquant les états parcourus par la machine et les décisions prise. Vous pouvez consulter les json sous `tests/data` qui donne l'historique d'execution attendu par chaque test.
- Un boolean indiquant si la machine s'est arretée dans un état final (`true`) ou s'est bloqué (`false`, lorsque la machine arrive dans un état qui ne lui permet plus de continuer, sans transition sortante mais non final).

# Format des données

## Machines de Turing

Le format de représentation des MT choisit est similaire à celui utilisé par https://turingmachine.io/ mais exprimé en json (dict en python).

Les champs du dictionnaire sont:

- `blank`: un caractère représentant le symbole vide
- `start state`: une string indiquant l'état initial
- `final states`: une liste de string indiquant les états finaux
- `table`: un dictionnaire représentant la table de transition. Chaque clef est le nom d'un état, et chaque valeur est un dictionnaire.

Le dict associé à un état donne pour chaque symbole lu les instructions à effectuer. Une instruction pour être représentée de deux manière:

- Une chaine `"R"` ou `"L"`, dans ce cas la machine doit simplement aller à droite ou à gauche, sans changer d'état ni rien écrire sur la bande.
- Un dict contenant les champs suivants
  - `write`: un caractère à écrire sur la bande (optional, si non spécifié la machine ne doit rien écrire et laisser le caractère lu)
  - un champs `R` ou `L`: spécifie si la machine doit aller à droite ou à gauche, et indique l'état dans lequel se placer.

Dans les tests, ou utilise une fonction utilitaire `to_dict` pour facilement donner le même comportement à plusieurs états.

Prenons l'exemple suivant, contenu dans la table de la machine du test `test_turing_machine_add_two_binary_numbers`:

```python
"rewrite": {
    "O": {"write": "0", "L": "rewrite"},
    "I": {"write": "1", "L": "rewrite"},
    **to_dict(["0", "1"], "L"),
    " ": {"R": "done"},
},
```

Cette définition indique que si la machine est dans l'état `rewrite`:

- Si elle lit le symbole `O`, elle doit écrire `0`, aller à gauche et se placer dans l'état `rewrite` (ne change pas d'état donc).
- Si elle lit le symbole `I`, elle doit écrire `1`, aller à gauche et se placer dans l'état `rewrite` (ne change pas d'état donc).
- Si elle lit le symbole `0` ou `1`, elle doit simplement aller à gauche sans changer d'état.
- Si elle lit le symbole ` `, elle doit aller à droite et se placer dans l'état `done`.

## Historique d'execution

L'historique d'execution est simplement une liste de dictionnaire contenant les champs suivants:

- `state`: état courant
- `reading`: ce que la machine lit
- `position`: la position de la machine sur le ruban (relatif au champs `memory`)
- `memory`: l'état actuel du ruban (avec symboles vide à gauche et à droite, contrairement à l'output de la machine qui doit être renvoyé)
- `transition`: la transition choisit dans la table (une string ou un dict donc) pour choisir le prochain état et le symbole à écrire.

Un invariant de cette representation doit être `memory[position] == reading`
