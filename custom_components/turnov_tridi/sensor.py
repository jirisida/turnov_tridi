import logging
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import timedelta
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Interval aktualizace: 1 hodina (4 hodiny je taky OK, šetří to web)
SCAN_INTERVAL = timedelta(hours=12)

URL_PAGE = "https://www.turnovtridi.cz/kdy-kde-svazime-odpad"

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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavení senzoru z Config Entry."""
    config = entry.data
    street = config["street"]
    name = config.get("name", "Svoz odpadu Turnov")
    language = config.get("language", "cz")

    async_add_entities([TurnovOdpadSensor(name, street, language, entry.entry_id)], True)


class TurnovOdpadSensor(SensorEntity):
    """Reprezentace senzoru."""

    def __init__(self, name, street, language, entry_id):
        self._attr_name = name
        self._street = street
        self._language = language
        self._attr_unique_id = f"{entry_id}_{street}" 
        self._attr_icon = "mdi:trash-can"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    def update(self):
        """Spuštění stahování."""
        data = self._fetch_data()
        
        if data:
            self._attr_native_value = data[0]["type"]
            self._attr_icon = data[0]["icon"]
            self._attr_extra_state_attributes = {"data": data}
        else:
            self._attr_native_value = TRANSLATIONS[self._language]["unknown"]

    def _fetch_data(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        headers = {"User-Agent": "Home Assistant Integration / TurnovOdpad"}
        params = {"combine": self._street, "field_datum_svozu_value": today}

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

                    if "Směsný" in text: type_id = "mixed"; icon = "mdi:trash-can"
                    elif "Bio" in text: type_id = "bio"; icon = "mdi:leaf"
                    elif "Papír" in text: type_id = "paper"; icon = "mdi:newspaper"
                    elif "Plasty" in text or "Plast" in text: type_id = "plastic"; icon = "mdi:recycle"

                    final_name = TRANSLATIONS[self._language].get(type_id, "Unknown")

                    results.append({
                        "date": date_obj.isoformat(),
                        "type": final_name,
                        "icon": icon,
                        "raw": text
                    })
            return results

        except Exception as e:
            _LOGGER.error(f"Chyba při stahování dat: {e}")
            return None