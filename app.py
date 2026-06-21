from flask import Flask
from flask import request

from layovers import get_layovers

app = Flask(__name__)


@app.route("/")
def home():

    page = """
    <h1>LayoverBuddy</h1>

    <p>Find possible layovers for your trip.</p>

    <form action="/search">

        <p>From City</p>
        <input type="text" name="from_city">

        <p>To City</p>
      <input type="text" name="to_city">

        <br><br>

        <button type="submit">
            Find Layovers
        </button>

    </form>
    """

    return page


@app.route("/search")
def search():

    from_city = request.args.get("from_city")
    to_city = request.args.get("to_city")

    places = get_layovers(to_city)

    result = f"<h1>{from_city} → {to_city}</h1>"

    if len(places) == 0:

        result += "<p>No layovers found.</p>"

    else:

        result += "<h3>Possible Layovers</h3>"

        result += "<ul>"

        for item in places:
            result += f"<li>{item}</li>"

        result += "</ul>"

    result += "<br>"
    result += "<a href='/'>Back</a>"
    return result


app.run(debug=True, port=5001)