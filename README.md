# Veille H/R — Groupe Shaman

Dashboard de veille sectorielle hôtellerie-restauration, accessible depuis n'importe quel navigateur via GitHub Pages.

---

## Installation (10 minutes)

### Étape 1 — Créer le repo GitHub

1. Va sur [github.com](https://github.com) et connecte-toi
2. Clique sur **New repository**
3. Nomme-le `veille-hr` (ou ce que tu veux)
4. Coche **Public** (obligatoire pour GitHub Pages gratuit)
5. Clique **Create repository**

---

### Étape 2 — Uploader les fichiers

Dans le repo créé, clique **uploading an existing file** et uploade dans cet ordre :

```
index.html
fetch_feed.py
.github/workflows/fetch-feed.yml
```

Pour le dossier `.github/workflows/`, clique **Add file > Create new file**, tape le chemin `.github/workflows/fetch-feed.yml` dans le nom, et colle le contenu du fichier.

---

### Étape 3 — Activer GitHub Pages

1. Dans ton repo, va dans **Settings > Pages**
2. Source : **Deploy from a branch**
3. Branch : **main** / dossier **/ (root)**
4. Clique **Save**

Ton dashboard sera accessible à :
`https://TON-USERNAME.github.io/veille-hr/`

---

### Étape 4 — Générer le premier feed.json

**Option A — Via GitHub Actions (recommandé)**
1. Va dans l'onglet **Actions** du repo
2. Clique sur **Actualisation veille H/R**
3. Clique **Run workflow > Run workflow**
4. Attends ~1 minute
5. Rafraîchis le dashboard

**Option B — En local**
```bash
pip install feedparser
python fetch_feed.py
# Commit et push le feed.json généré
git add feed.json
git commit -m "feed initial"
git push
```

---

## Fonctionnement automatique

Le script tourne **chaque matin à 6h UTC (7h heure Paris)** via GitHub Actions.
Il récupère les dernières actualités de toutes les sources, génère un `feed.json` et le commit automatiquement.

Le dashboard lit ce fichier à chaque ouverture.

---

## Sources surveillées

| Catégorie | Sources |
|-----------|---------|
| France H/R | L'Hôtellerie Restauration, Néo Restauration |
| Luxe & lifestyle | Le Figaro Gastronomie, Relais & Châteaux |
| International | Skift, Hospitality Net |
| Pays de la Loire | Google News (hôtel luxe PDL, château Nantes, resto gastro Angers/Nantes, tourisme Vendée, hôtellerie Loire-Atlantique) |
| Tendances | Google News (slow tourism, hôtellerie luxe France, Michelin, séminaire luxe) |
| Concurrents | Google News (Fontenille, Cheval Blanc, Airelles, châteaux Loire) |
| Auto-veille Shaman | Google News (Château du Portereau, Château de Noirieux, L'Attilio) |
| International luxe | Google News (luxury hotel innovation, Mandarin Oriental) |

---

## Ajouter ou modifier des sources

Ouvre `fetch_feed.py` et modifie le tableau `SOURCES`.
Chaque source a :
- `url` : l'URL du flux RSS ou Google News
- `source` : nom affiché dans le dashboard
- `geo` : `france`, `europe` ou `international`
- `geo_label` : libellé affiché sur la carte

Pour créer un flux Google News personnalisé :
`https://news.google.com/rss/search?q=MOT+CLE&hl=fr&gl=FR&ceid=FR:fr`

---

## Structure du projet

```
veille-hr/
├── index.html              Dashboard (ouvrir dans le navigateur)
├── fetch_feed.py           Script de collecte RSS
├── feed.json               Données générées (auto-commit)
├── README.md               Ce fichier
└── .github/
    └── workflows/
        └── fetch-feed.yml  Automatisation quotidienne
```
