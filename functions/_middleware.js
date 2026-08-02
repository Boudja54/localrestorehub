// functions/_middleware.js
// Cloudflare Pages middleware — forces all traffic to www.localrestorehub.com
// - localrestorehub.pages.dev  → 301 → https://www.localrestorehub.com/<path>
// - localrestorehub.com        → 301 → https://www.localrestorehub.com/<path>
export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname;

  if (host === 'localrestorehub.pages.dev' || host === 'localrestorehub.com') {
    return Response.redirect(
      'https://www.localrestorehub.com' + url.pathname + url.search,
      301
    );
  }

  return context.next();
}
