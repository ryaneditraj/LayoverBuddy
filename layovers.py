from storage import load_json


def _match_key(data, name):
    if name is None:
        return None

    cleaned = " ".join(str(name).split())
    if not cleaned:
        return None

    if cleaned in data:
        return cleaned

    folded = cleaned.casefold()
    for key in data:
        if str(key).casefold() == folded:
            return key

    return None


def get_layovers(destination):
    data = load_json("routes.json")
    key = _match_key(data, destination)
    if key is None:
        return []

    return data[key]


def get_scores():
    return load_json("scores.json")


def score_breakdown(place, scores, airport_data):
    """Return the pieces that add up to a layover score.

    The bonuses match the original rules: quicker city access and a longer
    worthwhile connection both raise the total.
    """

    info = airport_data.get(place, {})
    layover_score = scores.get(place, 0)
    airport_score = info.get("airport_score", 0)
    city_time = info.get("city_time", 60)
    best_hours = info.get("best_hours", 4)

    if city_time <= 30:
        city_bonus = 15
    elif city_time <= 45:
        city_bonus = 8
    else:
        city_bonus = 2

    if best_hours >= 8:
        duration_bonus = 15
    elif best_hours >= 6:
        duration_bonus = 10
    else:
        duration_bonus = 5

    return {
        "layover_score": layover_score,
        "airport_score": airport_score,
        "city_bonus": city_bonus,
        "duration_bonus": duration_bonus,
        "total": layover_score + airport_score + city_bonus + duration_bonus,
    }


def calculate_final_score(place, scores, airport_data):
    return score_breakdown(place, scores, airport_data)["total"]


def get_top_layovers(destination, amount=3):
    places = get_layovers(destination)
    scores = get_scores()
    ranked = [
        {"name": place, "score": scores.get(place, 0)}
        for place in places
    ]
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:amount]


def route_exists(destination):
    return _match_key(load_json("routes.json"), destination) is not None


def get_destination_count():
    return len(load_json("routes.json"))


def get_all_destinations():
    return list(load_json("routes.json"))


def get_average_score():
    scores = get_scores()
    if not scores:
        return 0

    total = sum(scores.values())
    return round(total / len(scores), 2)
