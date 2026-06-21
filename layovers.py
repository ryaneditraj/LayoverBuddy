import json


def get_layovers(destination):

    file = open("routes.json", "r")

    data = json.load(file)

    file.close()

    if destination in data:
        return data[destination]

    return []