from storage import load_json


def get_airport_data():
    return load_json("airport_info.json")


def resolve_airport_name(name):
    """Return the stored airport key, ignoring case and extra whitespace."""

    if name is None:
        return None

    cleaned = " ".join(str(name).split())
    if not cleaned:
        return None

    data = get_airport_data()
    if cleaned in data:
        return cleaned

    folded = cleaned.casefold()
    for key in data:
        if str(key).casefold() == folded:
            return key

    return None


def get_airport(airport_name):
    key = resolve_airport_name(airport_name)
    if key is None:
        return {}

    return get_airport_data()[key]


def airport_exists(airport_name):
    return resolve_airport_name(airport_name) is not None


def get_airport_score(airport_name):
    return get_airport(airport_name).get("airport_score", 0)


def get_city_time(airport_name):
    return get_airport(airport_name).get("city_time", 0)


def get_best_hours(airport_name):
    return get_airport(airport_name).get("best_hours", 0)


def get_airport_note(airport_name):
    return get_airport(airport_name).get("note", "")


def get_best_airport():
    data = get_airport_data()
    best_score = 0
    best_airport = ""

    for airport, info in data.items():
        score = info.get("airport_score", 0)
        if score > best_score:
            best_score = score
            best_airport = airport

    return best_airport


def get_airport_count():
    return len(get_airport_data())


def search_airports(text):
    if not text:
        return []

    folded = str(text).casefold()
    return [
        airport
        for airport in get_airport_data()
        if folded in str(airport).casefold()
    ]
