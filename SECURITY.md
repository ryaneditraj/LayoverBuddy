# Security policy

## Supported versions

Security fixes land on the default branch, `main`. There are no versioned releases yet.

| Version | Supported |
| --- | --- |
| `main` | Yes |

## Reporting a vulnerability

Please report vulnerabilities privately. Use a [GitHub security advisory](https://github.com/ryaneditraj/LayoverBuddy/security/advisories/new) on `ryaneditraj/LayoverBuddy`.

Include the route, a request example, and the effect you can show. Please give the maintainer a chance to fix the issue before writing about it in public. There is no bug bounty.

Do not open a public GitHub issue for a security report.

## What this app is

LayoverBuddy is a small Flask site. It reads local JSON files, renders pages, and does not have accounts, payments, or a database. It does not ship with API keys.

`python app.py` listens on `0.0.0.0:5000` by default so a container host can reach it. Leave `FLASK_DEBUG` unset on any shared machine. The debugger is off unless `FLASK_DEBUG` is `1`, `true`, or `yes`. Set `TRUST_PROXY=1` only when a reverse proxy you control is the only client that can reach the process.

## Hardening already in place

- Pages are rendered with Jinja autoescaping. Airport, about, and statistics pages used to return raw HTML strings; they now use templates.
- Search text is trimmed and limited to 80 characters before it is shown.
- Responses send `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.
- JSON dataset paths are fixed names inside the project directory.
- Runtime dependencies are pinned. Jinja2 is pinned to 3.1.6.

JSON-LD is included for search and answer engines. It is delivered in a nonce-tagged script so the content security policy can allow that block without allowing other inline scripts.
