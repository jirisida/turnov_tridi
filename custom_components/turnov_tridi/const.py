"""Konstanty pro integraci Svoz odpadu Turnov."""
from datetime import timedelta

DOMAIN = "turnov_odpad"
DEFAULT_NAME = "Svoz odpadu Turnov"
URL_PAGE = "https://www.turnovtridi.cz/kdy-kde-svazime-odpad"

# Interval aktualizace: 12 hodin
SCAN_INTERVAL = timedelta(hours=12)

# Mapování měsíců
MONTHS = {
    "Leden": 1, "Únor": 2, "Březen": 3, "Duben": 4, "Květen": 5, "Červen": 6,
    "Červenec": 7, "Srpen": 8, "Září": 9, "Říjen": 10, "Listopad": 11, "Prosinec": 12
}

# Překlady typů odpadu
TRANSLATIONS = {
    "cz": {
        "mixed": "Směsný",
        "bio": "Bio",
        "paper": "Papír",
        "plastic": "Plasty",
        "unknown": "Neznámý"
    },
    "en": {
        "mixed": "General Waste",
        "bio": "Bio Waste",
        "paper": "Paper",
        "plastic": "Plastic",
        "unknown": "Unknown"
    }
}