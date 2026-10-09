# Verification evidence

9 October 2026, before deployment. The user story is: a visitor opens Atomic.Dev, explores GridHQ/Still/LEFT, reads genuine GridHQ feedback, and follows download/community links. There is no client-to-API or API-to-database boundary in this site.

| Check | Result |
| --- | --- |
| Strict script CSP, matching SRI, self-hosted variable font | Passed in Chromium with headers enforced |
| Normal-motion reveals, scroll progress and hero expansion | Passed without runtime or CSP errors |
| Responsive layouts | Passed at 1440, 1024, 768, 390 and 320 pixels; no horizontal page overflow |
| Mobile navigation | Open/close, Escape, focus return and anchor-close passed |
| Reduced-motion preference | Animations stop and reveal-dependent content stays visible |
| JavaScript disabled | All three product sections and reviews remain visible |
| Website privacy / terms | Both pages return 200 and render their headings in local QA |
| XSS sink control | Enforced Trusted Types rejected an untrusted `innerHTML` assignment; a query-string payload was not rendered |
| Source and config guard | Deployment boundary, allowed files, links, CSP/SRI and unsafe DOM/runtime capability checks passed |
| Gitleaks v8.30.1 | No leaks found in reachable Git history or current files; archive checksum verified |
| Branding | Prohibited game name absent from all public text assets; historical commits were preserved |
| Reviews | Three supplied messages excerpted and attributed, without fabricated star ratings |
| Downloads | GridHQ latest release and V2.2.1 APK ZIP confirmed using GitHub release metadata |

Full-page desktop and mobile screenshots were visually inspected. Preview illustrations are explicitly labelled as illustrative or in-development concepts. Local browser testing used production security headers, not disabled browser web security. An initial 320px decorative overflow was fixed and the complete checks rerun successfully.

Production checks must confirm the deployed commit, HTML, approved script hash, header values, static assets, and HTTP 404 for sensitive/unimplemented paths. The final delivery reports the outcome of those checks. `SECURITY_AUDIT.md` identifies rate-limit configuration and account/branch-control limitations separately.

## Hosted preview verification

Vercel preview `dpl_6VUDxw1guAtY563U5Nt1ouAzcmpz` reached READY. Its homepage, JavaScript, CSS, font, favicon and social image match the tested local bytes exactly. All configured header values, including the fixed-origin CORS override, were verified on the hosted response. Privacy and Terms return 200. The environment file, Git config, admin/API-looking paths, source scripts, Vercel config, package manifest, audit report and an unknown path all return 404. The preview was accessed through a temporary authenticated review link; deployment protection was not disabled.

GitHub denied the source upload, so production publication and CI installation remain pending. The audit report records this access limitation.

## Review update: links, branding and app galleries

The home page now exposes all original destinations clearly, including Buy Me a Coffee, Reddit, Instagram, GitHub and Discord; GridHQ's release link is also in the hero. The supplied GridHQ wordmark replaces the invented mark. Dedicated galleries contain five actual screenshots for each app, recovered from the developer's shared files. Home-page example interfaces remain labelled separately from actual screenshots.

Browser checks passed for GridHQ sample tabs, Still task toggles, LEFT breakdown, all three preview drag handles and reset on release, gallery image loading, Previous/Next, arrow keys, Escape and focus restoration. Homepage checks passed at 1440, 1024, 768, 390 and 320 pixels; galleries passed at 1440, 768, 390 and 320, with no horizontal page overflow. Reduced motion hides drag controls. Source/CSP/SRI guards and JavaScript syntax passed.

Updated protected preview `dpl_8m7LmTZ3YPQDixA3fP7BT7gRfv9d` reached READY. All four page routes, JS, CSS, GridHQ wordmark and all 15 gallery screenshots match tested local bytes and configured security headers. Sensitive paths return 404. Production and the GitHub source remain pending the user's Termux publication step.

## Latest supplied GridHQ assets

The developer corrected the GridHQ logo and supplied the current app standings screenshot. Both deployed assets are byte-for-byte copies of these uploads. The illustrative GridHQ interface, invented example driver data and sample-tab JavaScript were removed. A landscape device frame preserves the complete screenshot without stretching or clipping its standings columns. The newest screenshot is first in the six-image GridHQ gallery.

Browser checks passed for the actual image, floating device animation, bounded dragging/reset, the existing Still/LEFT controls, all galleries, keyboard navigation, full-size viewing, reduced motion and responsive layouts. Mobile touch dragging and horizontal gallery swiping passed. Security and JavaScript syntax checks passed. The existing Superdesign-inspired hero expansion, floating orbit cards and scroll reveals remain in place.

Preview `dpl_Ge6o66ZusESJy9z8MpePB2QnFZjL` reached READY. Four page routes, approved JavaScript, CSS, supplied logo and current standings image match local files and configured security headers. Production publication remains pending.
