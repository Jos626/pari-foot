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
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import articles  # les GUIDES écrits (contenu SEO), avec leur lien d'affiliation en un seul endroit
import trafic    # le compteur de visites (sobre : sans cookie, sans adresse IP)

ICI = os.path.dirname(os.path.abspath(__file__))
LECTURE_VERTE, LECTURE_VERTE_FORTE = "#16a34a", "#15803d"

STYLE = """
 :root{color-scheme:light}
 *{box-sizing:border-box}
 body{margin:0;background:
      radial-gradient(900px 400px at 50% -10%,#e6f6ee 0%,rgba(230,246,238,0) 60%),
      linear-gradient(180deg,#f7f9fc 0%,#eef2f8 100%);
      color:#0f172a;min-height:100vh;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
      padding:22px 16px 46px}
 .page{max-width:640px;margin:0 auto}
 .tete{display:flex;align-items:center;gap:13px;margin:0 0 18px}
 .tete img{width:52px;height:52px;border-radius:14px;box-shadow:0 8px 18px -10px rgba(11,61,46,.8)}
 .tete h1{font-size:22px;margin:0;letter-spacing:-.4px}
 .tete p{margin:2px 0 0;color:#64748b;font-size:12.5px}
 .onglets{display:flex;gap:8px;margin:0 0 18px}
 .onglets a{flex:1;text-align:center;text-decoration:none;color:#475569;font-weight:600;font-size:14px;
            padding:11px 8px;border-radius:12px;background:#fff;border:1px solid #e8edf4}
 .onglets a.actif{background:#0b3d2e;color:#fff;border-color:#0b3d2e}
 .frais{display:flex;align-items:center;gap:8px;color:#166534;background:#e8f8ee;border-radius:12px;
        padding:10px 13px;font-size:13px;margin:0 0 16px}
 h2{font-size:15px;margin:22px 0 10px;color:#475569;text-transform:uppercase;letter-spacing:.6px}
 .match{background:#fff;border:1px solid #e8edf4;border-radius:18px;padding:16px 16px 12px;margin:0 0 12px;
        box-shadow:0 1px 2px rgba(15,23,42,.03),0 14px 30px -20px rgba(15,23,42,.22)}
 .match h3{margin:0 0 12px;font-size:16px;letter-spacing:-.2px}
 .pari{display:flex;align-items:center;gap:11px;padding:7px 0}
 .pari .nom{flex:1;font-size:14.5px;color:#334155}
 .pari .barre{height:6px;border-radius:99px;background:#eef2f7;overflow:hidden;flex:0 0 74px}
 .pari .barre i{display:block;height:100%;background:#22c55e}
 .pari .pc{font-weight:700;font-size:15px;color:#15803d;min-width:52px;text-align:right}
 .pari .pas{font-size:13px;min-width:26px;text-align:center}
 .plaisir{color:#8896a8;font-size:12.5px;margin:10px 0 0;line-height:1.6}
 .message{background:#fff;border:1px solid #e8edf4;border-radius:18px;padding:18px 16px;margin:0 0 14px;
          box-shadow:0 1px 2px rgba(15,23,42,.03),0 14px 30px -20px rgba(15,23,42,.22);
          white-space:pre-wrap;word-break:break-word;font-size:15px;line-height:1.62;color:#1e293b}
 .message b{color:#0f172a}
 .message .quand2{margin:14px 0 0;color:#475569;font-size:14px;font-weight:600}
 .message .trait{color:#dfe5ef;letter-spacing:-1px}
 .mont{background:#fff;border:1px solid #e8edf4;border-radius:18px;padding:16px;margin:0 0 12px;
       box-shadow:0 14px 30px -20px rgba(15,23,42,.22)}
 .mont .haut{display:flex;align-items:baseline;gap:10px;margin:0 0 6px}
 .mont h3{margin:0;font-size:16px;flex:1}
 .mont .cote{font-weight:800;font-size:20px;color:#15803d}
 .mont .quoi{color:#475569;font-size:14px;margin:0 0 8px}
 .mont .quand{color:#8896a8;font-size:12.5px;margin:0}
 .badge{display:inline-block;background:#e8f8ee;color:#166534;font-size:11.5px;font-weight:700;
        padding:3px 9px;border-radius:99px;margin:0 0 8px}
 .pied{color:#94a3b8;font-size:12px;text-align:center;margin:26px 0 0;line-height:1.7}
 .signature{color:#94a3b8;font-size:12.5px;text-align:center;margin:14px 0 0}
 .signature b{color:#64748b;font-weight:600}
 /* ── LES GUIDES (José, 10/10/2026) ─────────────────────────────────────────────────────────────
    C'est ici que vit le CONTENU qui se référence. L'application (analyses, montante) est un outil ;
    un outil ne se classe pas sur Google. Un article, oui — à condition qu'il soit lisible :
    paragraphes courts, titres clairs, et un lien d'affiliation qui arrive là où il répond au
    problème, jamais avant. */
 .nom-site{font-size:22px;font-weight:700;margin:0;letter-spacing:-.4px}
 .article{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:20px 18px;
          box-shadow:0 10px 30px -22px rgba(15,23,42,.35)}
 .article h1{font-size:23px;line-height:1.3;margin:0 0 10px;letter-spacing:-.4px}
 .article h2{font-size:18.5px;margin:26px 0 8px;letter-spacing:-.2px;
             border-top:1px solid #eef2f8;padding-top:18px}
 .article h2:first-of-type{border-top:0;padding-top:0}
 .article h3{font-size:15.5px;margin:18px 0 6px;color:#15803d}
 .article p{margin:0 0 12px;line-height:1.72;font-size:14.5px}
 .article li{margin:0 0 8px;line-height:1.68;font-size:14.5px}
 .article ul,.article ol{margin:0 0 12px;padding-left:20px}
 .article .chapeau{font-size:15.5px;color:#334155;line-height:1.7}
 .divulgation{background:#f1f5f9;border-left:3px solid #94a3b8;border-radius:0 10px 10px 0;
              padding:11px 13px;font-size:13px;color:#475569;line-height:1.6;margin:0 0 16px}
 .lien-affilie{color:#15803d;font-weight:600;text-decoration:underline;text-underline-offset:2px}
 .bouton-affilie{display:inline-block;background:#16a34a;color:#fff!important;padding:13px 22px;
                 border-radius:12px;font-weight:700;text-decoration:none;letter-spacing:.2px;
                 box-shadow:0 10px 24px -12px rgba(22,163,74,.85)}
 .guide-carte{display:block;background:#fff;border:1px solid #e2e8f0;border-radius:14px;
              padding:15px 16px;margin:0 0 12px;text-decoration:none;color:#0f172a}
 .guide-carte b{display:block;font-size:15.5px;margin-bottom:5px}
 .guide-carte span{font-size:13px;color:#64748b;line-height:1.55}
 .vide{background:#fff;border:1px dashed #d7dee9;border-radius:18px;padding:26px;text-align:center;
       color:#8896a8;font-size:14px}
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


def _page(titre, contenu, actif, titre_onglet=None, description=None):
    """La coquille commune. `titre_onglet` et `description` servent aux GUIDES : c'est le titre de
    l'onglet et la description que Google lit en premier, et c'est ce qui décide du clic."""
    p = lire_publication() or {}
    jour = p.get("jour") or ""
    # ⚠️ LA DATE ÉTAIT CASSÉE (José l'a vue : « chiffres du (10/10à 01:27) »). Un bricolage de
    # découpage de chaîne produisait une parenthèse et un « à » collés. On lit la date pour de bon.
    fabrique = ""
    try:
        quand = datetime.fromisoformat(p.get("fabrique_le") or "")
        fabrique = quand.astimezone().strftime("le %d/%m à %H:%M")
    except (ValueError, TypeError):
        fabrique = ""
    onglets = (f'<a class="{"actif" if actif == "jour" else ""}" href="/">Aujourd\'hui</a>'
               f'<a class="{"actif" if actif == "montante" else ""}" href="/montante">La montante</a>'
               f'<a class="{"actif" if actif == "guides" else ""}" href="/guides">Guides</a>')
    # ⚠️ UNE SEULE BALISE <title> PAR PAGE, ET ELLE EST PROPRE (règle SEO : 40 à 60 caractères).
    # Avant, les guides auraient hérité du titre de l'application — un même titre sur toutes les
    # pages, ce que Google traite comme du contenu dupliqué.
    titre_final = titre_onglet or "Pari Foot — les pronostics de José Ledanite"
    balise_desc = (f'\n<meta name="description" content="{html.escape(description)}">'
                   if description else "")
    # ⚠️ UN SEUL H1 PAR PAGE (règle SEO). Le nom du site est donc un H1 sur l'application, mais un
    # simple texte sur les guides : là, le H1 doit être le TITRE DE L'ARTICLE. Deux H1 sur une page
    # brouillent le sujet aux yeux de Google.
    nom_site = ("<h1>Pari Foot</h1>" if actif != "guides"
                else '<p class="nom-site">Pari Foot</p>')
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="qNKo4HtNvkss5ya1qdbGFi6Jd_kZbz2R5GQDh3QVJEg">
<title>{titre_final}</title>{balise_desc}
<link rel="manifest" href="/manifeste.json">
<meta name="theme-color" content="#f7f9fc">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icone-apple-180.png">
<link rel="icon" type="image/png" href="/icone-192.png">
<style>{STYLE}</style></head><body><div class="page">
<div class="tete"><img src="/icone-192.png" alt="Pari Foot" width="52" height="52">
<div>{nom_site}<p>{html.escape(jour) if not fabrique else "chiffres " + html.escape(fabrique)}</p></div></div>
<div class="onglets">{onglets}</div>
{contenu}
<p class="pied">Pour l\'installer : menu ⋮ de ton navigateur → « Ajouter à l\'écran d\'accueil ».</p>
<p class="signature">Pari Foot — par <b>José Ledanite</b></p>
</div></body></html>"""


def page_jour():
    p = lire_publication() or {}
    matchs = p.get("matchs") or []
    if not matchs:
        corps = ('<div class="vide">Aucune analyse publiée pour le moment.<br>'
                 'Reviens un peu plus tard dans la journée.</div>')
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
    """La liste des guides. C'est aussi la porte d'entrée du maillage interne : chaque article doit
    être atteignable en un clic depuis une page que Google visite souvent."""
    cartes = "".join(
        f'<a class="guide-carte" href="/guides/{slug}"><b>{html.escape(a["titre_onglet"])}</b>'
        f'<span>{html.escape(a["description"])}</span></a>'
        for slug, a in articles.ARTICLES.items())
    corps = ('<div class="article"><h1>Les guides</h1>'
             '<p class="chapeau">Des explications concrètes, écrites pour être utiles — pas des '
             'listes traduites. Je te dis ce qui marche, et surtout ce qui ne marche pas.</p>'
             + cartes + '</div>')
    return _page("Guides", corps, "guides",
                 titre_onglet="Guides — Pari Foot",
                 description="Des guides honnêtes sur le VPN, le streaming et le football en ligne, "
                             "écrits pour les joueurs francophones.")


def page_article(slug):
    """Un guide, avec SON titre d'onglet et SA description (voir la règle SEO dans _page())."""
    a = articles.ARTICLES.get(slug)
    if not a:
        return None
    corps = (f'<div class="article"><h1>{html.escape(a["h1"])}</h1>'
             f'<p class="chapeau">{html.escape(a["chapeau"])}</p>'
             f'{a["corps"]}'
             f'<p class="pied">Publié le {html.escape(a["publie_le"])} · '
             f'<a href="/guides">Voir les autres guides</a></p></div>')
    return _page(a["h1"], corps, "guides",
                 titre_onglet=a["titre_onglet"], description=a["description"])


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
            if not chemin.startswith(("/icone", "/manifeste", "/publication.json", "/trafic.json",
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
                page = page_article(chemin[len("/guides/"):].strip("/"))
                if page:
                    self._envoyer(page, "text/html; charset=utf-8")
                else:
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
