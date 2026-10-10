"""Fabrique le fichier que publie l'application Pari Foot.

⚠️⚠️ CE FICHIER A ÉTÉ RÉÉCRIT LE 10/10/2026, ET VOICI POURQUOI — c'est une leçon, pas un détail.
José a regardé l'application et a répondu sans ménagement : « C'est quoi ça ! 😄 Je veux que ce soit
exactement comme avec le bot. Et je veux pas l'histoire des analyses. Non ! Fais comme exactement
avec le bot. »

Il avait raison. J'avais reconstruit à ma façon un résumé à partir d'un fichier intermédiaire : des
pourcentages alignés, une section « pour le plaisir » qu'il n'a jamais demandée, et PAS les scores
les plus probables que le bot donne toujours. Autrement dit : à vouloir faire joli, j'avais fabriqué
une deuxième vérité — avec les mêmes chiffres, mais d'autres mots, un autre ordre, et des manques.

LA RÈGLE QUI EN DÉCOULE : on n'imite pas le bot, on lui DEMANDE son texte. Cette fabrique appelle le
moteur du bot (moteur.repondre) et range sa réponse telle quelle. L'application affiche ce texte.
Il ne peut donc pas y avoir de divergence : ce que le client lit dans l'application est
littéralement ce que le bot aurait envoyé.

⚠️ Et on jette les réponses de refus (« ce match n'est plus jouable ») : c'est la même règle que le
bot, un match en cours ne s'analyse pas.
"""
import json
import os
import sys
from datetime import datetime, timezone

BOT = os.path.expanduser("~/bot-pronos")
ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "publication.json")

sys.path.insert(0, BOT)
os.chdir(BOT)                       # le moteur lit ses fichiers de données depuis ce dossier


def lire(nom, defaut):
    try:
        with open(os.path.join(BOT, nom), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defaut


def main():
    import moteur                  # importé ici pour que le dossier courant soit déjà le bon

    analyses = lire("analyses-du-jour.json", {"jour": None, "matchs": {}})
    vivier = lire("vivier-montante.json", {})
    jour = analyses.get("jour") or datetime.now().strftime("%Y-%m-%d")

    matchs, refuses = [], 0
    for nom in (analyses.get("matchs") or {}).keys():
        try:
            texte = moteur.repondre(nom)
        except Exception as e:
            print(f"   (le moteur a échoué sur {nom} : {type(e).__name__})", flush=True)
            continue
        if not texte:
            continue
        # ⛔ ON NE PUBLIE PAS LES REFUS. Le bot refuse d'analyser un match commencé ; l'application
        # doit dire la même chose — ou plutôt, ne rien dire du tout : on ne publie que ce qui a une
        # vraie analyse.
        if "N'EST PLUS JOUABLE" in texte.upper() or "N'EST PAS" in texte.upper()[:120]:
            refuses += 1
            continue
        if "MES PARIS SUR CE MATCH" not in texte:
            continue
        matchs.append({"match": nom, "message": texte})

    pool = []
    for v in (vivier.get("vivier") or []):
        if not isinstance(v, dict) or not v.get("match"):
            continue
        pool.append({"match": v.get("match"), "competition": v.get("competition"),
                     "libelle": v.get("libelle"), "cote": v.get("cote"),
                     "coup_envoi": v.get("coup_envoi"), "en_direct": bool(v.get("en_direct"))})

    publication = {
        "jour": jour,
        "fabrique_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "matchs": matchs,
        "montante": {"mode": vivier.get("mode"), "jour": vivier.get("jour"), "pool": pool},
    }
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(publication, f, ensure_ascii=False, indent=1)
    print(f"publication écrite : {len(matchs)} analyse(s) du bot · {refuses} refus(s) écarté(s) "
          f"· {len(pool)} match(s) dans la montante")
    for m in matchs[:2]:
        premiere = m["message"].split("\n")[0]
        print("   ", premiere[:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())
