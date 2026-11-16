# Round 6 — Boost SEO GSC LocalRestoreHub

**Date :** 11 novembre 2026
**Cible :** 9 pages déjà en position 5-20 (page 1-2 Google) mais sans contenu enrichi
**Objectif :** pousser ces pages en top 5 → CTR ×10 (site : 4746 impressions, 4 clics, pos. moy. 34.5)
**Statut global :** ✅ DÉPLOYÉ ET VÉRIFIÉ EN PROD

## Commits

| Commit | Contenu |
|---|---|
| `080b52c` | Boost principal : 9 pages, 171 insertions, 0 suppression |
| `4421e9e` | Fix wording horaires Arcadia (« from … to ») |
| `0ca289e` | Fix wording horaires Azusa (« from … to ») ← **HEAD / dernier déployé** |

## Tableau des 9 pages

| # | Ville | ZIP | Position GSC | H2 24h | Angle de contenu (ancré sur le CONTEXT réel) |
|---|---|---|---|---|---|
| 1 | Camarillo | 93010 | 15.6 (51 imp) | 24-Hour Flood Cleanup | Parcelles agricoles/ranch : longs runs privés, puits, réseaux d'irrigation hors de vue + nappe remontant sous la Pleasant Valley drainée par Calleguas Creek |
| 2 | Duarte | 91009 | 12.3 (25 imp) | 24-Hour Flood Cleanup | Double source : ruissellement chargé de débris depuis Fish Canyon / Duarte Wash sur les rues en terrasses + drainages d'origine de 80-100 ans des bungalows Route 66 |
| 3 | Covina | 91722 | 14.3 (15 imp) | 24-Hour Water Damage Restoration | Héritage agrumicole : anciens réseaux d'irrigation dans le même sol que les laterals d'argile, racines des arbres matures + spreading grounds de la San Gabriel River à l'ouest |
| 4 | Azusa | 91702 | 8.8 (14 imp) | 24-Hour Flood Cleanup | Bouche du San Gabriel Canyon : ruissellement sur les petits lots en pente + sol alluvial profond qui transporte une fuite latéralement sur 20 pieds |
| 5 | Santa Ana | 92701 | 7.9 (10 imp) | 24-Hour Flood Cleanup | Grille historique dense : fourplex Spanish Colonial à murs partagés, allées arrière, fuite vers l'unité voisine avant l'appel ; la Santa Ana River en limite ouest |
| 6 | Midway City | 92655 | 17.5 (10 imp) | 24-Hour Water Damage Restoration | Nappe haute / quasi zéro pente : drains et laterals sans dénivelé, refoulement dans garages, carports et extensions basses ; East Garden Grove-Wintersburg Channel + Bolsa Chica |
| 7 | Artesia | 90702 | 7.5 (8 imp) | 24-Hour Water Damage Restoration | Lots étroits de l'ère laitière : garages détachés, hangars et patios coulés avant les codes, service + lateral passant SOUS ces dalles → fuite invisible, facture qui monte |
| 8 | Arcadia | 91006 | 5.3 (7 imp) | 24-Hour Flood Cleanup | Santa Anita Wash + bassins à débris sous les contreforts : débordement sur les rues en pente ; maisons 1920-1950 avec drains d'origine sous parquets massifs |
| 9 | Lawndale | 90260 | 8.7 (6 imp) | 24-Hour Emergency Water Extraction | 12.82 in de pluie / 35.7 jours humides, limon sableux au drainage irrégulier d'un bloc à l'autre, bâti médian 1963, Zone X |

Chaque page contient :
- 1 paragraphe unique (~100 mots) mentionnant le ZIP réel et « 10:00 AM to 2:00 AM »
- 1 H2 « [Ville] Water Damage FAQ » + 3 Q/R uniques (H3 nommant la ville)
- 0 modification de TITLE / DESC / INTRO / CONTEXT / disclaimer / numéro de tracking

## Vérifications (toutes passées)

| Vérif | Résultat |
|---|---|
| Doublons H3 (`grep … uniq -d`) sur 94 pages | **0** |
| Jaccard blocs round 6 (36 paires, mots >3 lettres, nom de ville retiré) | **max 0.25** (Duarte / Arcadia) — 0 paire > 0.30 |
| Jaccard vs les 24 pages des rounds 1-5 (528 paires) | **max 0.26** (Lawndale / Moorpark) — 0 paire > 0.30 impliquant le round 6 |
| Termes interdits (mold / moisissure / sewage) sur les 9 pages | **0** |
| Suppressions dans le diff (`git diff --numstat`) | **0** (171 insertions, 0 suppression) |
| Liens `tel:+18448331048` (dist) | **4 par page** |
| Disclaimer « actors or models » (dist + prod) | **présent sur les 9** |
| Canonical www | **OK** |
| `npm run build` | **OK — 99 pages** |
| Vérif prod `curl` des 9 pages (nouveau H2 + ZIP + horaires + FAQ) | **9/9 OK** |

## Statut prod (après déploiement Cloudflare Pages)

| Page | H2 détecté en prod |
|---|---|
| /water-damage-repair-camarillo-ca/ | 24-Hour Flood Cleanup in Camarillo ✅ |
| /water-damage-repair-duarte-ca/ | 24-Hour Flood Cleanup in Duarte ✅ |
| /water-damage-repair-covina-ca/ | 24-Hour Water Damage Restoration in Covina ✅ |
| /water-damage-repair-azusa-ca/ | 24-Hour Flood Cleanup in Azusa ✅ |
| /water-damage-repair-santa-ana-ca/ | 24-Hour Flood Cleanup in Santa Ana ✅ |
| /water-damage-repair-midway-city-ca/ | 24-Hour Water Damage Restoration in Midway City ✅ |
| /water-damage-repair-artesia-ca/ | 24-Hour Water Damage Restoration in Artesia ✅ |
| /water-damage-repair-arcadia-ca/ | 24-Hour Flood Cleanup in Arcadia ✅ |
| /water-damage-repair-lawndale-ca/ | 24-Hour Emergency Water Extraction in Lawndale ✅ |

Vérifié avec cache-buster `?cb=<timestamp>` (contournement du cache edge CF).

## Scripts

- `scripts/boost_round6.py` — injecteur idempotent (skip si « Water Damage FAQ » déjà présent), vérifie que TITLE/DESC restent identiques
- `scripts/check_boost_round6.py` — gate Jaccard sur les blocs injectés (exit 1 si paire > 0.30)

## Point d'attention (hors périmètre round 6)

Le scan Jaccard complet des 33 pages boostées révèle **18 paires > 0.30 entre pages des rounds 1-5** (aucune n'implique une page du round 6). Les plus fortes :

- Downey / El Segundo — 0.40
- Bell / South Gate — 0.37
- Commerce / Santa Paula — 0.37
- Fillmore / Piru — 0.37
- Commerce / Vernon — 0.36

Ces blocs datent des rounds 1-2 (avant la mise en place du gate). Recommandation : **round 7 de réécriture ciblée** sur ces ~8 pages, en changeant l'angle factuel (pas le vocabulaire). Risque doorway réel mais modéré — priorité plus basse que l'indexation/clics.

## Prochaine étape suggérée

1. Attendre 10-14 jours puis comparer avec un **export GSC frais** (`python3 scripts/gsc_export_diff.py <ancien.zip> <nouveau.zip>`) — vérifier le hash md5 pour ne pas réanalyser le même fichier.
2. Booster les pages qui montent naturellement (méthode validée 5 fois : Downey 23 → 64 impressions).
3. Round 7 = réécriture des 8 pages héritées du point d'attention ci-dessus.
