"""Le compteur de visites du site — sobre, et honnête sur ce qu'il mesure.

Ce qu'il compte : UNE VISITE PAR PAGE AFFICHÉE, sans cookie, sans identifiant, sans adresse IP
conservée. Aucune donnée personnelle n'est écrite nulle part : c'est la seule façon de compter qui
soit compatible avec un site public qu'on ne veut pas transformer en mouchard.

⚠️ CE QU'IL NE SAIT PAS FAIRE, ET IL LE DIT : l'hébergement gratuit REDÉMARRE le serveur (mise en
veille après 15 minutes sans visite, et à chaque republication). Un compteur qui vit en mémoire
repart alors de zéro. On écrit donc les compteurs dans un fichier, et le téléphone vient les
RELEVER régulièrement et les additionne. Ce qui est perdu, c'est au maximum ce qui s'est passé
entre le dernier relevé et un redémarrage — d'où la règle : **le relevé se fait souvent** (toutes
les 10 minutes), et les totaux sont annoncés comme « mesurés », jamais comme exacts au visiteur près.
"""

import json
import os
import threading
import time

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "trafic.json")

VERROU = threading.Lock()


def _jour():
    return time.strftime("%Y-%m-%d")


def _charger():
    try:
        with open(FICHIER, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _ecrire(d):
    try:
        tmp = FICHIER + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, FICHIER)
    except OSError:
        pass


# L'état vit en mémoire pendant que le serveur tourne (rapide), et se recopie sur disque à chaque
# visite : le fichier est petit, l'écriture est immédiate.
_ETAT = {"jours": {}, "demarre": time.strftime("%Y-%m-%dT%H:%M:%S"), "pages": {}, "sources": {}}


def _init():
    d = _charger()
    if isinstance(d.get("jours"), dict):
        _ETAT["jours"] = d["jours"]
    if isinstance(d.get("pages"), dict):
        _ETAT["pages"] = d["pages"]
    if isinstance(d.get("sources"), dict):
        _ETAT["sources"] = d["sources"]


_init()


def _provenance(referer):
    """D'OÙ VIENT LE VISITEUR — lu dans l'en-tête Referer, que le navigateur envoie lui-même.

    Demande de José (10/10/2026) : « voir quotidiennement les stats de visiteurs et leur provenance ».

    ⚠️ CE QUE ÇA DONNE VRAIMENT, ET CE QUE ÇA NE DONNE PAS. Le Referer dit la PAGE d'où l'on vient
    (google.com, facebook.com, un autre article…), pas la question tapée : depuis 2019, Google masque
    les mots-clés des recherches ordinaires. Prétendre afficher « les mots-clés qui amènent du
    monde » serait donc un mensonge — sauf pour les visiteurs venus d'un lien direct.
    Le détail par mot-clé demande Search Console, qui appartient à Google et exige un compte.
    """
    r = (referer or "").lower()
    if not r:
        return "accès direct (adresse tapée, favori, ou application)"
    if "google." in r:
        return "Google (recherche)"
    if any(x in r for x in ("facebook", "fb.com", "l.facebook")):
        return "Facebook"
    if any(x in r for x in ("t.co", "twitter", "x.com")):
        return "X / Twitter"
    if any(x in r for x in ("whatsapp", "wa.me")):
        return "WhatsApp"
    if "youtube" in r:
        return "YouTube"
    if "bing." in r:
        return "Bing"
    if "duckduckgo" in r:
        return "DuckDuckGo"
    if "pari-foot" in r or "localhost" in r or "127.0.0.1" in r:
        return "une autre page du site"
    return "autre site"


def compter(chemin, referer=""):
    """Une page vue. On garde le détail par jour, par page ET par provenance.

    « 40 visites » ne dit pas quoi corriger ; « 40 visites dont 31 sur le guide VPN, venues de
    Google » le dit — et c'est la seule façon de savoir si un article travaille.
    """
    with VERROU:
        j = _jour()
        _ETAT["jours"][j] = int(_ETAT["jours"].get(j) or 0) + 1
        cle = (chemin or "/").split("?")[0][:80]
        _ETAT["pages"][cle] = int(_ETAT["pages"].get(cle) or 0) + 1
        source = _provenance(referer)
        _ETAT["sources"][source] = int(_ETAT["sources"].get(source) or 0) + 1
        # On ne garde que 120 jours : au-delà, personne ne regarde, et le fichier grossirait pour rien.
        for jour in sorted(_ETAT["jours"])[:-120]:
            _ETAT["jours"].pop(jour, None)
        _ecrire(_ETAT)


def instantane():
    """Ce que le site répond sur /trafic.json : les compteurs, et de quand ils datent.

    ⚠️ ON DONNE AUSSI L'HEURE DE DÉMARRAGE DU SERVEUR. C'est ce qui permet, côté Pépite, de savoir
    qu'un redémarrage a eu lieu (compteur reparti de plus bas) et de ne PAS additionner deux fois
    ni perdre la différence en silence.
    """
    with VERROU:
        jours = dict(_ETAT["jours"])
        pages = dict(_ETAT["pages"])
        sources = dict(_ETAT["sources"])
    return {
        "jours": jours,
        "pages": dict(sorted(pages.items(), key=lambda kv: -kv[1])[:25]),
        "sources": dict(sorted(sources.items(), key=lambda kv: -kv[1])[:12]),
        "depuis": _ETAT["demarre"],
        "maintenant": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": "Une visite = une page affichée. Aucun cookie, aucune adresse IP conservée.",
    }
