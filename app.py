import json
import os
import secrets
from urllib.parse import quote

from flask import Flask
from flask import Response
from flask import g
from flask import request
from flask import render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from airport_info import get_airport_count
from airport_info import get_airport_data
from airport_info import get_airport_score
from airport_info import get_best_airport
from airport_info import resolve_airport_name
from attractions import get_attractions
from layovers import get_all_destinations
from layovers import get_average_score
from layovers import get_destination_count
from layovers import get_layovers
from layovers import get_scores
from layovers import score_breakdown
from recommendations import get_city_access_text
from recommendations import get_layover_type
from recommendations import get_recommendation
from recommendations import get_recommendation_tier
from storage import ROOT


app = Flask(__name__)

# Trust forwarded headers only when the process sits behind a known proxy.
# Left off by default so a client cannot spoof the public host.
if os.environ.get("TRUST_PROXY", "0").strip() == "1":
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1,
    )


QUERY_LIMIT = 80
SAMPLE_ORIGINS = (
    "Chennai",
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Kolkata",
)

FAQS = (
    {
        "question": "What is LayoverBuddy?",
        "answer": (
            "LayoverBuddy is a free open-source web app that ranks layover "
            "cities for a trip. It compares airport quality, how long it takes "
            "to reach the city, and how many hours the stop is worth, so you "
            "can judge the connection instead of looking only at the fare."
        ),
    },
    {
        "question": "How do I compare layovers between two cities?",
        "answer": (
            "Enter an origin and a destination on the home page, for example "
            "Chennai to New York, and open Find layovers. LayoverBuddy lists "
            "the sample connections for that destination, highest score first, "
            "with airport notes and attractions."
        ),
    },
    {
        "question": "How does LayoverBuddy score a layover airport?",
        "answer": (
            "The score adds a layover score and an airport score, then a city "
            "access bonus (15 points at 30 minutes or less, 8 points at 45 "
            "minutes or less, otherwise 2) and a duration bonus (15 points when "
            "the recommended stop is 8 hours or more, 10 points at 6 hours or "
            "more, otherwise 5)."
        ),
    },
    {
        "question": "Which layover cities does LayoverBuddy include?",
        "answer": (
            "The sample set covers Singapore, Istanbul, Dubai, Doha, Amsterdam, "
            "and Seoul. Destinations with saved routes are New York, London, "
            "Toronto, Tokyo, Paris, Los Angeles, and Chicago."
        ),
    },
    {
        "question": "Does LayoverBuddy show live flight prices or book tickets?",
        "answer": (
            "No. Routes, scores, airport facts, and attractions are local JSON "
            "files shipped with the project. LayoverBuddy does not call an "
            "airline API, show fares, or sell tickets."
        ),
    },
    {
        "question": "Why does the origin city not change which layovers I see?",
        "answer": (
            "Routes are stored by destination. The origin is shown on the "
            "result so the trip is easy to read, and it is kept only in the "
            "page URL. Two trips that share a destination currently share the "
            "same layover list."
        ),
    },
    {
        "question": "What counts as a good layover length?",
        "answer": (
            "Each city has a recommended length in hours. Under 4 hours is "
            "treated as a short layover, under 8 hours as a medium one, and "
            "8 hours or more as a long one. The duration bonus favors stops "
            "that are long enough to leave the airport."
        ),
    },
    {
        "question": "Is LayoverBuddy free and open source?",
        "answer": (
            "Yes. The project is released under the MIT License. You can run "
            "it locally, suggest a route, or send a pull request."
        ),
    },
    {
        "question": "Who maintains LayoverBuddy?",
        "answer": (
            "Ryan Editraj, an AI builder and tech creator. The project lives "
            "at github.com/ryaneditraj/LayoverBuddy."
        ),
    },
)


def clean_query(value, limit=QUERY_LIMIT):
    """Collapse whitespace and cap reflected search text."""

    if value is None:
        return ""

    return " ".join(str(value).split())[:limit]


def site_url():
    configured = os.environ.get("SITE_URL", "").strip().rstrip("/")
    if configured:
        return configured

    return request.url_root.rstrip("/")


def canonical_url():
    """Build a public URL from trimmed query values, not the raw query string."""

    url = site_url() + request.path
    pairs = []
    for key in request.args:
        value = clean_query(request.args.get(key))
        if not value:
            continue
        pairs.append(f"{quote(key, safe='')}={quote(value, safe='')}")
    if pairs:
        url += "?" + "&".join(pairs)
    return url


def dumps_ld(data):
    payload = json.dumps(data, ensure_ascii=False)
    return (
        payload.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def default_json_ld(description):
    site = site_url()
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "LayoverBuddy",
        "applicationCategory": "TravelApplication",
        "operatingSystem": "Web",
        "description": description,
        "url": site + "/",
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        },
        "author": {
            "@type": "Person",
            "name": "Ryan Editraj",
            "url": "https://github.com/ryaneditraj",
            "sameAs": [
                "https://github.com/ryaneditraj",
                "https://instagram.com/ryaneditraj",
            ],
        },
    }


def render_page(template, *, title, description, robots="index, follow", json_ld=None, **context):
    if json_ld is None:
        json_ld = default_json_ld(description)

    g.csp_nonce = secrets.token_urlsafe(16)
    context.update(
        page_title=title,
        page_description=description,
        robots=robots,
        canonical_url=canonical_url(),
        og_image=site_url() + "/static/og.png",
        json_ld=dumps_ld(json_ld),
        csp_nonce=g.csp_nonce,
    )
    return render_template(template, **context)


def sample_trips():
    trips = []
    destinations = get_all_destinations()
    for index, destination in enumerate(destinations):
        origin = SAMPLE_ORIGINS[index % len(SAMPLE_ORIGINS)]
        trips.append({"from_city": origin, "to_city": destination})
    return trips


def public_file(filename, content_type):
    path = os.path.join(ROOT, filename)
    with open(path, encoding="utf-8") as handle:
        body = handle.read().replace("__SITE_URL__", site_url())
    return Response(body, mimetype=content_type)


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    script_src = "script-src 'self'"
    nonce = getattr(g, "csp_nonce", "")
    if nonce:
        script_src += f" 'nonce-{nonce}'"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self'; "
        f"{script_src}; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@app.route("/")
def home():
    description = (
        "Compare layover cities by airport score, time into town, and how "
        "long a connection is worth. Rank stops such as Singapore, Dubai, "
        "Istanbul, and Doha before you pick a flight."
    )
    return render_page(
        "index.html",
        title="LayoverBuddy — rank the city you wait in",
        description=description,
        trips=sample_trips(),
        destinations=get_all_destinations(),
    )


@app.route("/search")
def search():
    from_city = clean_query(request.args.get("from_city"))
    to_city = clean_query(request.args.get("to_city"))
    scores = get_scores()
    airport_data = get_airport_data()
    results = []

    for place in get_layovers(to_city):
        breakdown = score_breakdown(place, scores, airport_data)
        info = airport_data.get(place, {})
        city_time = info.get("city_time", "Unknown")
        best_hours = info.get("best_hours", 0)
        final_score = breakdown["total"]
        results.append(
            {
                "name": place,
                "final_score": final_score,
                "breakdown": breakdown,
                "airport_score": info.get("airport_score", 0),
                "city_time": city_time,
                "best_hours": best_hours,
                "note": info.get("note", "No information available."),
                "recommendation": get_recommendation(final_score),
                "tier": get_recommendation_tier(final_score),
                "city_access": (
                    get_city_access_text(city_time)
                    if isinstance(city_time, (int, float))
                    else ""
                ),
                "layover_type": (
                    get_layover_type(best_hours)
                    if isinstance(best_hours, (int, float))
                    else ""
                ),
                "attractions": get_attractions(place),
            }
        )

    results.sort(key=lambda item: item["final_score"], reverse=True)

    if from_city and to_city:
        title = f"{from_city} to {to_city} layovers — LayoverBuddy"
        description = (
            f"Layover ranking for {from_city} to {to_city}. Compare connection "
            "cities by airport score, time into town, and recommended layover length."
        )
    else:
        title = "Layover results — LayoverBuddy"
        description = (
            "Layover ranking. Compare connection cities by airport score, "
            "time into town, and recommended layover length."
        )

    return render_page(
        "results.html",
        title=title,
        description=description,
        robots="noindex, follow",
        from_city=from_city,
        to_city=to_city,
        results=results,
        trips=sample_trips(),
    )


@app.route("/airport")
def airport_page():
    requested = clean_query(request.args.get("name"))
    key = resolve_airport_name(requested)
    if key is None:
        body = render_page(
            "airport.html",
            title="Airport not found — LayoverBuddy",
            description="That airport is not in the LayoverBuddy sample set.",
            robots="noindex, nofollow",
            found=False,
            name=requested or "Unknown airport",
            airport={},
            attractions=[],
        )
        return body, 404

    airport = get_airport_data()[key]
    description = (
        f"{key} layover guide: airport score {airport.get('airport_score', 0)}, "
        f"{airport.get('city_time', 0)} minutes to the city, best around "
        f"{airport.get('best_hours', 0)} hours. {airport.get('note', '')}"
    ).strip()
    json_ld = {
        "@context": "https://schema.org",
        "@type": "TouristDestination",
        "name": key,
        "description": airport.get("note", description),
        "url": canonical_url(),
        "touristType": "Layover traveler",
    }
    return render_page(
        "airport.html",
        title=f"{key} layover airport — LayoverBuddy",
        description=description,
        json_ld=json_ld,
        found=True,
        name=key,
        airport=airport,
        attractions=get_attractions(key),
    )


@app.route("/about")
def about():
    description = (
        "LayoverBuddy helps travelers compare layover cities, airport quality, "
        "and time into town instead of choosing a flight on price alone."
    )
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            default_json_ld(description),
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["question"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": item["answer"],
                        },
                    }
                    for item in FAQS
                ],
            },
        ],
    }
    return render_page(
        "about.html",
        title="About LayoverBuddy",
        description=description,
        json_ld=json_ld,
        faqs=FAQS,
    )


@app.route("/stats")
def stats():
    best_airport = get_best_airport()
    description = (
        "Sample-set statistics for LayoverBuddy: how many airports are ranked, "
        "which airport scores highest, and the average layover score."
    )
    return render_page(
        "stats.html",
        title="LayoverBuddy statistics",
        description=description,
        airport_count=get_airport_count(),
        destination_count=get_destination_count(),
        best_airport=best_airport,
        best_score=get_airport_score(best_airport) if best_airport else 0,
        average_score=get_average_score(),
    )


@app.route("/robots.txt")
def robots():
    return public_file("robots.txt", "text/plain; charset=utf-8")


@app.route("/sitemap.xml")
def sitemap():
    return public_file("sitemap.xml", "application/xml; charset=utf-8")


@app.route("/llms.txt")
def llms():
    return public_file("llms.txt", "text/plain; charset=utf-8")


@app.errorhandler(404)
def not_found(_error):
    body = render_page(
        "404.html",
        title="Page not found — LayoverBuddy",
        description="That page is not part of LayoverBuddy.",
        robots="noindex, nofollow",
    )
    return body, 404


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
