# bibIA : Détecteur de bibliographies hallucinées

Une application web pour vérifier l'existence et la validité des références bibliographiques. bibIA est conçue pour aider à identifier les "bibliographies hallucinées", ces références qui semblent plausibles mais qui ont été générées par des modèles de langage (LLM).


## Fonctionnalités clés

  * **Analyse Intelligente** : Collez une bibliographie entière. bibIA la segmente automatiquement en entrées individuelles.
  * **Parsing Structuré** : Tente d'extraire les informations clés de chaque référence (auteur, année, titre, journal, DOI, etc.) en utilisant des patrons de reconnaissance (Regex) adaptés aux formats courants (livres, articles).
  * **Correction Interactive** : L'application vous présente les données extraites et vous permet de les corriger manuellement avant de lancer la vérification, assurant une meilleure précision.
  * **Vérification Multi-sources** : Chaque référence est vérifiée de manière asynchrone auprès de deux sources :
      * **Crossref** : Via son API officielle, pour une vérification fiable basée sur le DOI.
      * **Google Scholar** : Via un scraping intelligent pour trouver des correspondances sur le titre et l'auteur.
  * **Résultats Clairs et Détaillés** : Obtenez un résumé simple (✅ Trouvée, ❌ Non trouvée, ⚠️ Erreur) pour chaque entrée, avec la possibilité d'explorer les détails de la vérification pour chaque source.
  * **Gestion des Délais** : Choisissez un mode de requête ("Rapide", "Prudent", "Très Prudent") pour ajuster le délai entre les appels à Google Scholar, afin d'éviter les blocages d'IP tout en respectant leurs serveurs.

## Comment ça marche ? 

Le processus se déroule en trois grandes étapes gérées par l'interface Streamlit :

1.  **Parsing** (`src/parser.py`) : Le texte brut de la bibliographie est divisé en références. Pour chacune, le module de parsing tente d'appliquer plusieurs stratégies (d'abord pour un format "article", puis "livre") pour extraire les métadonnées. Si tout échoue, un analyseur de secours (`fallback`) récupère le maximum d'informations possible.
2.  **Validation par l'Utilisateur** (`app.py`) : Les données parsées sont affichées dans un formulaire. L'utilisateur peut corriger une erreur de détection (par exemple, un mauvais découpage du titre) avant de soumettre la vérification.
3.  **Vérification Asynchrone** (`src/verifier.py`) : Une fois les données validées, bibIA lance des tâches de vérification parallèles pour chaque référence. Chaque référence est soumise aux fournisseurs disponibles (Crossref si un DOI est présent, et Google Scholar). Les résultats sont ensuite agrégés et affichés.

## Installation et lancement

Pour faire fonctionner bibIA sur votre machine locale, suivez ces étapes.

### Prérequis

  * Python 3.7 ou une version ultérieure.
  * `pip` pour l'installation des paquets.

### Étapes

1.  **Clonez le dépôt :**

    ```bash
    git clone https://github.com/SeidSmatti/bibIA.git
    cd bibIA
    ```

2.  **Créez un environnement virtuel (recommandé) :**

      * Sur macOS / Linux :
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
      * Sur Windows :
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Installez les dépendances :**
    Le fichier `requirements.txt` contient toutes les bibliothèques nécessaires.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancez l'application Streamlit :**

    ```bash
    streamlit run app.py
    ```

Votre navigateur web devrait s'ouvrir automatiquement sur la page de l'application (généralement `http://localhost:8501`).

##  Guide d'utilisation

L'interface est conçue pour être simple et intuitive :

1.  **Collez votre bibliographie** dans la zone de texte principale. Assurez-vous de séparer chaque référence par au moins une ligne vide.
2.  Cliquez sur le bouton **"Analyser la bibliographie"**. bibIA va traiter le texte et afficher le nombre d'entrées détectées.
3.  **Validez et corrigez** les champs extraits pour chaque entrée. C'est une étape cruciale : si le titre ou l'auteur a été mal détecté, la vérification échouera.
4.  **Choisissez un délai** pour les requêtes. Le mode "Prudent (Défaut)" est recommandé pour un usage normal.
5.  Cliquez sur **"Vérifier toutes les références"** pour lancer le processus. Une barre de progression vous informera de l'avancement.
6.  **Analysez les résultats**. Chaque entrée sera marquée comme trouvée ou non, et vous pourrez déplier les détails pour voir quelle source a permis la vérification.

## Structure du repo

```
.
├── app.py                  # Fichier principal de l'application Streamlit
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
└── src/
    ├── __init__.py         # Rend 'src' un module Python
    ├── config.py           # Constantes et configuration (URLs, Headers, Délais)
    ├── parser.py           # Logique de parsing des chaînes bibliographiques
    └── verifier.py         # Logique de vérification auprès des sources externes (Crossref, Scholar)
```

## Déploiement

Cette application est basée sur Streamlit et peut être déployée gratuitement sur le **Streamlit Community Cloud**. Pour ce faire :

1.  Poussez ce projet sur un dépôt GitHub public.
2.  Créez un compte sur [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Liez votre compte GitHub et déployez le dépôt en quelques clics. Streamlit s'occupera automatiquement d'installer les dépendances listées dans `requirements.txt`.

##  Contribuer

Les contributions sont les bienvenues \! Que ce soit pour signaler un bug, proposer une nouvelle fonctionnalité (comme l'ajout d'une nouvelle source de vérification) ou améliorer le parsing, n'hésitez pas à ouvrir une *issue* ou une *pull request*.

## 📄 Licence
Ce projet est distribué sous la licence GNU General Public License version 3 (GPLv3). Voir le fichier `LICENSE` pour plus de détails.

