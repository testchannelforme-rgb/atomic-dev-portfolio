# Atomic.Dev

Independent app portfolio for GridHQ, Still, and LEFT. A dependency-free static website hosted by the existing Vercel project `atomic-dev-portfolio`.

Only `public/` is published. There are no user accounts, admin routes, APIs, forms, database clients, runtime package dependencies, or required environment variables. GitHub and Vercel account access control is the administrative boundary.

## Development and validation

```sh
python3 scripts/dev_server.py
```

Open `http://127.0.0.1:8765`. The development server applies the production headers for browser testing; it is not deployed.

```sh
python3 scripts/security_check.py
node --check public/assets/site.js
```

After editing `public/assets/site.js`, run `python3 scripts/update_integrity.py`, then the checks above. Script changes must update both the SRI attribute and the CSP hash. The hash is not a credential. Do not add `unsafe-inline` or `unsafe-eval` to make a change work.

The CI workflow checks public files, CSP/SRI, links, JavaScript syntax and reachable Git history with Gitleaks v8.30.1. The scanner archive is pinned to its verified SHA-256. GitHub Actions checkout is pinned by commit and has only read permissions; checkout credentials are not persisted.

## Content and design

- The three apps have their own sections and dedicated screenshot galleries. The Still and LEFT panels are labelled app previews.
- The GridHQ device displays the supplied actual app screenshot unchanged in a landscape frame. Still and LEFT retain labelled interactive examples. The GridHQ gallery has six supplied screenshots; Still and LEFT have five each. Tap an app name to open its gallery.
- Buy Me a Coffee, Reddit, Instagram, GitHub and Discord links are prominent; the hero also has a Get GridHQ button.
- GridHQ uses the exact red/white G logo supplied in the latest review.
- Preview handles support bounded pointer dragging and keyboard arrows; reduced motion disables movement. Study tasks and the budget breakdown respond to taps without saving data. GridHQ opens its actual screenshot gallery.
- Galleries support full-size viewing, Previous/Next, arrow keys, Escape, focus return and horizontal touch swipes. Without JavaScript, screenshots open directly.
- GridHQ's button links to the current public release. The page displays V2.2.1 based on the verified release asset, not the planned V3.2 release.
- Reviews are excerpts from the three screenshots supplied by the developer; there are no fabricated ratings.
- Space Grotesk is self-hosted. Its SIL Open Font License is included in `public/assets/space-grotesk-OFL.txt`.
- Superdesign's scroll-animation example inspired the central expanding shape and app connections: https://superdesign.dev/library/scroll-animation. The site's code and Still/LEFT examples were written for this portfolio; GridHQ uses the supplied logo and real app screenshot.
- `/privacy` and `/terms` describe this website. They do not substitute for the apps' own policies.

## Security maintenance

See `SECURITY_AUDIT.md`. No third-party executable scripts or visitor tracking are loaded by the site. The original external analytics script was removed; analytics tracking therefore stops unless an approved integration and its CSP requirements are deliberately reintroduced.

Future APIs, login flows or databases require a new security design. Do not add browser-side secrets or a client-only admin check. Deployments of those features must include server-enforced authentication, per-resource authorisation, input validation, shared-store rate limiting, and narrowly scoped credentials. Add them only when those features exist.

## Source package and publication

The reviewed ZIP is a source handoff, with no Git metadata or credentials included. To run the full history scan, put these files in a full checkout of the existing repository; the standalone ZIP has no history to scan. The old root `index.html` is intentionally removed in this change. Use `public/index.html` with the included Vercel configuration. GitHub integration upload was denied with HTTP 403; source/CI and production publication remain pending repository access. The preview demonstrates the completed design without replacing the production website.
