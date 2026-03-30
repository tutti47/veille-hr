import feedparser
import json
import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

SOURCES = [
    # France H/R généraliste
    {"url": "https://www.lhotellerie-restauration.fr/rss/actualites.xml", "source": "L'Hôtellerie Restauration", "geo": "france", "geo_label": "France"},
    {"url": "https://www.neorestauration.com/rss/", "source": "Néo Restauration", "geo": "france", "geo_label": "France"},
    # Luxe & lifestyle
    {"url": "https://www.lefigaro.fr/rss/figaro_gastronomie.xml", "source": "Le Figaro Gastronomie", "geo": "france", "geo_label": "France"},
    {"url": "https://www.relaischateaux.com/fr/rss", "source": "Relais & Châteaux", "geo": "france", "geo_label": "France"},
    # International
    {"url": "https://skift.com/feed/", "source": "Skift", "geo": "international", "geo_label": "International"},
    {"url": "https://www.hospitalitynet.org/rss/", "source": "Hospitality Net", "geo": "international", "geo_label": "International"},
    # Google News — Pays de la Loire luxe
    {"url": "https://news.google.com/rss/search?q=h%C3%B4tel+luxe+Pays+de+la+Loire&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Pays de la Loire"},
    {"url": "https://news.google.com/rss/search?q=ch%C3%A2teau+h%C3%B4tel+Nantes&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Loire-Atlantique"},
    {"url": "https://news.google.com/rss/search?q=restaurant+gastronomique+Angers+Nantes&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Anjou / Nantes"},
    {"url": "https://news.google.com/rss/search?q=tourisme+luxe+Vend%C3%A9e&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Vendée"},
    {"url": "https://news.google.com/rss/search?q=h%C3%B4tellerie+Loire-Atlantique&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Loire-Atlantique"},
    # Google News — Tendances & Luxe
    {"url": "https://news.google.com/rss/search?q=slow+tourism+France+luxe&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=h%C3%B4tellerie+luxe+France&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=gastronomie+Michelin+France&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=s%C3%A9minaire+luxe+ch%C3%A2teau+France&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    # Google News — Concurrents
    {"url": "https://news.google.com/rss/search?q=Fontenille+Collection&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=Cheval+Blanc+h%C3%B4tel&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=Airelles+h%C3%B4tel&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    {"url": "https://news.google.com/rss/search?q=ch%C3%A2teau+h%C3%B4tel+luxe+Loire&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "europe", "geo_label": "Val de Loire"},
    # Google News — Groupe Shaman (auto-veille)
    {"url": "https://news.google.com/rss/search?q=%22Ch%C3%A2teau+du+Portereau%22&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Vertou"},
    {"url": "https://news.google.com/rss/search?q=%22Ch%C3%A2teau+de+Noirieux%22&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "Briollay"},
    {"url": "https://news.google.com/rss/search?q=%22L%27Attilio%22&hl=fr&gl=FR&ceid=FR:fr", "source": "Google News", "geo": "france", "geo_label": "France"},
    # International tendances
    {"url": "https://news.google.com/rss/search?q=luxury+hotel+innovation+2026&hl=en&gl=US&ceid=US:en", "source": "Google News", "geo": "international", "geo_label": "International"},
    {"url": "https://news.google.com/rss/search?q=Mandarin+Oriental+news&hl=en&gl=US&ceid=US:en", "source": "Google News", "geo": "international", "geo_label": "International"},
]

ALERT_KEYWORDS = [
    "pays de la loire", "loire-atlantique", "nantes", "vertou", "angers", "briollay",
    "fontenille", "cheval blanc", "airelles", "ouverture", "acquisition", "michelin",
    "château du portereau", "château de noirieux", "l'attilio", "slow tourism",
    "orangerie", "séminaire luxe", "guinguette", "revpar", "taux remplissage"
]

CAT_KEYWORDS = {
    "concurrence": ["fontenille", "cheval blanc", "airelles", "le barn", "six senses", "aman", "mandarin", "relais & châteaux", "acquisition", "rachat", "concurrent"],
    "ouverture": ["ouvre", "ouverture", "inauguration", "lancement", "nouveau", "opening", "open"],
    "gastronomie": ["michelin", "gastronomie", "chef", "étoile", "restaurant", "cuisine", "table", "menu", "recette"],
    "mice": ["séminaire", "mariage", "événement", "mice", "orangerie", "convention", "conférence", "corporate", "b2b"],
    "innovation": ["innovation", "concept", "nouveau format", "technologie", "ia", "digital", "experience", "immersif"],
    "tendance": ["tendance", "revpar", "taux", "marché", "croissance", "étude", "rapport", "analyse", "slow tourism", "luxe discret"],
}

def guess_category(title, summary):
    text = (title + " " + summary).lower()
    for cat, keywords in CAT_KEYWORDS.items():
        if any(k in text for k in keywords):
            return cat
    return "tendance"

def is_alert(title, summary):
    text = (title + " " + summary).lower()
    return any(k in text for k in ALERT_KEYWORDS)

def parse_date(entry):
    try:
        if hasattr(entry, "published"):
            dt = parsedate_to_datetime(entry.published)
            return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()

def relative_date(iso):
    try:
        dt = datetime.fromisoformat(iso)
        now = datetime.now(timezone.utc)
        diff = now - dt
        days = diff.days
        hours = diff.seconds // 3600
        if days == 0:
            return f"Il y a {hours}h" if hours > 0 else "À l'instant"
        elif days == 1:
            return "Il y a 1 j"
        elif days < 7:
            return f"Il y a {days} j"
        else:
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return ""

def fetch_all():
    items = []
    seen = set()
    for src in SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            for entry in feed.entries[:8]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Clean HTML from summary
                import re
                summary = re.sub(r"<[^>]+>", "", summary)[:280]
                if not title or not link:
                    continue
                uid = hashlib.md5(link.encode()).hexdigest()
                if uid in seen:
                    continue
                seen.add(uid)
                iso_date = parse_date(entry)
                items.append({
                    "id": uid,
                    "title": title,
                    "source": src["source"],
                    "link": link,
                    "excerpt": summary,
                    "cat": guess_category(title, summary),
                    "geo": src["geo"],
                    "geo_label": src["geo_label"],
                    "date": relative_date(iso_date),
                    "iso_date": iso_date,
                    "alert": is_alert(title, summary),
                })
        except Exception as e:
            print(f"Erreur source {src['url']}: {e}")
    # Sort by date desc
    items.sort(key=lambda x: x.get("iso_date", ""), reverse=True)
    # Keep max 120 items
    items = items[:120]
    return items

if __name__ == "__main__":
    items = fetch_all()
    with open("feed.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(), "items": items}, f, ensure_ascii=False, indent=2)
    print(f"feed.json généré — {len(items)} signaux")
