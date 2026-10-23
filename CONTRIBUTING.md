# Contributing to LayoverBuddy

Thanks for wanting to make layovers easier to compare. Issues and pull requests are welcome.

## Setup

```bash
git clone https://github.com/ryaneditraj/LayoverBuddy.git
cd LayoverBuddy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On Windows, activate the virtual environment with `venv\Scripts\activate` if you named it `venv`, or `.venv\Scripts\activate` for the path above.

Run the tests before you open a pull request:

```bash
python -m unittest discover -s tests -v
```

## What to change

- Keep the scoring rules in `layovers.py` unless the pull request is explicitly about changing them, and update `tests/test_app.py` in the same change. The published Chennai → New York scores are part of the contract the README describes.
- Add a city by updating the JSON files together: `routes.json` (destination → layover list), `scores.json`, `airport_info.json`, and `attractions.json`. Then add the airport URL to `sitemap.xml`.
- Routes are keyed by destination. Say so in the interface if a change makes that less obvious.
- Do not add live API keys. Configuration belongs in the environment, with a placeholder in `.env.example`.
- Do not commit `.env`, virtual environments, or `__pycache__`.

## Pull requests

1. Fork the repository and branch from `main`.
2. Keep the change focused.
3. Describe how you tested it. The pull request template has a short checklist.
4. Be kind in review. The code of conduct in `CODE_OF_CONDUCT.md` applies to issues and pull requests.

## Security

Please report vulnerabilities through a private GitHub security advisory, not a public issue. See `SECURITY.md`.
