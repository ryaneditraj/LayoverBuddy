import json


def get_airport_data():
    file = open(
        "airport_info.json",
        "r"
  )

    data = json.load(
        file
    )

    file.close()

    return data


def get_airport(
    airport_name
):

    data = get_airport_data()

    if airport_name in data:

        return data[
            airport_name
        ]

    return {}


def airport_exists(
    airport_name
):

    data = get_airport_data()

    return airport_name in data


def get_airport_score(
    airport_name
):

    airport = get_airport(
        airport_name
    )

    return airport.get(
        "airport_score",
        0
    )


def get_city_time(
    airport_name
):

    airport = get_airport(
        airport_name
    )

    return airport.get(
        "city_time",
        0
    )


def get_best_hours(
    airport_name
):

    airport = get_airport(
        airport_name
    )

    return airport.get(
        "best_hours",
        0
    )


def get_airport_note(
    airport_name
):

    airport = get_airport(
        airport_name
    )

    return airport.get(
        "note",
        ""
    )


def get_best_airport():

    data = get_airport_data()

    best_score = 0
    best_airport = ""

    for airport in data:

        score = data[
            airport
        ].get(
            "airport_score",
            0
        )

        if score > best_score:

            best_score = score
            best_airport = airport

    return best_airport


def get_airport_count():

    data = get_airport_data()

    return len(data)


def search_airports(
    text
):

    data = get_airport_data()

    results = []

    text = text.lower()

    for airport in data:

        if text in airport.lower():

            results.append(
                airport
            )

    return results