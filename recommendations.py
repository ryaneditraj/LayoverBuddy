def get_recommendation(
    score
):

    if score >= 190:

        return (
            "Excellent layover. "
            "Highly recommended."
        )

    if score >= 170:

        return (
            "Very good option."
        )

    if score >= 150:

        return (
            "Good option."
        )

    if score >= 120:

        return (
            "Average option."
        )

    return (
        "Not recommended."
    )


def get_layover_type(
    hours
):

    if hours < 4:

        return "Short"

    if hours < 8:

        return "Medium"

    return "Long"


def get_city_access_text(
    minutes
):

    if minutes <= 30:

        return (
            "Easy city access"
        )

    if minutes <= 45:

        return (
            "Moderate city access"
        )

    return (
     "Long travel time"
    )


def score_explanation(
    score
):

    if score >= 190:

        return (
            "Airport quality, city access "
            "and attractions are excellent."
        )

    if score >= 170:

        return (
            "Strong airport and good city access."
        )

    if score >= 150:

        return (
            "Decent layover choice."
        )

    return (
        "Limited advantages."
    )