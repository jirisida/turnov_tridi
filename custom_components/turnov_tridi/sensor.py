import logging
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import timedelta # Důležitý import pro interval
import re
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# --- NASTAVENÍ VÝCHOZÍHO INTERVALU ---
# Pokud uživatel v YAML nezadá jinak, aktualizuje se každou hodinu
SCAN_INTERVAL = timedelta(hours=1)

# Konstanty
DEFAULT_NAME = "Svoz odpadu Turnov"
CONF_STREET = "street"
CONF_LANGUAGE = "language"
URL_PAGE = "https://www.turnovtridi.cz/kdy-kde-svazime-odpad"

# Validace konfigurace
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STREET): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_LANGUAGE, default="cz"): vol.In(["cz", "en"]),
})

MONTHS = {
    "Leden": 1, "Únor": 2, "Březen": 3, "Duben": 4, "Květen": 5, "Červen": 6,
    "Červenec": 7, "Srpen": 8, "Září": 9, "Říjen": 10, "Listopad": 11, "Prosinec": 12
}

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

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Funkce pro vytvoření senzoru."""
    street = config.get(CONF_STREET)
    name = config.get(CONF_NAME)
    language = config.get(CONF_LANGUAGE)
    
    add_entities([TurnovOdpadSensor(name, street, language)], True)


class TurnovOdpadSensor(SensorEntity):
    """Reprezentace senzoru."""

    def __init__(self, name, street, language):
        self._attr_name = name
        self._street = street
        self._language = language
        self._attr_unique_id = f"turnov_odpad_{street.replace(' ', '_').lower()}"
        self._attr_icon = "mdi:trash-can"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    def update(self):
        data = self._fetch_data()
        
        if data:
            self._attr_native_value = data[0]["type"]
            self._attr_icon = data[0]["icon"]
            self._attr_extra_state_attributes = {"data": data}
        else:
            self._attr_native_value = TRANSLATIONS[self._language]["unknown"]

    def _fetch_data(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        headers = {
            "User-Agent": "Home Assistant Integration / TurnovOdpad",
        }
        params = {
            "combine": self._street,
            "field_datum_svozu_value": today
        }

        try:
            response = requests.get(URL_PAGE, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select("tr") 
            if not rows: rows = soup.select(".views-row")
            
            results = []
            
            for row in rows:
                text = row.get_text(" ", strip=True)
                if not re.search(r"\d{4}", text):
                    continue

                match_date = re.search(r"(\d+)\.\s+([a-zA-Zá-žÁ-Ž]+)\s+(\d{4})", text)
                
                if match_date:
                    day, month_name, year = match_date.groups()
                    month = MONTHS.get(month_name, 1)
                    date_obj = datetime.date(int(year), month, int(day))
                    
                    type_id = "unknown"
                    icon = "mdi:help"

                    if "Směsný" in text: 
                        type_id = "mixed"; icon = "mdi:trash-can"
                    elif "Bio" in text: 
                        type_id = "bio"; icon = "mdi:leaf"
                    elif "Papír" in text: 
                        type_id = "paper"; icon = "mdi:newspaper"
                    elif "Plasty" in text or "Plast" in text: 
                        type_id = "plastic"; icon = "mdi:recycle"

                    final_name = TRANSLATIONS[self._language].get(type_id, "Unknown")

                    results.append({
                        "date": date_obj.isoformat(),
                        "type": final_name,
                        "icon": icon,
                        "raw": text
                    })
            
            return results

        except Exception as e:
            _LOGGER.error(f"Chyba při stahování dat pro {self._street}: {e}")
            return None