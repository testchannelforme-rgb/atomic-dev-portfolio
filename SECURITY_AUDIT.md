# Atomic.Dev website security audit

Audit date: 9 October 2026. Target: `testchannelforme-rgb/atomic-dev-portfolio`, hosted by the existing Vercel project `atomic-dev-portfolio` in team `atomic-dev2`.

## Verified scope

The production deployment initially matched GitHub `main` commit `1c84304625e6799b5a817bb47330cb7340eab471`. Its source was a single static `index.html` file. There was no backend framework, dependency manifest, API directory, login system, admin route, form handler, password store, database connection, or application environment-variable reference. The Vercel project environment-variable listing returned an empty array and `hiddenProductionEnvCount: 0`.

## Results and changes

| Area | Finding / implemented control |
| --- | --- |
| API keys and environment variables | No credential candidates were found in the site source or reachable history. No project environment variables were configured. No keys were created or copied into browser code. |
| Authentication and admin access | This portfolio has no application admin or login route. Website edits are controlled by GitHub/Vercel account access. Public visitors can access only public static content. Adding a login would introduce a new feature requiring its own server-side design. |
| Object / role authorisation | No user records, private objects or per-user routes exist. No client-side authorisation claims were introduced. |
| Input, forms and XSS | No user input is processed. Removed inline executable code and inline CSS. Added a hash-based script CSP with `strict-dynamic`, matching SRI, denied inline handlers and evaluation, and enforced Trusted Types with no custom policy. JavaScript uses no HTML injection sinks or query-string rendering. Form submissions and network connections are denied by CSP. |
| API endpoints and CORS | No API endpoints exist. The hosted preview exposed Vercel’s default wildcard CORS header for public static files. Added an explicit fixed canonical origin to override it; credentialed CORS is not enabled. API-looking paths are expected to return 404 because they have no handler. |
| Security headers | CSP, HSTS, nosniff, frame denial, no-referrer, restricted Permissions Policy, same-origin opener/resource policies. The deprecated browser XSS filter is explicitly disabled; CSP is used instead. |
| Public files | Moved site assets to `public/` and configured Vercel to publish only that directory. Added ignores for secrets, development files and repository metadata. No maps, archives, environment files, database dumps or key files are included in public output. |
| Debug / dependencies | No debug statements, dev server or runtime package manager dependencies are deployed. Removed the third-party analytics script. Font and illustrations are self-hosted; font licence is included. No application dependency upgrade is applicable because there is no package manifest. |
| Database and password hashing | No database or passwords exist in this website. No claim is made about the separate Android app's storage. |
| Git history | Scanned all reachable local refs: 5 commits and 4 historical content blobs. Gitleaks v8.30.1 reported no leaks (4 non-merge commits scanned). A separate targeted check scanned all reachable commit objects and blobs with 10 secret rule families. The Gitleaks archive SHA-256 was verified against the official release metadata. Candidate credential values are redacted in reports. |
| Future checks | Prepared a read-only CI workflow (pending GitHub upload) with commit-pinned checkout, verified Gitleaks download, JavaScript syntax checks and a dependency-free deployment/CSP/SRI/link guard. |

## Remaining controls and limits

**Publication status:** GitHub blob upload returned HTTP 403, `Resource not accessible by integration`. The connector listed no installed accounts. These changes are tested local source and a Vercel preview; GitHub `main` and the production website have not been updated. Repository access must be granted before uploading the source and activating its CI workflow.

1. **Custom rate limiting is not enabled.** Vercel's active firewall configuration read and rule-insertion request both returned HTTP 404, `Seawall Config not found`, for the verified project and team. No existing WAF configuration was overwritten. `scripts/rate_limit_draft.json` describes a proposed log-only rule: 120 GET page requests per 60 seconds per IP on `/`, `/privacy` and `/terms`; assets are excluded. It is a preparation file, not deployed middleware or an active rule. Initialise the custom firewall in the Vercel dashboard, stage the rule in log mode, review matches, and only then enable enforcement.
2. **Repository branch protection is disabled.** The GitHub branch metadata returned `protected: false` for `main`. The available GitHub connector has no branch-protection mutation capability. Configure branch rules with required security checks, appropriate review requirements and restricted bypass permissions in GitHub settings.
3. **Account security is outside this source audit.** MFA, collaborator access, recovery methods, token scopes and sign-in history for GitHub/Vercel were not observable through the available interfaces. Review these at the account level; they control who can change the site's trusted source and deployment settings.
4. **History scans are bounded.** Reachable refs were audited. Deleted/unreachable objects, forks, previous uploads, private repositories and account/integration secrets are outside scope. A scanner finding no candidates is not proof that every possible secret format is absent. Rotate any credential that is independently known to have been disclosed.
5. **No absolute security guarantee.** This is a source/configuration audit and functional security verification of a small static website. It is not an independent penetration test or an audit of the Android apps.

## Verification commands

```sh
python3 scripts/security_check.py
node --check public/assets/site.js
gitleaks git . --redact --no-banner --log-opts='--all'
gitleaks dir public --redact --no-banner
```

The hash guard fails if the approved script changes without updating both its SRI attribute and CSP. `scripts/update_integrity.py` regenerates those values after an intentional script change. Runtime/browser and production verification evidence is recorded in `VERIFICATION.md` when completed.

## References

- https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy
- https://vercel.com/docs/project-configuration
- https://vercel.com/docs/vercel-firewall/vercel-waf/rule-configuration
- https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1

### Reviewed UI additions

Added self-hosted JPEG screenshots, supplied logo and three gallery pages. The screenshot viewer accepts only same-origin asset paths; captions use textContent. The demo controls and pointer dragging use no storage, networking or accounts. The updated script hash is present in CSP and SRI on every page. Existing static-only security scope and account/rate-limit limitations remain applicable.
