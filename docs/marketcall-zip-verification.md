# VÉRIFICATION ZIP TARGETING MarketCall — Diagnostic (19/08/2026)

**Offre :** #12330 "Water Damage Bundle | Inbounds | Static RTB Only | Pre-Approval"
**Source :** Google Sheet des ZIP ciblés (624 ZIP, Californie uniquement)
**Fichier de référence :** `/tmp/marketcall_zips.csv` (export du 19/08/2026)

## ✅ VERDICT : TOUT EST CONFORME — AUCUNE ACTION NÉCESSAIRE

### 1. Couverture des 31 villes du site
Les 31 pages villes CA sont toutes couvertes par les ZIP de l'offre.

⚠️ **Piège de noms** (à connaître pour les futures vérifications) :
- "Commerce" apparaît dans le sheet comme **"City Of Commerce"** (ZIP 90040) → COUVERT
- "East Los Angeles" (90022), "Los Angeles" (90023/90041) couvrent aussi des zones adjacentes
- Ne jamais comparer par NOM de ville — comparer par ZIP

### 2. Disclaimers exigés par l'offre
Les 3 sont présents dans `src/layouts/Layout.astro` (footer) :
- ✅ "free service to assist homeowners..." (obligatoire)
- ✅ "Same-day and 24/7 emergency services are subject to..." (obligatoire car on utilise "24/7")
- ✅ "Affiliate Disclosure" (bonne pratique FTC)

### 3. Conformité trafic
- ✅ Trafic autorisé : SEO, Paid Search (le site est du SEO pur)
- ❌ Interdit : GMB, SMS, Facebook Marketplace, Craigslist → ne JAMAIS utiliser ces canaux pour cet offre

### 4. Rappel des règles d'appel (pour ne pas se faire refuser)
- Durée minimale : **120 secondes**
- Horaires : 10:00 - 02:00 EST (lundi-dimanche)
- Qualifié : client intéressé par un service water damage dans la zone (PAS service client/billing)
- Hold period : 7 jours (les appels apparaissent avec retard — normal)

## 🚨 NE PAS TOUCHER À LA PAGE COMMERCE
La page `water-damage-repair-commerce-ca.astro` est conforme (ZIP 90040 couvert).
Ne pas la supprimer, ne pas la modifier pour ça.

## Contexte de l'offre (état 19/08)
- L'offre était en pause "caps filled" (cap réseau rempli — normal, pas un problème)
- Reprise automatique : 19/08/2026 16:00 (UTC+02:00)
- Payout : $374.99 par appel qualifié
