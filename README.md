# LocalRestoreHub.com 🏠

**Local Water Damage & Mold Remediation Directory — 24/7 US Response**

An SEO-optimized static directory website built with [Astro](https://astro.build) + [Tailwind CSS](https://tailwindcss.com), deployable to Cloudflare Pages.

## Tech Stack

- **Framework:** Astro v7 (static output)
- **Styling:** Tailwind CSS v4
- **Content:** Markdown city pages + centralized JSON data
- **Hosting:** Cloudflare Pages (via GitHub)

## Project Structure

```
src/
├── layouts/
│   └── Layout.astro          # Main layout (header, footer, SEO meta)
├── pages/
│   ├── index.astro           # Homepage
│   ├── about.astro           # About page
│   ├── contact.astro         # Contact page
│   ├── privacy-policy.astro  # Privacy Policy
│   ├── terms-of-service.astro# Terms of Service
│   └── cities/               # City pages (Markdown)
│       ├── ocala-fl.md
│       ├── tyler-tx.md
│       └── lima-oh.md
├── data/
│   └── cities.json           # City data (source for new pages)
└── styles/
    └── global.css            # Tailwind imports + custom theme
```

## Adding New City Pages

1. Add city data to `src/data/cities.json`
2. Create a new `.md` file in `src/pages/cities/` using the existing pages as template
3. Run `npm run build` to generate static files

## Development

```bash
npm run dev     # Start dev server
npm run build   # Generate static output to dist/
npm run preview # Preview built output
```

## Deployment

The `dist/` folder can be deployed to any static host. For Cloudflare Pages:
1. Connect your GitHub repo
2. Set build command: `npm run build`
3. Set build output: `dist/`
