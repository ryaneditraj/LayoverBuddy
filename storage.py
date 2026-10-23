"""Load the JSON datasets that ship with LayoverBuddy.

Filenames are fixed project files. Paths stay anchored to this directory so a
different working directory cannot redirect a read, and path separators are
rejected so a caller cannot climb out of the project.
"""

import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    if not filename or os.path.basename(filename) != filename:
        raise ValueError("JSON name must be a file name in the project directory")

    path = os.path.join(ROOT, filename)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
