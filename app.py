from flask import Flask
from flask import request
from flask import render_template

from layovers import get_layovers
from layovers import get_scores
from layovers import calculate_final_score

from airport_info import get_airport_data
from recommendations import get_recommendation


app = Flask(__name__)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/search")
def search():

    from_city = request.args.get("from_city")
    to_city = request.args.get("to_city")

    if not from_city:
        from_city = ""

    if not to_city:
        to_city = ""

    layovers = get_layovers(to_city)

    scores = get_scores()

    airport_data = get_airport_data()

    final_results = []

    for place in layovers:

        final_score = calculate_final_score(
            place,
            scores,
            airport_data
        )

        airport_info = airport_data.get(place, {})

        city_time = airport_info.get(
            "city_time",
            "Unknown"
        )

        airport_score = airport_info.get(
      "airport_score",
            0
        )

        best_hours = airport_info.get(
            "best_hours",
            0
        )

        note = airport_info.get(
            "note",
            "No information available."
        )

        recommendation = get_recommendation(
            final_score
        )

        final_results.append(
            {
                "name": place,
                "final_score": final_score,
                "airport_score": airport_score,
                "city_time": city_time,
                "best_hours": best_hours,
                "note": note,
              "recommendation": recommendation
            }
        )

    final_results.sort(
  key=lambda x: x["final_score"],
        reverse=True
    )

    return render_template(
        "results.html",
        from_city=from_city,
        to_city=to_city,
  results=final_results
    )

@app.route("/airport")
def airport_page():

    airport_name = request.args.get(
        "name"
    )

    airport_data = get_airport_data()

    airport = airport_data.get(
        airport_name,
        {}
    )

    output = f"""
    <h1>{airport_name}</h1>

    <p>
    Airport Score:
    {airport.get("airport_score", 0)}
    </p>

    <p>
    City Time:
    {airport.get("city_time", 0)}
    minutes
    </p>

    <p>  Best Layover:
    {airport.get("best_hours", 0)}
    hours
    </p>

    <p>
    {airport.get("note", "")}
    </p>

    <br>

    <a href="/">
        Back
    </a>
    """

    return output


@app.route("/about")
def about():

    page = """
    <h1>About LayoverBuddy</h1>

    <p>
    LayoverBuddy helps travellers
    discover better layovers.
    </p>

    <p>
 Instead of only choosing
    the cheapest flight,
    users can compare
    airports and cities.
    </p>

    <a href="/">
        Home
    </a>
    """

    return page


@app.route("/stats")
def stats():

    airport_data = get_airport_data()

    airport_count = len(
        airport_data
    )

    highest_score = 0
    highest_airport = ""

    for airport_name in airport_data:

        airport = airport_data[
            airport_name
        ]

        score = airport.get(
            "airport_score",
            0
        )

        if score > highest_score:

            highest_score = score
            highest_airport = airport_name

    page = f"""
    <h1>Statistics</h1>

    <p>
    Airports:
    {airport_count}
    </p>

    <p>
    Best Airport:
    {highest_airport}
    </p>

    <p>
    Score:
    {highest_score}
    </p>

    <a href="/">
 Home
    </a>
    """

    return page





app.run(host='0.0.0.0', port=5000)