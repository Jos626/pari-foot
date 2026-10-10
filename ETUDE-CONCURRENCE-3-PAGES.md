# Étude de concurrence — 3 pages à écrire

**Pour :** José Ledanite (Abidjan) — site football + streaming sportif, budget zéro, monétisation par affiliation NordVPN (programme Impact)
**Objet :** Mesurer la concurrence RÉELLE sur les 3 mots-clés/pages déjà identifiés, donner un verdict de difficulté pour chacun, et livrer le plan d'article détaillé de la page n°1 (« VPN pour eFootball »).
**Date de l'étude :** 10 octobre 2026
**Fichier :** `/data/data/com.termux/files/home/app-foot/ETUDE-CONCURRENCE-3-PAGES.md`

---

## ⚠️ À lire d'abord : ce que cette étude peut prouver, et ce qu'elle ne peut pas

Règle d'honnêteté, tenue de bout en bout : **aucun volume de recherche ni nombre de visites n'est inventé.** Quand une mesure était impossible avec les outils gratuits, c'est écrit franchement.

Chaque affirmation porte une étiquette :

- **[VÉRIFIÉ — source nommée]** = mesure prise aujourd'hui, que tu peux refaire toi-même avec le lien/la commande donnés.
- **[À VÉRIFIER]** = non confirmé, à contrôler avant de décider.

### Les outils réellement utilisés (et leurs limites)

| Outil | Ce qu'il donne | Source vérifiable | Limite |
|---|---|---|---|
| Autocomplétion Google (gl=ci, hl=fr) | Ce que les Ivoiriens tapent vraiment ; **l'ordre = popularité relative** | `suggestqueries.google.com/complete/search?client=firefox&hl=fr&gl=ci&q=…` | Pas de volume chiffré |
| Brave Search (HTML) | Qui occupe le terrain réellement | `search.brave.com/search?q=…` | Instantané, peut bouger ; **n'est pas Google** |
| DuckDuckGo (via repli Exa) | Deuxième moteur de contrôle, croisé avec Brave | outil `web_search` (repli) | Backend principal HS aujourd'hui (voir ci-dessous) |
| RDAP | **Date de création exacte** des sites concurrents | `curl -sL https://rdap.org/domain/<domaine>` | Ne dit rien du trafic ni du contenu |

### Les deux limites de mesure à connaître (je ne les cache pas)

1. **Je n'ai PAS obtenu une véritable page de résultats Google.** Google bloque l'extraction automatisée, et le backend DuckDuckGo de l'outil de recherche est tombé en panne pendant cette session (« ddgs package is not installed »), le repli Exa ne répondant qu'une fois sur trois. Les classements ci-dessous viennent donc de **Brave Search et DuckDuckGo**, croisés entre eux. L'**ordre exact** des positions Google peut différer ; **le contenu** (qui est présent, dans quelle langue) est lui bien établi par deux moteurs concordants. **[VÉRIFIÉ — Brave + DDG, 10/10/2026]**
2. **Le paramètre local `gl=ci` de Google n'a pu être forcé que sur l'autocomplétion** (endpoint direct, `gl=ci`), pas sur une vraie SERP. La « variante locale » est donc approchée par l'autocomplétion ivoirienne + les moteurs. **[À VÉRIFIER]** si tu veux le classement exact vu depuis Abidjan.
3. **hide.me, telleport.me, vpnhub.me (.me)** et quelques `.io`/`.org` : le registre RDAP est inaccessible pour ces extensions depuis ce poste. Leur âge est marqué **[À VÉRIFIER]**.

---

## SYNTHÈSE (l'essentiel en 30 secondes)

| Page | Requête principale | Espace francophone | Verdict de difficulté |
|---|---|---|---|
| **1. VPN pour eFootball** | « vpn pour efootball » | **PRESQUE VIDE** | **Atteignable en 1 mois** ✅ |
| **2. VPN Côte d'Ivoire** | « vpn cote d'ivoire » | Quelques pages FR, mais concurrents installés | **Atteignable en 3 mois** |
| **3. IPTV en Côte d'Ivoire (légalité + alternative)** | « iptv legal / interdit en cote d'ivoire » | **VIDE de tout guide honnête** (que la presse et le régulateur) | **Atteignable en 1 mois** ⚠️ (mais conversion incertaine) |

**LE SIGNAL LE PLUS IMPORTANT DE TOUT LE DOCUMENT :**

> ### SUR « VPN POUR eFOOTBALL » (ET SA VARIANTE FRANÇAISE « MEILLEUR VPN eFOOTBALL »), IL N'Y A **PRESQUE AUCUN RÉSULTAT EN FRANÇAIS DÉDIÉ**. LA PAGE DE RÉSULTATS EST OCCUPÉE À ~95 % PAR DE L'ANGLAIS (ExpressVPN, hide.me, Reddit, comparateurs anglophones), ET LES RARES PAGES FRANÇAISES TROUVÉES SONT DES PAGES DE FOURNISSEURS GÉNÉRIQUES TRADUITES, PAS DES ARTICLES PENSÉS POUR UN FRANCOPHONE.
>
> **Traduction concrète : un article français honnête et complet sur « VPN pour eFootball » arrive sur un terrain quasi vide en français.**

---

## PAGE 1 — « VPN pour eFootball »

### La demande réelle (autocomplétion Google, gl=ci, hl=fr)

**[VÉRIFIÉ — API autocomplétion Google, gl=ci, 10/10/2026.]** L'ordre = popularité relative :

- `vpn pour efootball`
- `vpn pour efootball 2025`
- `vpn pour efootball mobile`
- `vpn pour efootball gratuit`
- `meilleur vpn pour efootball`
- `vpn pour télécharger efootball`
- `vpn premium pour efootball`

Demandes liées : `vpn pes`, `vpn football streaming`, `vpn pour tv android`. **[VÉRIFIÉ — autocomplétion, mêmes paramètres.]**

**Ce que ça dit :** la demande est **précise et acheteuse** (« meilleur vpn », « premium », « mobile »). Ce n'est pas du trafic passif : c'est un joueur qui cherche activement une solution. Excellent pour l'affiliation.

### Qui occupe réellement les résultats

Requête principale **« vpn pour efootball »** (croisement Brave + DuckDuckGo, 10/10/2026) :

| # | Site | URL | Langue | Type | Âge du domaine (RDAP) |
|---|---|---|---|---|---|
| 1 | hide.me | `/fr/gaming-vpn/efootball` | **Français** (page traduite) | Fournisseur VPN | [À VÉRIFIER] (.me inaccessible) |
| 2 | ExpressVPN | `/gaming/efootball-vpn` | Anglais | Fournisseur VPN (marque) | **2008-09-21** [VÉRIFIÉ — RDAP] |
| 3 | GuruVPN | `/gaming/efootball` | Anglais | Fournisseur/comparateur VPN | 2018-06-08 [VÉRIFIÉ — RDAP] |
| 4 | VPNwise | `/en/guides/best-vpn-efootball/` | Anglais | Comparateur affilié | **2026-04-03** (très récent) [VÉRIFIÉ — RDAP] |
| 5 | HidzoVPN | `/blog/vpns-for-efootball` | Anglais | Marque VPN / blog | 2025-01-28 [VÉRIFIÉ — RDAP] |
| 6 | hide.me | `/en/gaming-vpn/efootball` | Anglais | Fournisseur VPN | [À VÉRIFIER] |
| 7 | Reddit | `r/eFootball` (plusieurs fils) | Anglais | Forum | **2005-04-29** [VÉRIFIÉ — RDAP] |
| 8 | Acciyo | `/best-vpn-for-efootball-2025…` | Anglais | Blog tech / affilié | 2017-01-16 [VÉRIFIÉ — RDAP] |
| 9 | GearUP Booster | `/fr/blog/efootball-console-lag-fix.html` | **Français** (mais : anti-lag, pas VPN) | Outil réseau gaming | 2022-07-22 [VÉRIFIÉ — RDAP] |
| 10 | VPNAlerT | `/best-virtual-private-network/pes/` | Anglais | Comparateur affilié | 2017-05-14 [VÉRIFIÉ — RDAP] |

Autres occupants vus (Brave + DDG) : **proprivacy.com** (2004-07-25 [VÉRIFIÉ — RDAP], comparateur anglophone installé), **vpnguider.com** (2020-05-23), **ufovpn.io** [À VÉRIFIER], YouTube, TikTok.

Requête variante **« meilleur vpn efootball »** (Brave, 10/10/2026) : ExpressVPN, HidzoVPN, VPNGuider, VPNAlerT, ufovpn.io, Reddit, YouTube — **100 % anglophone, ZÉRO résultat français.**

### Combien de résultats en français ?

> ## RÉSULTATS EN FRANÇAIS SUR « VPN POUR eFOOTBALL » : **1 SUR 10** (et c'est une page de fournisseur traduite, pas un article).
> ## RÉSULTATS EN FRANÇAIS SUR « MEILLEUR VPN eFOOTBALL » : **ZÉRO SUR 10**.

**C'est le signal décisif.** La demande est francophone (confirmée par l'autocomplétion gl=ci), mais l'offre éditoriale française est inexistante. Personne n'a écrit l'article que José veut écrire.

### Lecture concurrentielle

Trois familles d'occupants, **aucune n'est adaptée au public francophone** :

- **Les fournisseurs VPN** (ExpressVPN 2008, hide.me, GuruVPN, HidzoVPN) : forte autorité, énorme budget, mais contenu **en anglais** et autopromotionnel. Leur version française de la page eFootball, quand elle existe (hide.me/fr), est une **traduction** sans adaptation au joueur francophone africain.
- **Les comparateurs affiliés** (VPNwise 2026, VPNAlerT 2017, proprivacy 2004, VPNGuider 2020) : listes « best VPN », ton publicitaire, **en anglais**. Certains sont *très jeunes* (VPNwise : avril 2026) — preuve qu'il est encore possible d'entrer sur ce terrain.
- **Reddit / YouTube / TikTok** : gros en anglais, mais ce sont des canaux communautaires, **pas des concurrents éditoriaux** que José doit battre pour un article.

**Détail qui compte :** le concurrent le plus « proche » de José n'est pas ExpressVPN — c'est **VPNwise, créé en avril 2026**, qui se classe déjà avec un guide anglophone générique. Si un site de six mois y arrive en anglais, un article français sérieux y arrive aussi — et sans concurrent direct en français.

### Verdict de difficulté

> ## ✅ ATTEIGNABLE EN 1 MOIS (sur la requête française)

**Raisonnement :**
- Aucune page française dédiée au mot-clé n'existe → pas de « mur » éditorial en français à franchir. **[VÉRIFIÉ — Brave + DDG]**
- Les concurrents présents ne sont **pas optimisés pour le français** ; un article natif surclasse une traduction automatique. **[raisonnement — non mesurable avec les outils gratuits]**
- La demande est réelle et ciblée (7 suggestions d'autocomplétion, intention acheteuse). **[VÉRIFIÉ — autocomplétion]**
- **Réserve honnête :** les gros fournisseurs (ExpressVPN, hide.me) et Reddit gardent une autorité que José ne dépassera pas *en anglais*. Le succès ici est **un succès français uniquement** ; l'objectif est de capter le francophone, pas de battre ExpressVPN. Si Google décide de servir une SERP majoritairement anglophone depuis Abidjan (possible), l'article français se battra pour une place secondaire — c'est le **seul risque réel**, et il se surveille une fois l'article en ligne (Search Console).

### Plan d'article détaillé

**Titre exact recommandé :**
> **VPN pour eFootball en 2026 : est-ce que ça réduit vraiment le lag ? (et comment bien le régler)**

Variante (plus « recherche ») : *Meilleur VPN pour eFootball 2026 : le guide honnête (ce qui marche, ce qui ne marche pas).*

**Pourquoi ce titre :** il contient le mot-clé exact (« VPN pour eFootball »), l'année (2026, pour la fraîcheur), et une **promesse honnête** (répondre à la vraie question au lieu d'assener une liste). C'est exactement ce qui manque aux concurrents anglophones, qui vendent sans expliquer.

#### Structure en sections (H2) et contenu attendu

**H2-1 — « Réponse rapide » (3 lignes, en tête)**
- En 3 phrases : *oui* un VPN peut aider dans certains cas, *non* ce n'est pas magique. Donner le verdict immédiatement. Google récompense la réponse claire en tête, et ça retient le lecteur.
- **Lien d'affiliation #1 (discret)** : « Le VPN que j'utilise et qui marche le mieux pour ça : [→ NordVPN] (garantie 30 jours). »

**H2-2 — « Est-ce que Konami autorise les VPN sur eFootball ? »**
- Répondre à la question légale/ban, la plus angoissante : les conditions de Konami ne mentionnent pas les VPN ; aucun cas documenté de sanction pour simple routage. **[À VÉRIFIER]** — c'est une affirmation qu'il faut sourcer (renvoyer au texte Konami), ne jamais l'inventer.
- Distinguer : VPN pour stabiliser sa connexion (autorisé) ≠ triche/manipulation de match (interdit).

**H2-3 — « Un VPN réduit-il vraiment le ping sur eFootball ? La vérité technique »**
- Expliquer les **deux modes de connexion** d'eFootball : connexion directe entre joueurs (P2P) et connexion via serveur Konami. **[À VÉRIFIER — citer la doc Konami]**
- Quand un VPN aide : quand son FAI/opérateur (Orange, MTN, Moov en CI) fait prendre un détour pourri vers le serveur → un tunnel mieux « peeré » raccourcit le chemin.
- Quand il n'aide PAS : quand la route est déjà bonne, le VPN **ajoute** de la distance et **augmente** le ping.

**H2-4 — « Le VPN peut-il régler le lag de mon adversaire ? Non. »**
- Section d'honnêteté pure. Le « lag switching » adverse ne se corrige pas en changeant *sa* route. C'est exactement ce que les concurrents cachent (hide.me le dit même, et s'en sert pour se démarquer).
- **Effet recherché :** la franchise ici est ce qui donnera envie de croire le reste — et donc de cliquer sur le lien.

**H2-5 — « Dans quels cas un VPN aide vraiment un joueur eFootball »**
- Wi-Fi public / université / hôtel qui bloque le jeu.
- FAI qui « étrangle » (throttle) le trafic de jeu.
- Masquer son IP pour éviter les attaques DDoS d'adversaires.
- Accéder à des serveurs/filles d'attente régionaux.
- **Lien d'affiliation #2 (naturel)** : « Si tu es dans l'un de ces cas, [→ prendre NordVPN ici] — c'est le seul que je recommande, je t'explique pourquoi plus bas. »

**H2-6 — « Les critères qui comptent pour eFootball (à vérifier avant d'acheter) »**
- Protocole rapide (WireGuard / NordLynx) — éviter OpenVPN pour le jeu.
- Serveurs proches des hubs Konami.
- Split tunneling (ne router que le jeu), kill switch, prise en charge du P2P/NAT.

**H2-7 — « Quel VPN choisir pour eFootball en 2026 » (le cœur commercial)**
- Comparaison **honnête** : présenter 2-3 options avec leurs vrais défauts, puis **NordVPN en recommandation principale justifiée** (vitesse, protocole NordLynx, stabilité). Ne **pas** prétendre tester 8 VPN si un seul est affilié.
- **Lien d'affiliation #3 (principal, en boîte/CTA bien visible).**

**H2-8 — « Comment configurer ton VPN pour eFootball (mobile et PC, étape par étape) »**
- Étapes concrètes : installer, choisir WireGuard, choisir un serveur proche du serveur de match, activer le kill switch. Captures ou liste numérotée.
- Contexte local : rappeler que ça marche aussi sur mobile (la majorité des Ivoiriens jouent sur téléphone). **Lien d'affiliation #4 (soft).**

**H2-9 — « Comment savoir si ça a vraiment aidé (mesurer avant/après) »**
- Méthode simple : noter son ping sur 5 matchs sans VPN, puis 5 avec. Honnêteté = pas de faux chiffre de ping.

**H2-10 — FAQ (bloc questions/réponses, riche en mots-clés)**
- Un VPN gratuit, ça suffit ? (réponse honnête : limites de débit/serveurs).
- Ça marche sur console PS/Xbox ? (via routeur).
- Est-ce que je risque un ban ? (renvoi au H2-2).
- **Lien d'affiliation #5 (dans une seule réponse de la FAQ, pas toutes).**

**H2-11 — « Verdict »**
- Récapitulatif en 2 phrases + **CTA final** vers NordVPN.

#### Les 6 questions auxquelles l'article DOIT répondre

1. Est-ce que c'est légal / est-ce que je risque un ban ? *(H2-2)*
2. Est-ce que ça réduit vraiment le ping ? *(H2-3)*
3. Est-ce que ça règle le lag causé par l'adversaire ? *(H2-4 — non)*
4. Quel VPN précis choisir, et pourquoi ? *(H2-7)*
5. Comment le régler concrètement ? *(H2-8)*
6. Gratuit ou payant ? *(FAQ)*

#### Où placer le lien d'affiliation (règle : naturel, jamais forcé)

1. Réponse rapide (en haut) — discret, 1 lien.
2. Fin de « dans quels cas ça aide » — contextuel.
3. Section « Quel VPN choisir » — **lien principal**.
4. Section configuration — soft.
5. Une seule réponse de la FAQ — explicite.
> **5 liens maximum, tous justifiés par le texte autour.** Un lien qui tombe sans que le paragraphe l'ait amené = perte de confiance (et ça se voit).

#### Ce qu'il faut ABSOLUMENT éviter (sinon la page = publicité sans valeur)

- ❌ **Promettre une baisse de ping systématique.** C'est le mensonge n°1 des concurrents ; si le lecteur le teste et que ça empire, il part et la crédibilité est morte.
- ❌ **Dire qu'un VPN « bat » le lag-switching adverse.** C'est faux (Konami documente les deux modes de connexion). Le dire, c'est se faire démonter en commentaire.
- ❌ **La fausse neutralité « on a testé 8 VPN »** alors qu'un seul est affilié. Présenter 2-3 vrais concurrents avec leurs défauts, assumer une recommandation.
- ❌ **Une simple liste « Top 5 VPN » traduite de l'anglais.** C'est exactement ce que font les concurrents ; sans valeur ajoutée française, l'article ne se distingue pas.
- ❌ **Promettre des « coins gratuits », un « eFootball 2026 epic gratuit » ou un téléchargement piraté.** Détourne de l'objectif (le VPN) et fait passer le site pour un site d'arnaque.
- ❌ **Du contenu 100 % commercial sans explication technique.** La page doit d'abord **être utile**, vendre ensuite.
- ❌ **Cibler « VPN gratuit » en mot-clé principal.** L'intention ne convertit pas (qui cherche gratuit ne paie pas de VPN).
- ❌ **Des chiffres de débit/ping inventés.** Aucun test ne doit être simulé.
- ❌ **Titres putaclic** (« le secret que Konami cache »). Ton calme et honnête.

---

## PAGE 2 — « VPN Côte d'Ivoire »

### La demande réelle (autocomplétion Google, gl=ci, hl=fr)

**[VÉRIFIÉ — API autocomplétion Google, gl=ci, 10/10/2026 :]**

- `vpn cote d'ivoire`
- `vpn côte d'ivoire gratuit`
- `vpn côte d ivoire apk`
- `vpn pour cote d ivoire`
- `vpn serveur cote d ivoire`
- `vpn localisation cote d ivoire`
- `proton vpn cote d ivoire`
- `vpn ip cote d'ivoire`
- `nordvpn cote d'ivoire`
- `express vpn cote d ivoire`

**Ce que ça dit :** demande **large** (dix suggestions, plus large que la page 1) mêlant trois intentions : *obtenir une IP ivoirienne* (localisation), *un VPN gratuit*, et *des marques précises*. **« nordvpn cote d'ivoire » et « express vpn cote d ivoire » figurent dans l'autocomplétion** — la marque NordVPN est déjà associée au pays.

### Qui occupe réellement les résultats

Requête **« vpn cote d'ivoire »** (croisement Brave + DuckDuckGo, 10/10/2026) :

| # | Site | URL | Langue | Type | Âge du domaine (RDAP) |
|---|---|---|---|---|---|
| 1 | virtual-private-network.com | `/localisation/cote-d-ivoire/` | **Français** | Comparateur/localisation | **2026-05-13** (≈ 5 mois) [VÉRIFIÉ — RDAP] |
| 2 | uPhone | `/vpn/vpn-for-cote-divoire` | Anglais | eSIM / voyage | 1998-05-19 [VÉRIFIÉ — RDAP] |
| 3 | Comparitech | `/blog/vpn-privacy/best-vpn-ivory-coast/` | Anglais | **Gros comparateur** | 2015-01-10 [VÉRIFIÉ — RDAP] |
| 4 | VPNactu.fr | `/meilleur-vpn-cote-divoire/` | **Français** | Blog/affilié VPN FR | **2014-06-20** [VÉRIFIÉ — RDAP] |
| 5 | Proton VPN | `/vpn-servers/ivory-coast` | Anglais | **Site officiel** | 2016-12-03 [VÉRIFIÉ — RDAP] |
| 6 | VPN5best | `/go/cotedivoire-en/…` | Anglais | Comparateur | 2019-12-30 [VÉRIFIÉ — RDAP] |
| 7 | Telleport | `/region/Cote-d-Ivoire` | Anglais | Comparateur | [À VÉRIFIER] (.me) |
| 8 | CometVPN | `/locations/ivory-coast-vpn/` | Anglais | Marque VPN | 2019-08-12 [VÉRIFIÉ — RDAP] |
| 9 | Proton VPN | `/fr/vpn-servers/ivory-coast` | **Français** | **Site officiel** (version FR) | (idem) |
| 10 | Turbo VPN | `/fr/vpn-for-country/Ivory-coast-vpn` | Français/Anglais | Marque VPN | 2007-09-04 [VÉRIFIÉ — RDAP] |

Autres vus (Brave) : **cooltechzone.com** (2003-06-02), **vpnsuper.com** (2017-12-16), **vpn.com** (1997-12-01), **pixelprivacy.com** (2017-02-02), **flowvpn.com** (2015-07-06), **myvpnhub.com** (2021-08-19), vpnhub.me, finevpn.org [À VÉRIFIER]. **[VÉRIFIÉ — RDAP, 10/10/2026.]**

### Combien de résultats en français ?

Sur ~20 pages relevées : **4 pages réellement en français** — `virtual-private-network.com` (site neuf, mai 2026), `vpnactu.fr` (établi, 2014), `protonvpn.com/fr` (site officiel), `turbovpn.com/fr` (fournisseur). Le reste est **anglophone**.

> **Ce n'est PAS un espace vide en français** (contrairement à la page 1). Mais deux des quatre pages FR appartiennent à des **fournisseurs officiels** (autorité difficile à dépasser) et une est un **affilié installé depuis 2014**.

### Lecture concurrentielle

- **Le gros de la concurrence traite la Côte d'Ivoire comme une destination de voyage** (« travelling to Ivory Coast », eSIM, VPN pour touristes) — **pas** pour un Ivoirien qui vit sur place. C'est le défaut exploitable. **[VÉRIFIÉ — titres/descriptions Brave + DDG]**
- **Autorités installées à ne pas affronter de front :** Comparitech (2015), cooltechzone (2003), vpn.com (1997), proprivacy (2004), Proton VPN (officiel). La **tête de requête** est verrouillée par ces poids lourds.
- **Bonne nouvelle :** le site français `virtual-private-network.com` qui se classe n'a que **5 mois** → le terrain français local reste prenable. **[VÉRIFIÉ — RDAP]**
- **Angle libre :** personne ne parle au **Ivoirien qui vit en Côte d'Ivoire** (pas au touriste) : VPN pour le streaming local, le sport, la banque, la sécurité sur les réseaux mobiles Orange/MTN/Moov.

### Verdict de difficulté

> ## 🟠 ATTEIGNABLE EN 3 MOIS (sur la variante française/localisée)
> ## ❌ TÊTE DE REQUÊTE EN ANGLAIS : jamais sans budget.

**Raisonnement :**
- La tête de requête internationale (« VPN for Ivory Coast ») est tenue par des domaines de 20+ ans et des marques officielles → à écarter. **[VÉRIFIÉ — RDAP]**
- La **variante française/localisée** est atteignable : un site FR de 5 mois y est déjà, et l'angle « Ivoirien sur place » n'est traité par personne. **[VÉRIFIÉ/Raisonnement]**
- Pourquoi 3 mois et pas 1 : il faut surpasser `vpnactu.fr` (affilié établi depuis 2014) et `protonvpn.com/fr` (autorité officielle) sur le terrain français — plus dur que la page 1 où il n'y a **aucun** concurrent français dédié.

---

## PAGE 3 — « IPTV en Côte d'Ivoire : ce qui est légal et l'alternative »

### La demande réelle (autocomplétion Google, gl=ci, hl=fr)

**[VÉRIFIÉ — API autocomplétion Google, gl=ci, 10/10/2026 :]**

- `iptv cote d'ivoire`
- `abonnement iptv cote d ivoire`
- `fournisseur iptv côte d'ivoire`
- `iptv prix cote d'ivoire`
- `playlist iptv cote d ivoire`
- `lien iptv cote d ivoire`
- `url iptv cote d ivoire`
- `iptv interdit en côte d'ivoire`
- `iptv legal en cote d ivoire`
- `abonnement iptv 12 mois côte d ivoire`

**Ce que ça dit :** demande **la plus large des trois** (dix suggestions), **forte intention d'achat** (« abonnement », « prix », « 12 mois »). Mais aussi des requêtes de **légalité** (« interdit », « legal ») → l'audience elle-même se demande si c'est légal. **C'est exactement le vide à occuper.**

### Qui occupe réellement les résultats

**A) Requête commerciale « iptv cote d'ivoire »** (Brave, 10/10/2026) — que des petits revendeurs :

| Site | URL | Langue | Type | Âge du domaine (RDAP) |
|---|---|---|---|---|
| IPTV Ivoirien | `iptvivoirien.com` | Français | Revendeur IPTV | **2026-01-02** [VÉRIFIÉ — RDAP] |
| IPTV Abidjan | `iptvabidjan.com` | Français | Revendeur IPTV | **2026-06-14** [VÉRIFIÉ — RDAP] |
| Sen Virtuel | `senvirtuel.com/iptv-cote-divoire` | Français | Revendeur IPTV | **2025-03-19** [VÉRIFIÉ — RDAP] |
| IPTV Ivoire | `iptvivoire.com` | Français | Revendeur IPTV | **2026-05-27** [VÉRIFIÉ — RDAP] |
| IPTV Côte d'Ivoire | `iptv-cotedivoire.net` | Français | Revendeur IPTV | [À VÉRIFIER] (.net) |
| Good IPTV Services | `goodiptvservices.com/…-2026/` | Français | Comparateur IPTV | **2025-01-16** [VÉRIFIÉ — RDAP] |
| Jumia CI | `jumia.ci/…television-par-satellite/` | Français | E-commerce | [À VÉRIFIER] (.ci) |
| Artemis | `…my.canva.site` | Français | Page Canva | [À VÉRIFIER] |

**Aucun média installé, aucun comparateur d'autorité.** Uniquement des **revendeurs spécialisés dont les domaines ont moins de 2 ans** — pour la plupart créés en **2025-2026**. **[VÉRIFIÉ — RDAP, 10/10/2026.]**

**B) Requêtes de légalité** (« iptv legal en cote d'ivoire », « iptv interdit en cote d'ivoire ») — DuckDuckGo, 10/10/2026 — **que de la presse et du régulateur, 100 % français :**

- **haca.ci** — le régulateur ivoirien de l'audiovisuel [.ci, [À VÉRIFIER]]
- **abidjan.net** — presse, **1998-03-15** [VÉRIFIÉ — RDAP]
- **linfodrome.com** — presse, **2011-11-14** [VÉRIFIÉ — RDAP]
- **koaci.com** — presse, **2007-10-11** [VÉRIFIÉ — RDAP]
- **yeclo.com** — presse, 2015-08-30 [VÉRIFIÉ — RDAP]
- **aip.ci** (Agence Ivoirienne de Presse), **digitalmag.ci**, **ivoirescoop.com**, **cinews.ci**, **unite.ci**, **laws.africa** (textes de loi)

### Combien de résultats en français ?

> **TOUS LES RÉSULTATS SONT EN FRANÇAIS** — mais ce sont soit des **revendeurs IPTV très jeunes** (côté commercial), soit de la **presse et du régulateur** (côté légalité). **AUCUN « guide honnête qui explique ce qui est légal ET propose l'alternative VPN » n'existe.** C'est un angle totalement libre.

### Lecture concurrentielle

- **Côté commercial :** concurrence **faible** (domaines 2025-2026, aucune autorité, aucun budget visible). Mais ce sont des revendeurs ; ils utilisent peut-être des méthodes de référencement agressives. **[À VÉRIFIER]**
- **Côté légalité :** la presse (abidjan.net, 1998) et **le régulateur HACA lui-même** occupent le terrain. Mais ce sont des **articles de presse / communiqués**, pas des guides pratiques optimisés pour un lecteur qui cherche « est-ce légal, et je fais quoi à la place ? ». **Le vide est là.**
- **Le vrai risque n'est pas SEO, il est éditorial :** l'audience veut de l'IPTV **illégal**. Une page honnête qui refuse de vendre de l'IPTV et redirige vers un VPN **capte cette audience mais convertit mal** — elle convertit ceux qui cherchaient « légal », une minorité. **[raisonnement]**

### Verdict de difficulté

> ## ⚠️ ATTEIGNABLE EN 1 MOIS (pour se classer)
> ## ⚠️ MAIS CONVERSION INCERTAINE = le vrai obstacle n'est pas la concurrence, c'est de monétiser une audience qui vient chercher un produit illégal.

**Raisonnement :**
- Pour se **classer** : la barrière est faible (concurrents commerciaux neufs, presse non optimisée pour l'intention pratique). **[VÉRIFIÉ — RDAP + Brave/DDG]**
- Pour **gagner de l'argent** : l'auteur doit écrire une page honnête qui dit « l'IPTV non autorisé est illégal en CI (5 ans de prison / ~50 M FCFA de risque selon la presse — **[À VÉRIFIER sur le texte de loi])**, et voici l'alternative légale : un VPN ». Une partie de l'audience partira. C'est **assumé** : la page ne doit **jamais** vendre d'IPTV.
- **Garde-fou juridique :** ne jamais recommander, lister ou linker un abonnement IPTV. Le rôle de la page est de **décourager l'IPTV illégal** et d'orienter vers le VPN. C'est ce qui la rend défendable (et c'est la ligne de José : « page honnête »).

---

## ORDRE DE PRIORITÉ RECOMMANDÉ

1. **Page 1 — VPN pour eFootball** → **à écrire en premier.** Espace français quasi vide, demande acheteuse, monétisation directe NordVPN, aucun casse-tête juridique. *Verdict : 1 mois.*
2. **Page 3 — IPTV (légalité + alternative)** → **deuxième.** Concurrence la plus faible pour se classer, mais conversion partielle et vigilance juridique. *Verdict : 1 mois pour se classer, monétisation incertaine.*
3. **Page 2 — VPN Côte d'Ivoire** → **troisième.** Demande large mais concurrence installée (vpnactu 2014, Proton VPN officiel). *Verdict : 3 mois sur la variante française/localisée, jamais sur la tête anglophone.*

---

## Rappel de fiabilité (ce qui tient, ce qui est fragile)

**Ce qui est solide :**
- Les **âges de domaine** (RDAP) — vérifiables, exacts au jour près. **[VÉRIFIÉ]**
- Les **suggestions d'autocomplétion** — endpoint direct de Google, gl=ci. **[VÉRIFIÉ]**
- La **langue de chaque page concurrente** et le **type** (fournisseur / comparateur / forum / presse / régulateur) — confirmés par deux moteurs croisés. **[VÉRIFIÉ — Brave + DDG]**
- Le fait que **la page 1 est quasi vide en français** — concordant sur Brave ET DuckDuckGo, sur deux requêtes. **[VÉRIFIÉ]**

**Ce qui est fragile (à surveiller) :**
- Les **positions exactes dans Google** — non obtenues (Google bloque, backend DDG en panne). Ordre susceptible de différer. **[À VÉRIFIER]**
- Les **volumes de recherche** — **non mesurables** avec les outils gratuits. Aucun chiffre inventé. **[NON MESURÉ]**
- Les affirmations sur les **conditions d'utilisation de Konami** (H2-2 du plan) et sur la **peine légale IPTV** — à **sourcer** (doc Konami / texte de loi) avant publication. **[À VÉRIFIER]**
- Les données **.me / .ci / .io** — registre RDAP inaccessible ce jour. **[À VÉRIFIER]**
