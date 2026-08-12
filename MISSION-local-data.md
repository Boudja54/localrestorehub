# MISSION : Données chiffrées locales par ville (anti-doorway renforcé)

**Source :** audit de l'agent veille (12/08/2026) + validation Bouj
**Objectif :** ajouter 2-3 données chiffrées VRAIES par page ville pour sortir définitivement de la zone doorway 🟡 → 🟢

## Données à ajouter par ville (dans le CONTEXT ou un bloc dédié)

1. **Jours de pluie moyens / précipitations annuelles** (en pouces ou inches)
2. **Risque d'inondation FEMA** (flood zone / risk rating — Low/Moderate/High)
3. **1 donnée locale unique** au choix :
   - Âge médian du bâti (housing stock era)
   - Type de sol dominant (clay, sand, loam)
   - Quartiers à risque (flood-prone areas)
   - Classement/particularité locale (ex: ville la plus dense du comté)

## Sources de données fiables (vérifier AVANT d'écrire)

- **FEMA Flood Map Service Center** : https://msc.fema.gov/portal/search → rechercher par ville/zip
- **NOAA / National Weather Service** : https://www.weather.gov/ (climatologie locale)
- **Weather Spark** : https://weatherspark.com/y/[ville] (moyennes annuelles fiables)
- **US Climate Data** : https://www.usclimatedata.com/
- **City-Data.com** : https://www.city-data.com/city/[ville]-California.html (âge du bâti, sols, infos démographiques)
- **Google via browser_navigate** (si bloqué : r.jina.ai ou Bing)

## Règles

1. ✅ Données VRAIES vérifiées — jamais inventées. Si une donnée n'est pas trouvée : écrire une phrase qualitative factuelle (ex: "heavily paved terrain" déjà validé)
2. ✅ Chaque ville doit avoir des chiffres DIFFÉRENTS (c'est le but)
3. ✅ Insérer dans `const CONTEXT = "..."` ou un nouveau bloc dédié après le CONTEXT
4. ❌ Ne pas gonfler : 2-3 données max par page, pas 300 mots
5. ✅ Vérifier l'unicité après : `for f in src/pages/water-damage-repair-*.astro; do grep -o 'const CONTEXT = "[^"]*"' "$f" | cut -d'"' -f2; done | sort | uniq -d` → vide
6. ✅ Rebuild : `npm run build` → 34 pages
7. ✅ Commit + push

## Pages concernées (29 villes CA)
Toutes les pages `src/pages/water-damage-repair-*.astro` — les 14 déjà réécrites doivent juste GAGNER les chiffres, les 15 autres (Acton, Agoura Hills, Bardsdale, Castaic, Commerce, Elizabeth Lake, Fillmore, Juniper Hills, Littlerock, Moorpark, Piru, Santa Paula, Somis, Valyermo, Vernon) doivent avoir INTRO + CONTEXT uniques ET chiffres.

## Vérification finale
- `npm run build` OK
- `uniq -d` sur les CONTEXT → vide
- Au moins 2 villes avec des données chiffrées visibles
- Git commit + push → Cloudflare republie auto
