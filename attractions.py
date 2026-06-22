import json


def get_attractions_data():

    file = open(
        "attractions.json",
        "r"
    )

    data = json.load(
        file
    )

    file.close()

    return data


def get_attractions(
    city
):

    data = get_attractions_data()

    if city in data:

     return data[
            city
     ]

    return []


def get_attraction_count(
    city
):

    attractions = get_attractions(
        city
    )

    return len(
        attractions
    )