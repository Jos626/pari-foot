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
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import articles  # les GUIDES écrits (contenu SEO), avec leur lien d'affiliation en un seul endroit
import trafic    # le compteur de visites (sobre : sans cookie, sans adresse IP)

# ── Couche de finition commune (23/10/2026) ────────────────────────────────────────────────
# Détails d'interface (retour à la ligne des titres, contour des images, transitions nommées,
# chiffres tabulaires, focus visible, respect de prefers-reduced-motion). Servie à part pour ne
# jamais toucher aux gabarits : si elle disparaît, rien ne casse.
FINITION_CSS = r"""/* finition.css — couche de finition commune (23/10/2026)
   Règles reprises du dépôt ECC, appliquées en dernier : elles corrigent des détails sans toucher
   à la mise en page. Chargée par Pépite, Écoute, Pari Foot et Guide VPN.
   Ne jamais y mettre de règle de structure : uniquement du détail qui améliore sans casser. */

/* 1. Retour à la ligne : les titres ne finissent plus sur un mot orphelin,
      les textes courts se répartissent proprement. */
h1, h2, h3, h4, .titre, .titre-section, .entete h1, .hero h1, .article h1 {
  text-wrap: balance;
}
p, li, .aide, .sous, .chapeau, .extrait, .excerpt, figcaption, blockquote {
  text-wrap: pretty;
}

/* 2. Les images ne se fondent plus dans le fond clair (ni dans le sombre). */
img {
  outline: 1px solid rgba(0, 0, 0, .10);
  outline-offset: -1px;
}
@media (prefers-color-scheme: dark) {
  img { outline-color: rgba(255, 255, 255, .12); }
}

/* 3. Transitions nommées : jamais « all », sinon la mise en page s'anime par accident. */
button, .bouton, [role="button"], a.bouton, .carte-cliquable, summary {
  transition-property: transform, box-shadow, filter, background-color, border-color, color;
  transition-duration: .18s;
  transition-timing-function: cubic-bezier(.22, .61, .36, 1);
}
button:active, .bouton:active, [role="button"]:active, a.bouton:active {
  transform: scale(.96);
}

/* 4. Les chiffres qui changent ne font plus danser la ligne. */
table td, table th, .stat, .valeur, .compteur, .note-fin, .score, .badge, time, .prix {
  font-variant-numeric: tabular-nums;
}

/* 5. Le focus clavier se voit — sans halo permanent à la souris. */
:focus-visible {
  outline: 2px solid #0891b2;
  outline-offset: 2px;
}

/* 6. Cibles tactiles : un petit lien de pied de page reste atteignable au doigt. */
.pied a, footer a, nav a {
  display: inline-block;
  min-height: 24px;
  padding: 2px 0;
}

/* 7. Respect de la préférence système : certaines personnes ne supportent pas le mouvement. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
"""



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
.hero-accueil{position:relative;border-radius:18px;overflow:hidden;margin:0 0 22px;background:#1b1a17}
.hero-accueil img{width:100%;height:clamp(220px,46vw,420px);object-fit:cover;display:block;filter:brightness(.72)}
.hero-voile{position:absolute;inset:auto 0 0 0;padding:18px 20px 20px;
  background:linear-gradient(to top,rgba(12,11,9,.86),rgba(12,11,9,0))}
.hero-voile h1{color:#fff;font-size:clamp(1.5rem,6vw,2.4rem);margin:6px 0 0;line-height:1.12}
.hero-voile .etiquette{color:#e8c547;font-size:.72rem;letter-spacing:.12em;font-weight:700}
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

/* ══════════════════════════════════════════════════════════════════════════════════════
   COUCHE « VERRE CLAIR » — protocole de design de José (22/10/2026).
   Le blog garde sa tenue éditoriale (titres serif, larges marges) ; ce sont les surfaces,
   les ombres et les accents qui changent : halos pastel, cartes de verre, boutons en
   dégradé violet → cyan, apparition en fondu.
   ══════════════════════════════════════════════════════════════════════════════════════ */
:root{--violet:#7c3aed;--cyan:#0891b2;--verre:rgba(255,255,255,.66)}
body{
  background:
    radial-gradient(820px 520px at 6% -6%, rgba(124,58,237,.13), transparent 62%),
    radial-gradient(760px 560px at 102% 0%, rgba(8,145,178,.11), transparent 58%),
    radial-gradient(700px 620px at 50% 108%, rgba(236,72,153,.08), transparent 62%),
    #f9fafd;
  background-attachment:fixed;
}
header.site{background:rgba(255,255,255,.72);border-bottom:1px solid rgba(27,35,55,.08);
  -webkit-backdrop-filter:blur(18px) saturate(150%);backdrop-filter:blur(18px) saturate(150%)}
.marque{font-family:"Outfit",Georgia,serif;font-weight:800}
.une .visuel,.carte .vignette{border-radius:18px;box-shadow:0 18px 44px -30px rgba(27,35,55,.5)}
.une h2,.carte h3{letter-spacing:-.02em}
.etiquette{background:linear-gradient(100deg,rgba(124,58,237,.14),rgba(8,145,178,.14));
  color:#4c1d95;border:1px solid rgba(124,58,237,.22)}
.carte{background:rgba(255,255,255,.55);border:1px solid rgba(255,255,255,.8);
  border-radius:18px;padding:18px;margin:14px 0;
  -webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);
  box-shadow:0 16px 40px -32px rgba(27,35,55,.5);
  transition:transform .2s ease, box-shadow .25s ease, border-color .2s ease}
.carte:hover{transform:translateY(-3px);border-color:rgba(124,58,237,.3);
  box-shadow:0 22px 46px -30px rgba(124,58,237,.45)}
button,.bouton,.pf-form button{
  background:linear-gradient(100deg,var(--violet),var(--cyan));color:#fff;border:0;
  border-radius:14px;font-weight:700;font-family:inherit;
  box-shadow:0 12px 28px -14px rgba(124,58,237,.6);
  transition:transform .18s ease, box-shadow .25s ease, filter .2s ease}
button:hover,.bouton:hover,.pf-form button:hover{transform:translateY(-2px);filter:brightness(1.05);
  box-shadow:0 18px 38px -16px rgba(8,145,178,.55)}
input,textarea,select{background:rgba(255,255,255,.9);border:1px solid rgba(27,35,55,.12);
  border-radius:14px;transition:border-color .2s ease, box-shadow .2s ease}
input:focus,textarea:focus,select:focus{outline:none;border-color:var(--cyan);
  box-shadow:0 0 0 4px rgba(8,145,178,.14)}
/* encart « guide gratuit » : texte plein, jamais grisé ni barré */
.encart{background:#fffaf0 !important;border:1px solid #e8c56a !important;border-radius:16px;
  color:#1b2337}
.encart b{color:#1b2337;text-decoration:none}
.encart p{color:#4a5568 !important;font-size:14.5px;line-height:1.55}
.encart a{color:#7c3aed !important;font-weight:700;text-decoration:none}
.pf-boite{border-radius:20px;box-shadow:0 30px 70px -40px rgba(27,35,55,.6)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;
  transition-duration:.01ms!important}}
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


POPUP_CSS = r'''.pf-popup{position:fixed;inset:0;background:rgba(20,18,14,.55);display:flex;align-items:center;justify-content:center;padding:18px;z-index:99}
.pf-popup[hidden]{display:none}
.pf-boite{background:#fffdf8;border-radius:16px;max-width:380px;width:100%;padding:22px 20px 18px;position:relative;box-shadow:0 18px 50px rgba(0,0,0,.25);text-align:center}
.pf-boite img{width:100%;height:120px;object-fit:cover;border-radius:10px;margin-bottom:14px}
.pf-boite h3{margin:0 0 8px;font-size:1.25rem;line-height:1.25}
.pf-texte{margin:0 0 14px;font-size:.95rem;color:#5a5348}
.pf-form{display:flex;flex-direction:column;gap:8px}
.pf-form input{padding:12px 14px;border:1px solid #d9d2c4;border-radius:10px;font-size:1rem;background:#fff}
.pf-form button{padding:13px 16px;border:0;border-radius:10px;background:#14120e;color:#fff;font-size:1rem;font-weight:600;cursor:pointer}
.pf-fermer{position:absolute;top:8px;right:10px;border:0;background:transparent;font-size:1.6rem;line-height:1;cursor:pointer;color:#7a7264}
.pf-non{display:block;width:100%;margin-top:12px;border:0;background:transparent;color:#8a8272;font-size:.85rem;text-decoration:underline;cursor:pointer}
'''


POPUP_HTML = r'''<!-- ⛔ POPUP DE CAPTURE (19/10/2026, demande de José) : le formulaire en bas d'article ne parlait
     pas — trop loin, jamais vu. Il apparaît maintenant après 18 s de lecture (ou 55 % de la page),
     une seule fois par visiteur et par jour, et se ferme librement. Un popup qu'on ne peut pas
     fermer fait fuir ; un popup qu'on ferme soi-même se retient. -->
<div id="pf-popup" class="pf-popup" hidden>
  <div class="pf-boite" role="dialog" aria-modal="true" aria-labelledby="pf-titre">
    <button type="button" class="pf-fermer" aria-label="Fermer">×</button>
    <img src="/img/p6.jpg" alt="" width="360" height="120">
    <h3 id="pf-titre">Reçois nos meilleurs pronostics foot, chaque matin</h3>
    <p class="pf-texte">Les matchs du jour, l'analyse, la cote et la montante — dans ta boîte mail
    avant le coup d'envoi. Gratuit, désinscription en un clic.</p>
    <form action="/abonner" method="POST" class="pf-form">
                      <input type="email" name="email" required placeholder="ton@email.com" aria-label="Ton adresse email">
      <button type="submit">Recevoir mes pronostics du jour</button>
    </form>
    <button type="button" class="pf-non">Non merci, je continue ma lecture</button>
  </div>
</div>
<script>
(function () {
  // ?popup=1 force l'affichage : sans ça, le drapeau « une fois par jour » empêche de vérifier.
  var forcer = location.search.indexOf("popup=1") !== -1;
  if (!forcer) {
    try { if (localStorage.getItem("pf_popup") === new Date().toDateString()) return; } catch (e) {}
  }
  if (location.pathname.indexOf("/livre-blanc") === 0) return;
  var boite = document.getElementById("pf-popup");
  if (!boite) return;
  var montre = false;
  function afficher() {
    if (montre) return;
    montre = true;
    boite.hidden = false;
    if (!forcer) { try { localStorage.setItem("pf_popup", new Date().toDateString()); } catch (e) {} }
  }
  function fermer() { boite.hidden = true; }
  boite.querySelector(".pf-fermer").addEventListener("click", fermer);
  boite.querySelector(".pf-non").addEventListener("click", fermer);
  boite.addEventListener("click", function (e) { if (e.target === boite) fermer(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") fermer(); });
  setTimeout(afficher, 8000);
  window.addEventListener("scroll", function () {
    var h = document.documentElement;
    if ((h.scrollTop + window.innerHeight) / h.scrollHeight > 0.40) afficher();
  }, { passive: true });
})();
</script>'''


def _page(titre, contenu, actif, titre_onglet=None, description=None):
    """La coquille du blog : en-tête collant, contenu, pied. Un seul <title> par page."""
    titre_final = titre_onglet or "Pari Foot — pronostics et guides de paris sportifs"
    balise_desc = (f'\n<meta name="description" content="{html.escape(description)}">'
                   if description else "")
    def lien(cle, libelle, adresse):
        return f'<a class="{"actif" if actif == cle else ""}" href="{adresse}">{libelle}</a>'
    onglets = (lien("jour", "Aujourd’hui", "/") + lien("guides", "Guides", "/guides")
               )
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
<meta name="google-site-verification" content="h5XzcBysNSdxCMwQ0ksBW0wg9kprPAmrjHKjOFjkJls" />
<title>{titre_final}</title>{balise_desc}
<link rel="manifest" href="/manifeste.json">
<meta name="theme-color" content="#fffdf8">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icone-apple-180.png">
<link rel="icon" type="image/png" href="/icone-192.png">
<style>{STYLE}
{POPUP_CSS}
</style><link rel="stylesheet" href="/finition.css"></head><body>
<header class="site"><div class="wrap">
<a class="marque" href="/">Pari<span>Foot</span></a>
<nav>{onglets}</nav>
</div></header>
<main class="wrap">{contenu}</main>
<footer class="pied"><div class="wrap">
<p><b>Pari Foot</b> — les pronostics du jour et des guides honnêtes sur les paris sportifs.</p>
<p>Écrit par José Ledanite · <a href="/sitemap.xml">Plan du site</a></p>
</div></footer>

{POPUP_HTML}</body></html>"""


def page_jour():
    """Accueil éditorial. ⛔ PLUS AUCUN MATCH ICI (19/10/2026, demande de José) : les pronostics
    partent par email, le site ne montre que du contenu qui amène du trafic et l'inscription.
    Un match affiché en vitrine obligeait à le rafraîchir chaque matin — et un jour raté faisait
    passer tout le site pour périmé."""
    recents = list(articles.ARTICLES.items())[:6]
    cartes = []
    for slug, a in recents:
        cartes.append(
            f'<a class="carte" href="/guides/{slug}/">'
            f'<div class="vignette"><img src="{_image(slug)}" alt="" loading="lazy" width="264" height="192"></div>'
            f'<div class="carte-corps"><span class="etiquette">{html.escape(a.get("etiquette") or "GUIDE")}</span>'
            f'<h3>{html.escape(a.get("h1") or a.get("titre") or slug)}</h3>'
            f'<p>{html.escape((a.get("chapeau") or "")[:150])}</p></div></a>')

    # ⛔ UN BLOG SANS IMAGE EN TÊTE NE RESSEMBLE PAS À UN BLOG (remarque de José, 20/10) :
    # la page d'accueil enchaînait titre et texte sur du vide. Une grande photo de football
    # en ouverture donne le ton éditorial et retient l'œil avant la lecture.
    corps = (
        '<div class="hero-accueil">'
        '<img src="/img/p1.jpg" alt="Ambiance de stade lors d\'un match de football" '
        'width="1200" height="675">'
        '<div class="hero-voile"><span class="etiquette">PARIS SPORTIFS · CÔTE D\'IVOIRE</span>'
        '<h1>Parie mieux. Pas plus.</h1></div></div>'
        '<section class="hero-texte">'
        '<p class="chapeau">Des guides clairs pour les parieurs ivoiriens : comprendre une cote, '
        'tenir une bankroll, repérer un opérateur sérieux. Et mes pronostics du jour, envoyés par '
        'email chaque matin.</p>'
        '<p><a class="bouton" href="/guides/">Lire les guides</a></p>'
        '</section>'
        + FORMULAIRE +
        '<h2 class="section-titre">Les derniers guides</h2>'
        f'<div class="grille">{"".join(cartes)}</div>'
        '<div class="encart" style="border-color:#d9a900;background:#fffaf0;margin-top:26px">'
        '<img src="/img/p3.jpg" alt="" width="56" height="56">'
        '<div><b>Le guide du parieur débutant — gratuit</b>'
        '<p>Six sections pour ne pas griller sa bankroll en trois jours. '
        '<a href="/livre-blanc/"><b>Recevoir le guide</b></a>.</p></div>'
        '<div><b>Les 4 règles du parieur qui dure</b>'
        '<p>Deux ou trois équipes, un ou deux types de pari, 3 % du capital, et jamais un pari '
        "d'avant-match : on parie en direct, quand on voit le match. "
        '<a href="/methode-4-regles/"><b>Lire la méthode</b></a>.</p></div></div>'
    )
    return _page("Pari Foot", corps, "jour",
                 titre_onglet="Pari Foot — guides de paris sportifs et pronostics par email",
                 description="Guides de paris sportifs pour la Côte d'Ivoire : cotes, bankroll, "
                             "opérateurs fiables. Pronostics quotidiens par email, gratuit.")


def page_montante():
    """La montante n'est plus affichée : elle part dans l'email du matin, avec les analyses.
    La page reste ouverte pour expliquer ce que c'est et capter l'inscription."""
    corps = ('<div class="article" style="margin-top:26px"><h1>La montante</h1>'
             '<p class="chapeau">Une progression de mises, match par match, jusqu\'à ce que la '
             'série s\'arrête. Elle est envoyée chaque matin aux abonnés, avec les analyses du jour.</p>'
             + FORMULAIRE +
             '<h2>Comment ça marche</h2>'
             '<p>On part d\'une mise de départ, on la reporte sur le pari suivant, et on s\'arrête '
             'dès qu\'un pari tombe. L\'objectif n\'est pas de « doubler » : c\'est de faire monter '
             'une mise sans jamais exposer plus que le départ.</p>'
             '<ul><li>Chaque étape est indiquée avec sa cote et son heure de coup d\'envoi.</li>'
             '<li>La série s\'arrête au premier échec — c\'est la règle, pas une option.</li>'
             '<li>Ne suis jamais une montante avec de l\'argent dont tu as besoin.</li></ul>'
             '<p class="aide">Jeu responsable · interdit aux mineurs · joue seulement ce que tu peux perdre.</p>'
             '</div>')
    return _page("La montante", corps, "montante",
                 titre_onglet="La montante — Pari Foot",
                 description="La montante expliquée : une progression de mises envoyée chaque matin "
                             "aux abonnés, avec les analyses du jour.")


def page_guides():
    """L'archive des guides : chaque article doit être atteignable en un clic."""
    entrees = list(reversed(list(articles.ARTICLES.items())))
    if not entrees:
        corps = ('<div class="article" style="margin-top:26px"><h1>Les guides</h1>'
                 '<p class="chapeau">Les guides arrivent.</p></div>')
    else:
        # ⛔ LE LIVRE BLANC D'ABORD (José, 24/10/2026) : les 4 règles sont la porte d'entrée de la
        # liste, pas un article de plus perdu en bas.
        carte_livre = (
            '<a class="carte" href="/methode-4-regles/">'
            '<div class="vignette"><img src="/img/p3.jpg" alt="" loading="lazy" width="264" '
            'height="192"></div>'
            '<div><h3>Les 4 règles du parieur qui dure</h3>'
            '<p>Deux ou trois équipes suivies, un ou deux types de pari, 3 % du capital, et '
            'seulement des paris en direct, sur ces équipes.</p>'
            '<span class="meta">Livre blanc gratuit · 7 min</span></div></a>')
        cartes = carte_livre + "".join(
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
             f'<div class="encart" style="border-color:#d9a900;background:#fffaf0">'
             f'<img src="/img/auteur.jpg" alt="" width="56" height="56">'
             f'<div><b>📘 Le parieur débutant — gratuit</b>'
             f'<p>Six sections pour ne pas griller sa bankroll en trois jours. '
             f'<a href="/livre-blanc/"><b>Recevoir le guide</b></a> — par email, sans spam.</p></div></div>'
             f'{FORMULAIRE}'
             f'<div class="partage"><span>Partager</span>{partage}</div></div>')
    return _page(a["h1"], corps, "guides", titre_onglet=_maj(titre), description=a["description"])


# ⛔ LE FORMULAIRE DE CAPTURE DU SITE FOOT. Même chaîne que Guide VPN (FormSubmit → boîte de
# José → Pépite lit et envoie la séquence), mais le sujet porte « Pari Foot » : c'est ce qui
# permet à l'autorépondeur de choisir la séquence paris et non la séquence VPN.
FORMULAIRE = """
<form class="capture" action="/abonner" method="POST">
  <input type="email" name="email" required placeholder="ton@email.com" aria-label="Ton adresse email">
  <button type="submit">Recevoir mes pronostics du jour</button>
</form>
<p class="capture-note">Chaque jour, mes meilleurs pronostics dans ta boîte — et le guide du parieur débutant tout de suite. Gratuit, désinscription en un clic.</p>
"""

COUVERTURE = """
<div class="ebook"><div class="livre">
  <div class="haut"><small>Guide gratuit · édition 2026</small>
    <h3>Le parieur<br>débutant</h3></div>
  <div class="bas">Cotes · Mise · Erreurs à éviter<br>José Ledanite</div>
</div></div>
"""

LIVRE_BLANC = """
<h2>1. Une cote n'est pas une probabilité</h2>
<p>Une cote de 1,20 ne veut pas dire « sûr ». Elle dit ceci : le bookmaker estime l'événement
probable à un peu plus de 80 %, et il garde une marge au passage. Sur dix paris de ce type, tu en
perdras un ou deux — et c'est précisément ce qui efface les gains des neuf autres.</p>
<p>La bonne lecture : plus la cote est basse, plus la marge du bookmaker pèse lourd. C'est
mathématique, pas une opinion.</p>

<h2>2. La mise compte plus que le choix du match</h2>
<p>Deux parieurs peuvent choisir exactement les mêmes matchs : l'un finit ruiné, l'autre non.
La différence, c'est la taille des mises.</p>
<ul>
<li>Ne mise jamais plus de <b>2 à 3 % de ta bankroll</b> sur un pari, quelle que soit ta confiance.</li>
<li>Ta bankroll, c'est l'argent que tu acceptes de perdre entièrement — pas ton budget du mois.</li>
<li>Après une perte, la mise suivante ne change pas. « Se refaire » est le mécanisme qui vide
les comptes.</li>
</ul>

<h2>3. Les trois paris qui coûtent le plus cher</h2>
<ul>
<li><b>Le combiné à cinq sélections</b> — les cotes se multiplient, les probabilités aussi, mais
dans l'autre sens. Cinq favoris à 80 % de chances chacun, c'est une chance sur trois que tout passe.</li>
<li><b>Le pari « sûr » sur ton équipe</b> — tu ne paries pas avec ton cœur, tu paries avec une cote.</li>
<li><b>Le pari en direct après un but</b> — la cote a déjà bougé, et l'émotion décide à ta place.</li>
</ul>

<h2>4. Vérifier un opérateur avant de déposer</h2>
<p>Trois questions, deux minutes :</p>
<ul>
<li>Est-il <b>agréé en Côte d'Ivoire</b> ? Depuis 2024, seuls LONACI et ses partenaires publiés ont
le droit d'opérer légalement.</li>
<li>Les <b>retraits</b> passent-ils par Mobile Money, et en combien de temps ?</li>
<li>Les <b>conditions du bonus</b> : mise exigée, cote minimale, délai. Un bonus sans ces
précisions n'est pas un bonus.</li>
</ul>

<h2>5. Le bonus : lire les conditions, pas le pourcentage</h2>
<p>Un « 400 % » signifie presque toujours : 100 % sur chacun de tes quatre premiers dépôts, avec
une exigence de mise élevée et un délai court. La question utile n'est pas « combien ? » mais
« combien de fois dois-je miser avant de pouvoir retirer ? ».</p>
<p>Compare toujours trois lignes : l'exigence de mise, la cote minimale acceptée, et la durée de
validité. Les montants exacts changent — vérifie-les dans les conditions en vigueur le jour où tu
t'inscris.</p>

<h2>6. La règle qui résume tout</h2>
<p>Le pari sportif n'est pas un revenu : c'est un divertissement avec un coût. Celui qui gagne sur
la durée ne parie pas plus, il parie mieux — et il accepte de ne pas parier du tout certains jours.</p>
<p><small>Jeu responsable · interdit aux mineurs · joue seulement ce que tu peux perdre.</small></p>
"""


METHODE_4_REGLES = """
<h2>Pourquoi la plupart des parieurs perdent</h2>
<p>Ce n'est presque jamais une question de malchance. C'est une question de dispersion : trop
d'équipes, trop de types de paris, des mises qui grossissent après une perte, et des décisions prises
à chaud. Un parieur dispersé mise sur ce qu'il voit passer ; un parieur qui dure mise sur ce qu'il
connaît.</p>
<p>Les quatre règles qui suivent ne promettent pas de gagner. Elles servent à <b>arrêter de perdre
bêtement</b> — et c'est déjà la moitié du travail. Je les applique sur mon propre compte, avec mon
argent.</p>

<h2>Règle 1 — Ne parie que sur deux ou trois équipes</h2>
<p>Un championnat compte vingt clubs, et tu n'en connais vraiment aucun. Suivre trois équipes, ce
n'est pas une limitation : c'est la seule façon d'avoir un avis qui vaut mieux que celui du
bookmaker.</p>
<p>Comment les choisir :</p>
<ul>
<li>Des équipes que tu <b>regardes réellement</b> jouer, au moins une fois par mois.</li>
<li>Des équipes dont tu peux citer le gardien, le buteur et le style de jeu sans regarder.</li>
<li>Évite les clubs que tout le monde suit : leur cote est déjà parfaite. Cherche un club moins
couvert, où l'information circule moins vite.</li>
</ul>
<p>Ce que tu suis, match après match : les compositions probables, les absences, la forme réelle
(résultats et <b>manière</b> de gagner), et la façon dont l'équipe se comporte quand elle est menée.
Cette fiche, tenue à la main, vaut tous les pronostics achetés.</p>

<h2>Règle 2 — Un ou deux types de pari, pas plus</h2>
<p>Chaque type de pari est un métier différent. Le over/under ne se lit pas comme un handicap, et le
handicap asiatique ne se lit pas comme un résultat sec. En changeant d'angle tous les jours, tu
n'accumules aucune expérience : tu recommences à zéro chaque week-end.</p>
<p>Deux familles suffisent pour toute une saison :</p>
<ul>
<li><b>Le résultat ou le double chance</b> sur tes équipes — le plus lisible quand tu connais
vraiment l'équipe.</li>
<li><b>Le nombre de buts</b> (plus ou moins), qui dépend du style des deux équipes et se travaille
bien avec une seule grille de lecture.</li>
</ul>
<p>Choisis-en une, garde l'autre pour plus tard, et note chaque pari dans la même case du carnet.
C'est la répétition qui crée la compétence, pas la variété.</p>

<h2>Règle 3 — 3 % du capital, jamais plus</h2>
<p>C'est la règle qui sauve les trois autres. Le capital, c'est l'argent que tu acceptes de perdre
entièrement — jamais le loyer, jamais l'argent du commerce.</p>
<p><b>Ta mise, c'est 3 % du capital et pas un franc de plus.</b> Pour 100 000 FCFA de capital :</p>
<ul>
<li><b>3 % = 3 000 FCFA</b> par pari, au maximum, quelle que soit ta confiance. La confiance n'est pas
une donnée.</li>
<li>Après une perte, la mise suivante <b>ne change pas</b>. Doubler pour se refaire est le mécanisme
exact qui vide les comptes.</li>
<li>Une perte ne se rattrape pas le même jour : elle se rattrape sur trente paris, ou pas du tout.</li>
</ul>
<p>Le calcul, sur les trois capitaux les plus courants :</p>
<ul>
<li>Capital 25 000 FCFA → mise maximum <b>750 FCFA</b></li>
<li>Capital 50 000 FCFA → mise maximum <b>1 500 FCFA</b></li>
<li>Capital 100 000 FCFA → mise maximum <b>3 000 FCFA</b></li>
</ul>
<p>C'est ce qui protège le capital : à 3 %, il faut <b>vingt pertes d'affilée</b> pour perdre la
moitié de son capital. Vingt pertes d'affilée arrivent à tout le monde — c'est pour ça que la règle
existe.</p>

<h2>Règle 4 — Uniquement en direct, et seulement sur tes deux ou trois équipes</h2>
<p>Aucun pari avant le coup d'envoi. Tu regardes le match, et tu paries quand tu vois ce que tu
attendais : une équipe qui domine sans marquer, un rythme qui change, une cote qui s'ouvre. Le pari
d'avant-match se prend à l'aveugle, sur des informations que tout le monde a déjà.</p>
<p>Le direct ne donne pas le droit d'improviser pour autant : tes deux ou trois équipes, un ou deux
types de pari, 3 % de mise. Le direct sert à <b>voir</b>, pas à tenter.</p>
<p>Ce que ça change, concrètement :</p>
<ul>
<li>tu ne paries jamais un match que tu ne peux pas regarder ;</li>
<li>si la situation attendue n'arrive pas, tu ne paries pas — un match sans pari est un bon match ;</li>
<li>la mise reste décidée d'avance à 3 %, même à chaud.</li>
</ul>

<h2>La feuille qui rend tout vérifiable</h2>
<p>Une règle non notée est une règle qui n'existe pas. Pour chaque pari, quatre lignes suffisent :
la date, l'équipe (parmi tes trois), le type de pari et la cote, la mise, le résultat.</p>
<p>Au bout de trente paris, tu sauras deux choses que personne ne peut te dire à ta place : si ton
avantage est réel, et si tu respectes vraiment ta mise. La plupart des parieurs découvrent à ce
moment-là qu'ils misaient deux fois plus que ce qu'ils croyaient.</p>

<h2>Les erreurs qui coûtent le plus cher</h2>
<ul>
<li><b>Le combiné à cinq sélections</b> — les cotes se multiplient, les probabilités se divisent.</li>
<li><b>Parier sur son équipe de cœur</b> — on ne parie pas avec un maillot, on parie avec une cote.</li>
<li><b>Changer d'équipes après deux pertes</b> — c'est repartir à zéro au pire moment.</li>
<li><b>Augmenter la mise après une bonne série</b> — la série ne dit rien du prochain match.</li>
</ul>

<h2>Ce que ces quatre règles ne feront pas</h2>
<p>Elles ne transformeront pas le pari en salaire. Le bookmaker garde une marge sur chaque cote :
sur la durée, la majorité des parieurs perd, et aucune méthode ne change ce fait. Ces règles servent
à faire partie des exceptions, et surtout à ne jamais perdre plus que prévu.</p>
<p><small>Jeu responsable · interdit aux mineurs · ne joue que ce que tu peux perdre. Si le pari
cesse d'être un divertissement, arrête et parles-en à quelqu'un.</small></p>
"""


def page_quatre_regles():
    corps = ('<div class="article" style="margin-top:26px">'
             '<p class="fil"><a href="/">Accueil</a> \u203a Guide gratuit</p>'
             '<h1>Les 4 r\u00e8gles du parieur qui dure</h1>'
             '<p class="chapeau">Deux ou trois équipes, un ou deux types de pari, 3 % du capital, '
             'uniquement des paris en direct, sur les équipes que je suis. La méthode que j\'applique avec mon propre argent.</p>'
             # ⛔ « LE TUTORIEL EST TROP COURT » (José, 25/10/2026) : la page reste le résumé, et
             # l'ebook de 17 pages se télécharge ici, sans inscription.
             '<p><a class="bouton" href="/fichiers/les-4-regles-du-parieur.pdf" download>'
             '📥 Télécharger l\'ebook (PDF, 17 pages)</a></p>'
             '<p class="aide">Gratuit, sans inscription. Le format long de cette page : les chiffres, '
             'la feuille de suivi, les erreurs qui coûtent cher.</p>'
             + FORMULAIRE +
             '<div class="entete-meta"><img src="/img/auteur.jpg" alt="Jos\u00e9 Ledanite" width="34" height="34">'
             '<span><b>Jos\u00e9 Ledanite</b> \u00b7 \u00e9dition 2026 \u00b7 7 min de lecture</span></div>'
             + METHODE_4_REGLES +
             '</div>')
    return _page("Les 4 r\u00e8gles du parieur qui dure", corps, "guides",
                 titre_onglet="Les 4 r\u00e8gles du parieur qui dure \u2014 guide gratuit",
                 description="La m\u00e9thode en quatre r\u00e8gles pour durer aux paris sportifs : deux ou "
                             "trois \u00e9quipes suivies, un ou deux types de pari, 3 % du capital, "
                             "et uniquement des paris en direct, sur les \u00e9quipes suivies.")


def page_livre_blanc():
    corps = ('<div class="article" style="margin-top:26px">'
             '<p class="fil"><a href="/">Accueil</a> › Guide gratuit</p>'
             '<h1>Le parieur débutant</h1>'
             '<p class="chapeau">Cotes, mise, erreurs qui coûtent cher : ce que j\'aurais aimé lire '
             'avant mon premier pari.</p>'
             + COUVERTURE + FORMULAIRE +
             '<div class="entete-meta"><img src="/img/auteur.jpg" alt="José Ledanite" width="34" height="34">'
             '<span><b>José Ledanite</b> · édition 2026 · 8 min de lecture</span></div>'
             + LIVRE_BLANC +
             '</div>')
    return _page("Le parieur débutant", corps, "guides",
                 titre_onglet="Le parieur débutant — guide gratuit",
                 description="Guide gratuit pour débuter les paris sportifs sans griller sa bankroll : "
                             "cotes, mise, erreurs à éviter, vérifier un opérateur.")


def page_merci():
    corps = ('<div class="article" style="margin-top:40px">'
             '<h1>C\'est noté, tes 4 règles partent par email.</h1>'
             '<p class="chapeau">L\'email s\'appelle <b>« Tes 4 règles du parieur qui dure »</b> et '
             'contient les quatre règles, lisibles tout de suite, plus le lien du guide complet. '
             'S\'il n\'est pas là dans un quart d\'heure, regarde dans les spams et marque-le comme '
             '« non spam » — sinon tu ne recevras pas non plus les pronostics.</p>'
             '<p><a class="bouton" href="/fichiers/les-4-regles-du-parieur.pdf" download>'
             "📥 Télécharger l'ebook (PDF, 17 pages)</a></p>"
             '<p><a href="/guides/"><b>Lire les guides en attendant →</b></a></p></div>')
    return _page("C'est envoyé", corps, "guides", titre_onglet="Guide envoyé — Pari Foot")


def _abonner(email_client):
    """Inscrit un lecteur : le site dépose l'adresse dans un dépôt privé GitHub.

    ⛔ HISTORIQUE DU 19/10/2026, à garder en tête avant de « simplifier » :
      · FormSubmit n'a jamais confirmé son activation pour ce domaine (liens 500) — zéro inscription.
      · Envoyer l'email directement en SMTP depuis Render est impossible : `Network is unreachable`
        (port 465 bloqué par l'hébergeur). Vérifié par diagnostic, pas supposé.
    Le dépôt privé est la seule porte qui reste ouverte en HTTPS sans nouveau compte à créer.
    Pépite lit ce fichier depuis le téléphone et envoie lui-même le guide et la séquence — c'est
    lui qui a le SMTP, pas le site.
    """
    import base64
    import urllib.error
    jeton = os.environ.get("GH_TOKEN")
    depot = os.environ.get("GH_REPO", "Jos626/pari-foot-inscriptions")
    if not jeton:
        return False
    entetes = {"Authorization": "Bearer " + jeton, "Accept": "application/vnd.github+json",
               "User-Agent": "PariFoot", "Content-Type": "application/json"}
    url = f"https://api.github.com/repos/{depot}/contents/inscriptions.jsonl"
    sha, contenu = None, ""
    try:
        req = urllib.request.Request(url, headers=entetes)
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        sha = d.get("sha")
        contenu = base64.b64decode(d.get("content") or "").decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    ligne = json.dumps({"email": email_client, "quand": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "source": "foot"}, ensure_ascii=False) + "\n"
    corps = {"message": f"Inscription {email_client[:3]}***",
             "content": base64.b64encode((contenu + ligne).encode()).decode()}
    if sha:
        corps["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(corps).encode(), method="PUT", headers=entetes)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status in (200, 201)


def sitemap():
    """LA CARTE DU SITE — indispensable : sans elle, Google met des semaines à trouver les guides.
    Le domaine est celui du déploiement ; si José change d'adresse, cette ligne suit."""
    base = os.environ.get("URL_PUBLIQUE", "https://pari-foot.onrender.com").rstrip("/")
    pages = ["/", "/guides", "/livre-blanc", "/methode-4-regles"] + [f"/guides/{s}" for s in articles.ARTICLES]
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

        def _envoyer(self, donnees, type_mime, code=200, entete_plus=None):
            if isinstance(donnees, str):
                donnees = donnees.encode()
            self.send_response(code)
            self.send_header("Content-Type", type_mime)
            # ⛔ EN-TÊTES ABSENTS (audit du 22/10/2026) : on les ajoute ici, une fois pour toutes.
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("Referrer-Policy", "no-referrer-when-downgrade")
            # ?moi=1 : l'appareil de José s'exclut lui-même des compteurs, définitivement
            if getattr(self, "_cookie_moi", False):
                self.send_header("Set-Cookie", "pk_moi=1; Max-Age=31536000; Path=/; SameSite=Lax")
            for cle, valeur in (entete_plus or {}).items():
                self.send_header(cle, valeur)
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

        def _origine_locale(self):
            """⛔ CSRF (audit du 22/10/2026) : on refuse un formulaire venu d'un autre site."""
            origine = (self.headers.get("Origin") or self.headers.get("Referer") or "").strip()
            if not origine:
                return True
            return origine.startswith(("https://pari-foot.onrender.com",
                                       "http://127.0.0.1", "http://localhost"))

        def do_POST(self):
            """Les formulaires du site (inscription) postent ici.

            ⛔ Sans cette méthode, le serveur répond 501 et l'inscription est perdue — le lecteur
            voit une page d'erreur, et aucune inscription n'arrive. Le traitement est le même que
            pour GET : le corps est lu par la route /abonner elle-même.
            """
            if not self._origine_locale():
                self.send_response(403)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.do_GET()

        def do_GET(self):

            if self.path.split("?")[0] == "/finition.css":

                donnees = FINITION_CSS.encode("utf-8")

                self.send_response(200)

                self.send_header("Content-Type", "text/css; charset=utf-8")

                self.send_header("Cache-Control", "public, max-age=3600")

                self.send_header("Content-Length", str(len(donnees)))

                self.end_headers()

                self.wfile.write(donnees)

                return
            chemin = self.path.split("?")[0]
            # ⛔ 404 SUR UNE BARRE OBLIQUE (constat de José, 22/10/2026) : les liens du site
            # pointaient vers « /livre-blanc/ » alors que la route n'acceptait que
            # « /livre-blanc ». On tolère désormais les deux, sans casser les adresses d'articles
            # qui, elles, se terminent volontairement par une barre.
            if len(chemin) > 1 and chemin.endswith("/") and not chemin.startswith("/guides/"):
                chemin = chemin.rstrip("/")

            # ⛔ DÉSINSCRIPTION (20/10/2026) : l'email quotidien promet « un clic ». Sans cette
            # route, le lien promis menait à une page 404 — promesse non tenue, et signalement
            # spam assuré.
            if chemin == "/desinscription":
                import urllib.parse as _up
                params = _up.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                adresse = (params.get("email") or [""])[0].strip().lower()
                fait = False
                if adresse:
                    try:
                        import sqlite3 as _sq
                        conn = _sq.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "..", "seo-app", "abonnes.db"))
                        conn.execute("UPDATE abonnes SET statut='inactif' WHERE email=?", (adresse,))
                        conn.commit()
                        fait = conn.total_changes > 0
                        conn.close()
                    except Exception:                              # noqa: BLE001
                        fait = False
                corps = ("<!doctype html><html lang=fr><meta charset=utf-8>"
                         "<meta name=viewport content='width=device-width,initial-scale=1'>"
                         "<title>Désinscription — Pari Foot</title>"
                         "<body style=\"font-family:system-ui;background:#14120e;color:#f2ece0;"
                         "padding:32px;line-height:1.6\"><h1 style=\"font-size:1.3rem\">"
                         + ("C'est fait." if fait else "Adresse introuvable.")
                         + "</h1><p style=\"color:#b9ae9a\">"
                         + ("Tu ne recevras plus les pronostics du jour. Tes guides restent en ligne."
                            if fait else
                            "Aucun abonné actif ne correspond à cette adresse.")
                         + "</p><p><a style=\"color:#e3b45a\" href='/'>Retour au site</a></p>")
                corps_bytes = corps.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(corps_bytes)))
                self.end_headers()
                self.wfile.write(corps_bytes)
                return

            # ⚠️ ON COMPTE LES PAGES AFFICHÉES, PAS LES FICHIERS. Une icône ou un fichier JSON n'est
            # pas une visite : les compter gonflerait les chiffres sans rien dire de vrai. On garde
            # aussi le détail par page — « 40 visites » ne dit pas quoi corriger, « 40 visites dont
            # 31 sur le guide VPN » le dit.
            if not chemin.startswith(("/icone", "/img", "/manifeste", "/publication.json", "/trafic.json",
                                      "/sitemap", "/robots")):
                # ⛔ SON PROPRE TÉLÉPHONE NE COMPTE PAS (José, 25/10/2026) : ouvrir l'adresse une
                # fois avec ?moi=1 pose un cookie qui exclut cet appareil des compteurs.
                cookies = self.headers.get("Cookie") or ""
                if "pk_moi=1" not in cookies and "moi=1" not in (self.path or ""):
                    trafic.compter(chemin, self.headers.get("Referer") or "",
                                   self.headers.get("User-Agent") or "",
                                   (self.client_address[0] if self.client_address else ""))
                if "moi=1" in (self.path or ""):
                    self._cookie_moi = True

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
            if chemin in ("/montante", "/montante/"):
                # ⛔ PAGE SUPPRIMÉE (19/10/2026, demande de José) : la montante part dans l'email.
                # L'ancienne URL redirige vers les guides plutôt que d'afficher un fantôme.
                self.send_response(301)
                self.send_header("Location", "/guides/")
                self.end_headers()
                return
            # ── LES GUIDES (le contenu qui se référence). José, 10/10/2026 : « on va passer au SEO
            # de pari foot ». Sans ces pages, il n'y a rien à référencer : une application sans
            # texte ne se classe pas sur Google.
            if chemin in ("/abonner", "/abonner/"):
                longueur = int(self.headers.get("Content-Length") or 0)
                donnees = self.rfile.read(longueur).decode("utf-8", "ignore")
                params = urllib.parse.parse_qs(donnees)
                courriel = (params.get("email") or [""])[0].strip()
                if "@" in courriel and "." in courriel.split("@")[-1]:
                    try:
                        _abonner(courriel)
                    except Exception as e:      # noqa: BLE001 — on ne casse pas la page
                        print("inscription : envoi impossible —", type(e).__name__, e, flush=True)
                self.send_response(303)
                self.send_header("Location", "/livre-blanc/merci/")
                self.end_headers()
                return
            if chemin in ("/livre-blanc/merci", "/livre-blanc/merci/"):
                self._envoyer(page_merci(), "text/html; charset=utf-8")
                return
            if chemin in ("/methode-4-regles", "/methode-4-regles/"):
                self._envoyer(page_quatre_regles(), "text/html; charset=utf-8")
                return
            if chemin == "/livre-blanc":
                self._envoyer(page_livre_blanc(), "text/html; charset=utf-8")
                return
            if chemin in ("/guides", "/guides/"):
                self._envoyer(page_guides(), "text/html; charset=utf-8")
                return
            if chemin.startswith("/guides/"):
                slug = chemin[len("/guides/"):].strip("/")
                # ⛔ ANCIENNE URL CONSERVÉE EN 301 (20/10/2026) : le comparatif Betclic/Premier Bet a
                # été réécrit autour de 1xBet, seul programme d'affiliation actif. On redirige
                # proprement pour ne pas perdre l'indexation déjà acquise sur l'ancienne adresse.
                if slug == "betclic-ou-premier-bet-comparatif":
                    self.send_response(301)
                    self.send_header("Location", "/guides/1xbet-ou-premier-bet-comparatif/")
                    self.end_headers()
                    return
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
                # ⛔ TRAVERSÉE DE CHEMIN (audit du 22/10/2026) : « /img/../../x.jpg » sortait du
                # dossier du site. Nom de fichier simple + vérification du chemin résolu.
                fichier = os.path.realpath(os.path.join(ICI, "img", os.path.basename(chemin)))
                if not fichier.startswith(os.path.realpath(os.path.join(ICI, "img")) + os.sep):
                    self._envoyer("introuvable", "text/plain", 404)
                    return
                try:
                    with open(fichier, "rb") as f:
                        self._envoyer(f.read(), "image/jpeg")
                except OSError:
                    self._envoyer("introuvable", "text/plain", 404)
                return
            if chemin.startswith("/fichiers/") and chemin.endswith(".pdf"):
                # ⛔ L'EBOOK SE TÉLÉCHARGE (José, 25/10/2026) : « j'ai parlé plutôt d'un ebook que le
                # client peut télécharger à la réception du mail ». Même garde que /img : nom simple,
                # chemin résolu vérifié, sinon on sort du dossier.
                fichier = os.path.realpath(os.path.join(ICI, "fichiers", os.path.basename(chemin)))
                if not fichier.startswith(os.path.realpath(os.path.join(ICI, "fichiers")) + os.sep):
                    self._envoyer("introuvable", "text/plain", 404)
                    return
                try:
                    with open(fichier, "rb") as f:
                        self._envoyer(f.read(), "application/pdf",
                                      entete_plus={"Content-Disposition":
                                                   f'attachment; filename="{os.path.basename(fichier)}"'})
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

    # ⛔ ÉCOUTE OUVERTE À TOUT LE RÉSEAU (audit du 22/10/2026) : 0.0.0.0 est nécessaire sur
    # Render, mais sur le téléphone cela exposait le site à tout le Wi-Fi. On n'ouvre largement
    # que si la variable RENDER existe ; sinon on reste en local.
    hote = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    return ThreadingHTTPServer((hote, port), Traitement)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Pari Foot écoute sur le port {port}", flush=True)
    fabriquer_serveur(port).serve_forever()
