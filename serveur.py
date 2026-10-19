"""Pari Foot — l'application des pronostics de José Ledanite.

CE QUE C'EST. La face visible du bot de football : les analyses du jour et la montante, dans une
application qu'on installe sur son téléphone (menu ⋮ du navigateur → « Ajouter à l'écran d'accueil »).

D'OÙ VIENNENT LES CHIFFRES, ET POURQUOI CE SERVEUR NE CALCULE RIEN. Les cotes viennent de
m.betclic.ci, un site ivoirien : la récolte et le calcul se font sur le téléphone de José, là où ça
fonctionne. Cette application ne fait qu'AFFICHER un instantané (publication.json) fabriqué là-bas.
Séparer les deux, c'est ce qui permet à l'application d'être simple, rapide et impossible à casser
depuis l'extérieur : elle n'a aucun accès, aucune clé, aucune donnée personnelle.

⚠️ AUCUNE DONNÉE DE CLIENT ICI. On publie des matchs, des pourcentages et des cotes. Jamais un nom,
jamais un identifiant Telegram, jamais une mise. Un instantané publié doit pouvoir être lu par
n'importe qui sans rien révéler de qui que ce soit.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import articles  # les GUIDES écrits (contenu SEO), avec leur lien d'affiliation en un seul endroit
import trafic    # le compteur de visites (sobre : sans cookie, sans adresse IP)

ICI = os.path.dirname(os.path.abspath(__file__))
LECTURE_VERTE, LECTURE_VERTE_FORTE = "#16a34a", "#15803d"

STYLE = """:root{
  --ink:#161513; --muted:#6d6a63; --line:#e7e1d5; --bg:#fffdf8; --card:#ffffff;
  --accent:#d9a900; --accent-soft:#fff4cc;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:17px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
img{max-width:100%;display:block}
a{color:var(--ink)}
.wrap{max-width:748px;margin:0 auto;padding:0 20px}

/* ── en-tête ───────────────────────────────────────────── */
header.site{position:sticky;top:0;z-index:10;background:rgba(255,253,248,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.marque{font-family:Georgia,"Times New Roman",serif;font-size:22px;font-weight:700;
  letter-spacing:-.02em;text-decoration:none}
.marque span{color:var(--muted);font-weight:400}
header.site nav a{color:var(--muted);text-decoration:none;font-size:14px;margin-left:20px}
header.site nav a:hover{color:var(--ink)}

/* ── une du blog ───────────────────────────────────────── */
.une{display:block;text-decoration:none;margin:34px 0 10px}
.une .visuel{position:relative;border-radius:14px;overflow:hidden;background:#efe9dc;aspect-ratio:16/9}
.une .visuel img{width:100%;height:100%;object-fit:cover}
.etiquette{display:inline-block;background:var(--accent-soft);color:#6b5200;font-size:12px;
  font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:6px 10px;border-radius:999px}
.une h2{font-family:Georgia,"Times New Roman",serif;font-size:clamp(26px,6vw,38px);line-height:1.15;
  letter-spacing:-.02em;margin:14px 0 8px}
.une p{color:var(--muted);margin:0 0 10px}
.meta{font-size:13.5px;color:var(--muted)}
.meta b{color:var(--ink);font-weight:600}

/* ── liste des articles ────────────────────────────────── */
.titre-section{display:flex;align-items:center;gap:14px;margin:42px 0 6px}
.titre-section h2{font-family:Georgia,serif;font-size:15px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin:0;white-space:nowrap}
.titre-section i{flex:1;height:1px;background:var(--line)}
.liste{display:flex;flex-direction:column}
.carte{display:flex;gap:18px;padding:22px 0;border-bottom:1px solid var(--line);text-decoration:none}
.carte:last-child{border-bottom:0}
.carte .vignette{flex:0 0 132px;height:96px;border-radius:10px;overflow:hidden;background:#efe9dc}
.carte .vignette img{width:100%;height:100%;object-fit:cover}
.carte h3{font-family:Georgia,serif;font-size:19px;line-height:1.25;margin:0 0 6px;letter-spacing:-.01em}
.carte p{color:var(--muted);font-size:14.5px;margin:0 0 8px;display:-webkit-box;
  -webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.carte:hover h3{text-decoration:underline;text-underline-offset:3px}

/* ── article ───────────────────────────────────────────── */
.fil{font-size:13px;color:var(--muted);margin:22px 0 0}
.fil a{color:var(--muted);text-decoration:none}
.article h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(29px,7vw,44px);
  line-height:1.12;letter-spacing:-.025em;margin:14px 0 12px}
.article .chapeau{font-size:19.5px;line-height:1.5;color:#3d3a35;margin:0 0 18px}
.article .entete-meta{display:flex;align-items:center;gap:10px;padding:14px 0;border-top:1px solid var(--line);
  border-bottom:1px solid var(--line);margin-bottom:26px}
.article .entete-meta img{width:34px;height:34px;border-radius:50%;object-fit:cover}
.article .entete-meta span{font-size:13.5px;color:var(--muted)}
.article .hero{border-radius:14px;overflow:hidden;margin:0 0 30px;background:#efe9dc}
.article .hero img{width:100%;height:auto}
.article h2{font-family:Georgia,serif;font-size:26px;line-height:1.25;letter-spacing:-.015em;margin:38px 0 12px}
.article h3{font-size:19px;margin:26px 0 8px}
.article p{margin:0 0 18px}
.article ul,.article ol{margin:0 0 20px;padding-left:22px}
.article li{margin:0 0 9px}
.article a.lien-affilie,.article a{color:#8a6b00;text-decoration:underline;text-underline-offset:2px}
.article .divulgation{background:#f6f2e6;border-left:3px solid var(--accent);padding:14px 16px;
  font-size:14px;color:#4a463d;border-radius:0 8px 8px 0;margin:0 0 24px}
.article blockquote{margin:26px 0;padding:4px 0 4px 20px;border-left:3px solid var(--line);
  font-family:Georgia,serif;font-size:20px;color:#3d3a35}
.article table{width:100%;border-collapse:collapse;margin:0 0 22px;font-size:15px}
.article th,.article td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}

/* ── encart auteur / partage ───────────────────────────── */
.encart{display:flex;gap:16px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
  border-radius:14px;padding:20px;margin:40px 0 26px}
.encart img{width:56px;height:56px;border-radius:50%;object-fit:cover;flex:0 0 auto}
.encart b{display:block;font-size:15px}
.encart p{font-size:14.5px;color:var(--muted);margin:4px 0 0}
.partage{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:18px 0;border-top:1px solid var(--line)}
.partage span{font-size:13px;color:var(--muted);margin-right:4px}
.partage a,.partage button{font-size:13.5px;text-decoration:none;color:var(--ink);border:1px solid var(--line);
  background:var(--card);padding:8px 13px;border-radius:999px;cursor:pointer;font-family:inherit}
.partage a:hover,.partage button:hover{border-color:var(--ink)}

/* ── pied ──────────────────────────────────────────────── */
footer.pied{margin-top:50px;border-top:1px solid var(--line);padding:28px 0 42px;
  font-size:14px;color:var(--muted)}
footer.pied .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
footer.pied a{color:var(--muted)}


/* ── couverture 3D du livre blanc ──────────────────────── */
.ebook{perspective:1100px;display:flex;justify-content:center;margin:14px 0 30px}
.ebook .livre{position:relative;width:212px;height:292px;padding:22px 18px 18px;
  transform:rotateY(-21deg) rotateX(4deg);transform-style:preserve-3d;
  background:linear-gradient(135deg,#0f2b46 0%,#1e5f8a 52%,#0b1f33 100%);
  color:#fff;border-radius:3px 8px 8px 3px;
  box-shadow:26px 24px 44px -18px rgba(10,25,40,.55), 0 2px 0 rgba(255,255,255,.15) inset;
  display:flex;flex-direction:column;justify-content:space-between}
.ebook .livre::before{content:"";position:absolute;left:0;top:0;bottom:0;width:15px;
  background:linear-gradient(90deg,rgba(0,0,0,.5),rgba(255,255,255,.14));border-radius:3px 0 0 3px}
.ebook .livre::after{content:"";position:absolute;right:-7px;top:4px;bottom:4px;width:7px;
  background:linear-gradient(90deg,#e8eef5,#c9d3de);transform:rotateY(90deg);transform-origin:left}
.ebook .haut small{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;opacity:.8}
.ebook .haut h3{font-family:Georgia,serif;font-size:24px;line-height:1.14;margin:10px 0 0;letter-spacing:-.02em}
.ebook .bas{font-size:11.5px;opacity:.85;border-top:1px solid rgba(255,255,255,.25);padding-top:9px}
.ebook .badge-3d{position:absolute;top:10px;right:10px}

/* ── formulaire de capture ─────────────────────────────── */
.capture{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 10px}
.capture input[type=email]{flex:1 1 220px;padding:13px 15px;border:1px solid var(--line);
  border-radius:10px;font:inherit;background:#fff}
.capture input[type=email]:focus{outline:2px solid var(--accent);outline-offset:1px}
.capture button{flex:0 0 auto;padding:13px 20px;border:0;border-radius:10px;cursor:pointer;
  background:var(--ink);color:#fff;font:inherit;font-weight:600}
.capture button:hover{background:#000}
.capture-note{font-size:12.5px;color:var(--muted);margin:0 0 22px}

@media (max-width:520px){
  .carte{gap:14px}
  .carte .vignette{flex-basis:96px;height:80px}
  .carte h3{font-size:17px}
  .carte p{display:none}
}
"""


def lire_publication():
    try:
        with open(os.path.join(ICI, "publication.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _joli(texte):
    """Le texte du bot -> du HTML lisible. On ÉCHAPPE d'abord, on met en forme ensuite.

    ⚠️ L'ÉCHAPPEMENT D'ABORD N'EST PAS UN DÉTAIL : les analyses contiennent des noms d'équipes et de
    compétitions qui viennent de sources extérieures. Un « < » non échappé casserait la page.
    """
    protege = html.escape(str(texte or ""))
    protege = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", protege)
    protege = re.sub(r"(━━+)", r'<span class="trait">\1</span>', protege)
    return protege


def _quand_ou_direct(fiche):
    """L'heure du coup d'envoi, ou la mention « en direct ».

    ⚠️ POURQUOI C'EST ICI : José a demandé « ce sont les matchs à venir pour aujourd'hui ? ». La
    réponse est oui — le bot refuse d'analyser un match commencé — mais le montrer vaut mieux que le
    dire. Et si un match a commencé entre-temps, autant l'écrire franchement.
    """
    if fiche.get("en_direct"):
        return "🔴 En direct en ce moment — trop tard pour ce match"
    brut = fiche.get("coup_envoi") or ""
    if not brut:
        return ""
    try:
        quand = datetime.fromisoformat(brut)
        return "🕐 Coup d'envoi à " + quand.astimezone().strftime("%Hh%M")
    except (ValueError, TypeError):
        return ""


def _carte_message(m):
    """UNE CARTE = LE MESSAGE DU BOT, MOT POUR MOT.

    ⛔ LEÇON DU 10/10/2026. José : « Je veux que ce soit exactement comme avec le bot. Et je veux pas
    l'histoire des analyses. Non ! Fais comme exactement avec le bot. » Avant, cette fonction
    reconstruisait un joli résumé à partir d'un fichier intermédiaire : d'autres mots, un autre ordre,
    une section « pour le plaisir » qu'il n'avait jamais demandée, et PAS les scores les plus
    probables que le bot donne toujours. C'était une deuxième vérité avec les mêmes chiffres.
    Maintenant on affiche le texte que le moteur du bot a produit. Il ne peut plus y avoir d'écart.
    """
    quand = _quand_ou_direct(m)
    pied = f'<p class="quand2">{quand}</p>' if quand else ""
    return f'<div class="message">{_joli(m.get("message"))}{pied}</div>' 


def _coherent(paris):
    """⛔ LA RÈGLE DE JOSÉ : jamais un « plus de buts » ET un « under » sur le MÊME match.

    Quand les deux sortent, on garde l'under seul (décision du propriétaire, appliquée aussi dans le
    bot). Sans ce filtre, l'application afficherait un conseil qui se contredit lui-même.
    """
    a_under = any("UNDER" in (p.get("libelle") or "").upper() for p in paris)
    if not a_under:
        return paris
    return [p for p in paris
            if "UNDER" in (p.get("libelle") or "").upper()
            or not any(mot in (p.get("libelle") or "").upper()
                       for mot in ("PLUS DE", "+1,5", "+2,5", "PLUS DE BUTS"))]


def _carte_match(m):
    paris = _coherent(m.get("paris") or [])
    lignes = []
    for p in paris:
        pc = p.get("pourcent")
        largeur = max(2, min(100, int(pc))) if isinstance(pc, (int, float)) else 0
        lignes.append(
            f'<div class="pari"><span class="nom">{html.escape(str(p.get("libelle", "")))}</span>'
            f'<span class="barre"><i style="width:{largeur}%"></i></span>'
            f'<span class="pc">{pc:g} %</span>' if isinstance(pc, (int, float)) else
            f'<div class="pari"><span class="nom">{html.escape(str(p.get("libelle", "")))}</span>')
        # la pastille, telle que le bot la donne
        if p.get("pastille"):
            lignes[-1] += f'<span class="pas">{p["pastille"]}</span>'
        lignes[-1] += "</div>"
    plaisir = m.get("plaisir") or []
    bas = ""
    if plaisir:
        jolis = " · ".join(f'{html.escape(str(p.get("libelle")))} {p.get("pourcent"):g} %'
                           for p in plaisir if isinstance(p.get("pourcent"), (int, float)))
        if jolis:
            bas = f'<p class="plaisir">Pour le plaisir (sans pastille) : {jolis}</p>'
    return (f'<div class="match"><h3>{html.escape(str(m.get("match", "")))}</h3>'
            f'{"".join(lignes)}{bas}</div>')


def _carte_montante(v):
    quand = ""
    brut = v.get("coup_envoi") or ""
    if brut:
        try:
            h, minute = brut[11:13], brut[14:16]
            quand = f"Coup d\'envoi à {h}h{minute}"
        except Exception:
            quand = ""
    cotes = v.get("cotes") or {}
    detail = " · ".join(f"{k} : {val}" for k, val in cotes.items() if val)
    return (f'<div class="mont"><span class="badge">🌱 LA MONTANTE</span>'
            f'<div class="haut"><h3>{html.escape(str(v.get("match", "")))}</h3>'
            f'<span class="cote">{v.get("cote", "")}</span></div>'
            f'<p class="quoi">{html.escape(str(v.get("libelle", "")))}'
            + (f' — cotes {html.escape(detail)}' if detail else '') + '</p>'
            f'<p class="quand">{quand}</p></div>')




ANCIENS_VPN = {"vpn-efootball", "meilleur-vpn-pour-tv-android-le-guide-complet-2024",
               "telecharger-vpn-pour-tv-android-le-guide-complet",
               "vpn-pour-tv-android-guide-complet-gratuit-et-payant",
               "vpn-pour-regarder-canal-a-l-etranger-le-guide-complet",
               "meilleur-vpn-pour-la-chine-le-guide-complet-2026",
               "cyberghost-vpn-prix-par-mois-le-guide-complet"}

MARQUES = [("nordvpn", "NordVPN"), ("cyberghost", "CyberGhost"), ("betclic", "Betclic"),
           ("1xbet", "1xBet"), ("melbet", "Melbet"), ("premierbet", "Premier Bet")]


def _base():
    return os.environ.get("URL_PUBLIQUE", "https://pari-foot.onrender.com").rstrip("/")


def _image(slug, variante=0):
    """Illustration stable : le même article garde toujours la même image."""
    import hashlib
    empreinte = int(hashlib.md5((slug or "").encode()).hexdigest()[:8], 16)
    return f"/img/p{(empreinte + variante) % 8 + 1}.jpg"


def _temps_lecture(corps):
    mots = len(re.sub(r"<[^>]+>", " ", corps or "").split())
    return max(3, round(mots / 200))


def _maj(texte):
    texte = (texte or "").strip()
    if not texte:
        return texte
    texte = re.sub(r"\bvpn\b", "VPN", texte, flags=re.IGNORECASE)
    for fautif, juste in MARQUES:
        texte = re.sub(r"\b" + fautif + r"\b", juste, texte, flags=re.IGNORECASE)
    return texte[:1].upper() + texte[1:]


def _date_fr(texte):
    return (texte or "").strip() or "—"


def _page(titre, contenu, actif, titre_onglet=None, description=None):
    """La coquille du blog : en-tête collant, contenu, pied. Un seul <title> par page."""
    titre_final = titre_onglet or "Pari Foot — pronostics et guides de paris sportifs"
    balise_desc = (f'\n<meta name="description" content="{html.escape(description)}">'
                   if description else "")
    def lien(cle, libelle, adresse):
        return f'<a class="{"actif" if actif == cle else ""}" href="{adresse}">{libelle}</a>'
    onglets = (lien("jour", "Aujourd’hui", "/") + lien("guides", "Guides", "/guides")
               + lien("montante", "La montante", "/montante"))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre_final}</title>{balise_desc}
<link rel="manifest" href="/manifeste.json">
<meta name="theme-color" content="#fffdf8">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icone-apple-180.png">
<link rel="icon" type="image/png" href="/icone-192.png">
<style>{STYLE}</style></head><body>
<header class="site"><div class="wrap">
<a class="marque" href="/">Pari<span>Foot</span></a>
<nav>{onglets}</nav>
</div></header>
<main class="wrap">{contenu}</main>
<footer class="pied"><div class="wrap">
<p><b>Pari Foot</b> — les pronostics du jour et des guides honnêtes sur les paris sportifs.</p>
<p>Écrit par José Ledanite · <a href="/sitemap.xml">Plan du site</a></p>
</div></footer>
</body></html>"""


def page_jour():
    """Les analyses du jour. ⛔ Si elles datent d'hier, on ne fait pas semblant : afficher de
    vieux pronostics comme s'ils étaient du jour, c'est le meilleur moyen de perdre la confiance
    du lecteur — et la sienne."""
    p = lire_publication() or {}
    matchs = p.get("matchs") or []
    jour = p.get("jour") or ""
    aujourd = time.strftime("%Y-%m-%d")
    if matchs and jour and jour != aujourd:
        corps = (f'<div class="article" style="margin-top:26px"><h1>Pas d’analyses aujourd’hui</h1>'
                 f'<p class="chapeau">Les dernières analyses publiées datent du {html.escape(jour)}. '
                 f'Je ne les remets pas en avant : un pronostic périmé n’a aucune valeur.</p>'
                 f'<p><a href="/guides/"><b>Lire les guides en attendant →</b></a></p></div>')
    elif not matchs:
        corps = ('<div class="article" style="margin-top:26px"><h1>Pas d’analyses aujourd’hui</h1>'
                 '<p class="chapeau">Rien de solide à publier pour l’instant. Reviens en fin de '
                 'journée, ou lis les guides.</p>'
                 '<p><a href="/guides/"><b>Lire les guides →</b></a></p></div>')
    else:
        corps = "".join(_carte_message(m) for m in matchs)
    return _page("Aujourd'hui", corps, "jour")


def page_montante():
    p = lire_publication() or {}
    pool = (p.get("montante") or {}).get("pool") or []
    if not pool:
        corps = ('<div class="vide">Le vivier de la montante n\'est pas encore publié.<br>'
                 'Il arrive d\'habitude la veille au soir.</div>')
    else:
        corps = ('<h2>Le vivier du jour</h2>'
                 '<p class="plaisir" style="margin:0 0 12px">Les matchs retenus pour la montante. '
                 'La cote affichée est celle du pari conseillé.</p>'
                 + "".join(_carte_montante(v) for v in pool))
    return _page("La montante", corps, "montante")


def page_guides():
    """L'archive des guides : chaque article doit être atteignable en un clic."""
    entrees = list(reversed(list(articles.ARTICLES.items())))
    if not entrees:
        corps = ('<div class="article" style="margin-top:26px"><h1>Les guides</h1>'
                 '<p class="chapeau">Les guides arrivent.</p></div>')
    else:
        cartes = "".join(
            f'<a class="carte" href="/guides/{slug}/">'
            f'<div class="vignette"><img src="{_image(slug)}" alt="" loading="lazy" width="264" height="192"></div>'
            f'<div><h3>{html.escape(_maj(a["titre_onglet"]))}</h3>'
            f'<p>{html.escape(a["description"])}</p>'
            f'<span class="meta">{html.escape(_date_fr(a["publie_le"]))} · {_temps_lecture(a["corps"])} min</span>'
            f'</div></a>' for slug, a in entrees)
        corps = (f'<div class="article" style="margin-top:26px"><h1>Les guides</h1>'
                 f'<p class="chapeau">{len(entrees)} guides : les règles du pari, les erreurs qui '
                 f'coûtent cher, et comment lire une cote.</p></div>'
                 f'<div class="liste">{cartes}</div>')
    return _page("Guides", corps, "guides", titre_onglet="Guides — Pari Foot",
                 description="Guides de paris sportifs : cotes, gestion de mise, erreurs à éviter, "
                             "écrits pour les parieurs francophones.")


def page_article(slug):
    """Un guide présenté comme un article de blog : visuel, signature, partage."""
    a = articles.ARTICLES.get(slug)
    if not a:
        return None
    url = f"{_base()}/guides/{slug}/"
    titre = a["titre_onglet"]
    partage = (
        f'<a href="https://wa.me/?text={urllib.parse.quote(titre + " " + url)}" rel="nofollow">WhatsApp</a>'
        f'<a href="https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(url)}" rel="nofollow">Facebook</a>'
        f'<button type="button" onclick="navigator.clipboard.writeText(\'{url}\');this.textContent=\'Lien copié\'">Copier le lien</button>'
    )
    corps = (f'<div class="article">'
             f'<p class="fil"><a href="/">Accueil</a> › <a href="/guides/">Guides</a> › {html.escape(titre)}</p>'
             f'<h1>{html.escape(_maj(a["h1"]))}</h1>'
             f'<p class="chapeau">{html.escape(a["chapeau"])}</p>'
             f'<div class="entete-meta"><img src="/img/auteur.jpg" alt="José Ledanite" width="34" height="34">'
             f'<span><b>José Ledanite</b> · {html.escape(_date_fr(a["publie_le"]))} · '
             f'{_temps_lecture(a["corps"])} min de lecture</span></div>'
             f'<div class="hero"><img src="{_image(slug)}" alt="{html.escape(titre)}" width="1200" height="675"></div>'
             f'{a["corps"]}'
             f'<div class="partage"><span>Partager</span>{partage}</div></div>')
    return _page(a["h1"], corps, "guides", titre_onglet=_maj(titre), description=a["description"])


def sitemap():
    """LA CARTE DU SITE — indispensable : sans elle, Google met des semaines à trouver les guides.
    Le domaine est celui du déploiement ; si José change d'adresse, cette ligne suit."""
    base = os.environ.get("URL_PUBLIQUE", "https://pari-foot.onrender.com").rstrip("/")
    pages = ["/", "/montante", "/guides"] + [f"/guides/{s}" for s in articles.ARTICLES]
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>")


def robots():
    base = os.environ.get("URL_PUBLIQUE", "https://pari-foot.onrender.com").rstrip("/")
    return f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"


MANIFESTE = """{
 "name": "Pari Foot", "short_name": "Pari Foot", "lang": "fr",
 "start_url": "/", "scope": "/", "display": "standalone",
 "background_color": "#f7f9fc", "theme_color": "#f7f9fc",
 "description": "Les pronostics football de José Ledanite. Par José Ledanite.",
 "icons": [
  {"src": "/icone-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
  {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
  {"src": "/icone-masquable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
 ]
}"""

SERVICE_WORKER = """self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});   // rien en cache : un pronostic périmé est un mensonge
"""

FICHIERS = {"manifeste.json": ("application/manifest+json; charset=utf-8", MANIFESTE),
            "sw.js": ("text/javascript; charset=utf-8", SERVICE_WORKER)}
ICONES = ("icone-192.png", "icone-512.png", "icone-masquable-512.png",
          "icone-apple-180.png", "iparv.png")


def fabriquer_serveur(port=8080):
    class Traitement(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _envoyer(self, donnees, type_mime, code=200):
            if isinstance(donnees, str):
                donnees = donnees.encode()
            self.send_response(code)
            self.send_header("Content-Type", type_mime)
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

        def do_GET(self):
            chemin = self.path.split("?")[0]

            # ⚠️ ON COMPTE LES PAGES AFFICHÉES, PAS LES FICHIERS. Une icône ou un fichier JSON n'est
            # pas une visite : les compter gonflerait les chiffres sans rien dire de vrai. On garde
            # aussi le détail par page — « 40 visites » ne dit pas quoi corriger, « 40 visites dont
            # 31 sur le guide VPN » le dit.
            if not chemin.startswith(("/icone", "/img", "/manifeste", "/publication.json", "/trafic.json",
                                      "/sitemap", "/robots")):
                trafic.compter(chemin, self.headers.get("Referer") or "",
                               self.headers.get("User-Agent") or "")

            if chemin == "/trafic.json":
                import json as _json
                self._envoyer(_json.dumps(trafic.instantane(), ensure_ascii=False).encode(),
                              "application/json; charset=utf-8")
                return

            # ⚠️ DIAGNOSTIC TEMPORAIRE — POSÉ PUIS RETIRÉ LE MÊME JOUR (10/10/2026).
            # Question de José : « Quand je prendrai l'abonnement OVH, mon téléphone devra-t-il toujours
            # garder la récolte des cotes ? » Le test a été fait DEPUIS FRANCFORT — un vrai serveur, pas
            # une supposition : m.betclic.ci répond 403 Forbidden, la page du football comme la racine.
            # Betclic Côte d'Ivoire refuse les serveurs européens.
            # ✅ CONCLUSION RETENUE : la RÉCOLTE DES COTES RESTE SUR LE TÉLÉPHONE, quoi qu'il arrive.
            # Le reste (analyses, montante, application) peut partir sur OVH.
# ⛔ On ne réactive pas ce genre de route en ligne : une adresse écrite en dur est la règle,
            # et un diagnostic public qui va chercher des pages est exactement ce qu'on ne garde pas.

            if chemin in ("/", "/index.html"):
                self._envoyer(page_jour(), "text/html; charset=utf-8")
                return
            if chemin == "/montante":
                self._envoyer(page_montante(), "text/html; charset=utf-8")
                return
            # ── LES GUIDES (le contenu qui se référence). José, 10/10/2026 : « on va passer au SEO
            # de pari foot ». Sans ces pages, il n'y a rien à référencer : une application sans
            # texte ne se classe pas sur Google.
            if chemin == "/guides":
                self._envoyer(page_guides(), "text/html; charset=utf-8")
                return
            if chemin.startswith("/guides/"):
                slug = chemin[len("/guides/"):].strip("/")
                page = page_article(slug)
                if page:
                    self._envoyer(page, "text/html; charset=utf-8")
                    return
                # ⛔ Les guides VPN vivaient ici avant la séparation des deux sites. On les renvoie
                # définitivement vers Guide VPN : une redirection 301 transmet ce qui a été gagné,
                # là où un 404 le perdrait.
                if slug in ANCIENS_VPN:
                    self.send_response(301)
                    self.send_header("Location", "https://jos626.github.io/guides/" + slug + "/")
                    self.end_headers()
                    return
                self._envoyer("<h1>Page introuvable</h1>", "text/html; charset=utf-8", 404)
                return
            # La carte du site : elle dit à Google quelles pages existent. Sans elle, un site neuf
            # peut rester des semaines sans être exploré.
            if chemin == "/sitemap.xml":
                self._envoyer(sitemap(), "application/xml; charset=utf-8")
                return
            if chemin == "/robots.txt":
                self._envoyer(robots(), "text/plain; charset=utf-8")
                return
            if chemin == "/publication.json":
                self._envoyer(json.dumps(lire_publication() or {},
                                         ensure_ascii=False).encode(),
                              "application/json; charset=utf-8")
                return
            if chemin.lstrip("/") in FICHIERS:
                type_mime, texte = FICHIERS[chemin.lstrip("/")]
                self._envoyer(texte, type_mime)
                return
            if chemin.startswith("/img/") and chemin.endswith(".jpg"):
                fichier = os.path.join(ICI, chemin.lstrip("/"))
                try:
                    with open(fichier, "rb") as f:
                        self._envoyer(f.read(), "image/jpeg")
                except OSError:
                    self._envoyer("introuvable", "text/plain", 404)
                return
            if chemin.lstrip("/") in ICONES:
                try:
                    with open(os.path.join(ICI, chemin.lstrip("/")), "rb") as f:
                        self._envoyer(f.read(), "image/png")
                except OSError:
                    self._envoyer("introuvable", "text/plain", 404)
                return
            self._envoyer("<h1>Page introuvable</h1>", "text/html; charset=utf-8", 404)

    return ThreadingHTTPServer(("0.0.0.0", port), Traitement)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Pari Foot écoute sur le port {port}", flush=True)
    fabriquer_serveur(port).serve_forever()
