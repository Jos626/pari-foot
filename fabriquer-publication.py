"""Fabrique le fichier que l'application publie (publication.json).

POURQUOI CE FICHIER EXISTE. Les cotes du bot viennent de m.betclic.ci — un site ivoirien, donc
inaccessible depuis un serveur en Europe. C'est sur le TÉLÉPHONE que la récolte et le calcul ont
lieu, et c'est là qu'ils fonctionnent. L'application, elle, n'a pas besoin de savoir calculer : elle
a besoin de SAVOIR MONTRER. On lui donne donc un instantané propre, fabriqué ici, et rien d'autre.

CE QU'ON GARDE, ET CE QU'ON JETTE. On garde ce qu'un client lit : le nom du match, la compétition,
les paris proposés avec leur pourcentage, la cote, l'heure du coup d'envoi, et le vivier de la
montante. On jette tout le reste (identifiants internes, abonnés, surveillance, battements) : un
instantané publié doit pouvoir être lu par n'importe qui sans rien révéler de privé.
"""
import json
import os
import sys
from datetime import datetime, timezone

BOT = os.path.expanduser("~/bot-pronos")
SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publication.json")

# ⛔ LES SEUILS DES PASTILLES, IDENTIQUES AU BOT (décision de José) : 🟢 dès 70 %, 🟢🟢 au-dessus de
# 80 %, et RIEN en dessous. Une pastille qui apparaîtrait ici alors qu'elle n'apparaît pas dans le bot
# serait un mensonge par incohérence.
SEUIL_PASTILLE = 70.0
SEUIL_PASTILLE_FORTE = 80.0


def lire(nom, defaut):
    try:
        with open(os.path.join(BOT, nom), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defaut


def pastille(pourcent):
    if pourcent is None:
        return None
    if pourcent > SEUIL_PASTILLE_FORTE:
        return "🟢🟢"
    if pourcent >= SEUIL_PASTILLE:
        return "🟢"
    return None


def main():
    analyses = lire("analyses-du-jour.json", {"jour": None, "matchs": {}})
    vivier = lire("vivier-montante.json", {})
    programme = lire("programme-du-jour.json", {"matchs": []})

    matchs = []
    for nom, paris in (analyses.get("matchs") or {}).items():
        retenus, plaisir = [], []
        for p in (paris or []):
            libelle = (p.get("libelle") or "").strip()
            pourcent = p.get("pourcent")
            if not libelle:
                continue
            fiche = {"libelle": libelle, "pourcent": round(pourcent, 1) if pourcent is not None else None,
                     "pastille": pastille(pourcent)}
            (plaisir if p.get("fun") else retenus).append(fiche)
        if retenus or plaisir:
            matchs.append({"match": nom, "paris": retenus, "plaisir": plaisir})

    # la montante : le vivier tel quel, mais nettoyé de tout ce qui est interne
    pool = []
    for v in (vivier.get("vivier") or []):
        if not isinstance(v, dict) or not v.get("match"):
            continue
        pool.append({"match": v.get("match"), "competition": v.get("competition"),
                     "libelle": v.get("libelle"), "cote": v.get("cote"),
                     "favori": v.get("favori"), "cotes": v.get("cotes"),
                     "coup_envoi": v.get("coup_envoi"), "en_direct": bool(v.get("en_direct")),
                     "risques": v.get("risques") or []})

    publication = {
        "jour": analyses.get("jour") or programme.get("quand", "")[:10],
        "fabrique_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "bot de pronostics de José Ledanite (calcul sur téléphone, cotes Betclic CI)",
        "matchs": matchs,
        "montante": {"mode": vivier.get("mode"), "jour": vivier.get("jour"), "pool": pool},
    }
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(publication, f, ensure_ascii=False, indent=1)
    print(f"publication.json écrit : {len(matchs)} matchs analysés, {len(pool)} matchs dans la montante")
    for m in matchs[:3]:
        jolis = ", ".join(f"{p['libelle']} {p['pourcent']}% {p['pastille'] or ''}".strip()
                          for p in m["paris"][:3])
        print(f"   {m['match']} → {jolis or '(que du plaisir)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
