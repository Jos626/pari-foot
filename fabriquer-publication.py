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


def nommer_pari(item):
    """Le libellé d'un pari, tel que le bot l'écrirait.

    ⛔ POURQUOI CETTE FONCTION : le vivier laisse « libelle » VIDE dès que le pari n'est pas une
    double chance. L'application affichait donc « None » — José l'a vu sur sa capture (« San
    Giovanni - Tre Fiori → None »). Un « None » à l'écran, c'est un trou dans la confiance : le
    client se demande ce qu'on lui cache. On nomme donc le pari avec le vocabulaire du bot :
    victoire → « Victoire de X », combiné → « Combiné de X », double chance → « X ou Nul ».
    """
    libelle = (item.get("libelle") or "").strip()
    if libelle:
        return libelle
    favori = (item.get("favori") or "").strip()
    pari = (item.get("pari") or "").strip().lower()
    if "victoire" in pari:
        return f"Victoire de {favori}" if favori else "Victoire"
    if "combin" in pari:
        return f"Combiné de {favori}" if favori else "Combiné"
    if "double" in pari:
        return f"{favori} ou Nul" if favori else "Double chance"
    return pari.capitalize() if pari else "—"


def horaires():
    """Heure de coup d'envoi et état « en direct », par match — les mêmes données que le bot."""
    c = lire("cotes-betclic.json", {})
    table = {}
    for nom, fiche in (c.get("cotes") or {}).items():
        if isinstance(fiche, dict):
            table[nom] = {"coup_envoi": fiche.get("coup_envoi"),
                          "en_direct": bool(fiche.get("en_direct")),
                          "competition": fiche.get("competition")}
    return table


def main():
    import moteur                  # importé ici pour que le dossier courant soit déjà le bon

    analyses = lire("analyses-du-jour.json", {"jour": None, "matchs": {}})
    vivier = lire("vivier-montante.json", {})
    aujourd = datetime.now().strftime("%Y-%m-%d")
    jour = analyses.get("jour") or aujourd

    # ⛔ CONSTAT 19/10/2026 — LA PANNE QUI COÛTE LA CRÉDIBILITÉ : le bot était mort, ses analyses
    # dataient du 17, et cette fabrique les a republiées avec un horodatage neuf. José a reçu une
    # « montante du jour » portant un match du 17 — vrai match, mauvaise journée. Un pronostic
    # périmé présenté comme celui du jour, c'est pire qu'aucun pronostic.
    # Règle : si les analyses ne sont pas de la journée, on ne fabrique RIEN et on le dit.
    if jour != aujourd:
        print(f"⛔ Analyses datées du {jour} (aujourd'hui : {aujourd}). "
              f"Le bot n'a rien produit de neuf — publication annulée.", flush=True)
        return 2

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
        # on ajoute l'heure du coup d'envoi quand on la connaît : José a demandé « ce sont les matchs
        # à venir pour aujourd'hui ? ». La réponse est oui (le bot refuse les matchs commencés), mais
        # mieux vaut le montrer que le dire.
        table = horaires()
        infos = table.get(nom) or {}
        # ⛔ Même règle pour chaque match : sans coup d'envoi du bon jour, il ne part pas.
        # ⛔ EXIGENCE DE PREUVE (19/10/2026). Un match sans heure de coup d'envoi n'a aucune preuve
        # qu'il se joue aujourd'hui : le 19/10, trois rencontres japonaises sans horaire sont
        # passées en publication — introuvables dans le calendrier du jour (FotMob), et l'une
        # d'elles ressemblait à un match féminin du 18. Pas d'horaire du jour = pas de publication.
        quand = (infos.get("coup_envoi") or "")[:10]
        if quand != jour:
            if quand:
                print(f"   (écarté, joué le {quand}) {nom}", flush=True)
            else:
                print(f"   (écarté, aucun horaire vérifiable) {nom}", flush=True)
            refuses += 1
            continue
        matchs.append({"match": nom, "message": texte,
                       "coup_envoi": infos.get("coup_envoi"),
                       "en_direct": infos.get("en_direct", False)})

    pool = []
    for v in (vivier.get("vivier") or []):
        if not isinstance(v, dict) or not v.get("match"):
            continue
        quand = (v.get("coup_envoi") or "")[:10]
        if quand and quand != jour:      # match d'un autre jour = hors montante
            continue
        pool.append({"match": v.get("match"), "competition": v.get("competition"),
                     "libelle": nommer_pari(v),          # ⛔ plus jamais de « None » à l'écran
                     "cote": v.get("cote"),
                     "coup_envoi": v.get("coup_envoi"), "en_direct": bool(v.get("en_direct"))})

    # même règle côté site : la montante se lit dans l'ordre des coups d'envoi
    pool.sort(key=lambda v: (v.get("coup_envoi") or "9999"))

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
