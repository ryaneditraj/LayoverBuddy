from storage import load_json


def get_attractions_data():
    return load_json("attractions.json")


def get_attractions(city):
    data = get_attractions_data()
    if city in data:
        return data[city]

    return []


def get_attraction_count(city):
    return len(get_attractions(city))
