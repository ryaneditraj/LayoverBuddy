import json


def get_layovers(destination):

    file = open(
        "routes.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    if destination in data:

        return data[
            destination
        ]

    return []


def get_scores():

    file = open(
        "scores.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    return data


def calculate_final_score(
    place,
    scores,
    airport_data
):

    layover_score = scores.get(
        place,
        0
    )

    airport_score = airport_data.get(
        place,
        {}
    ).get(
        "airport_score",
        0
    )

    city_time = airport_data.get(
        place,
        {}
    ).get(
        "city_time",
        60
    )

    best_hours = airport_data.get(
        place,
        {}
    ).get(
        "best_hours",
        4
    )

    score = 0

    score += layover_score

    score += airport_score

    if city_time <= 30:

        score += 15

    elif city_time <= 45:

        score += 8

    else:

        score += 2

    if best_hours >= 8:

        score += 15

    elif best_hours >= 6:

        score += 10

    else:

        score += 5

    return score


def get_top_layovers(
    destination,
    amount=3
):

    places = get_layovers(
      destination
    )

    scores = get_scores()

    temp = []

    for place in places:

        score = scores.get(
            place,
            0
        )

        temp.append(
            {
                "name": place,
                "score": score
            }
        )

    temp.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return temp[:amount]


def route_exists(
    destination
):

    file = open(
        "routes.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    return destination in data


def get_destination_count():

    file = open(
        "routes.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    return len(data)


def get_all_destinations():

    file = open(
        "routes.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    result = []

    for item in data:

        result.append(
            item
        )

    return result


def get_average_score():

    scores = get_scores()

    total = 0

    count = 0

    for airport in scores:

        total += scores[
            airport
        ]

        count += 1

    if count == 0:

     return 0

    return round(
        total / count,
        2
    )