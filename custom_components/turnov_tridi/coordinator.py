import logging
from datetime import timedelta
import async_timeout
from bs4 import BeautifulSoup
import datetime
import re

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# Import konstant z const.py
from .const import DOMAIN, URL_PAGE, SCAN_INTERVAL, MONTHS, TRANSLATIONS

_LOGGER = logging.getLogger(__name__)

class TurnovOdpadCoordinator(DataUpdateCoordinator):
    """Koordinátor pro stahování dat z webu Turnova."""

    def __init__(self, hass: HomeAssistant, street: str, language: str):
        """Inicializace koordinátora."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.street = street
        self.language = language
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        """Hlavní funkce pro stažení dat (asynchronně)."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        params = {"combine": self.street, "field_datum_svozu_value": today}

        try:
            # Nastavíme timeout 20 sekund, aby to nezamrzlo
            async with async_timeout.timeout(20):
                async with self.session.get(URL_PAGE, params=params) as response:
                    response.raise_for_status()
                    html = await response.text()

            # Parsování HTML je náročné na procesor, proto ho pustíme v odděleném vlákně,
            # abychom nezbrzdili celý Home Assistant.
            return await self.hass.async_add_executor_job(self._parse_html, html)

        except Exception as err:
            raise UpdateFailed(f"Chyba při komunikaci s webem: {err}") from err

    def _parse_html(self, html):
        """Logika parsování HTML (BeautifulSoup)."""
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select("tr")
        if not rows: rows = soup.select(".views-row")

        results = []
        for row in rows:
            text = row.get_text(" ", strip=True)
            # Pokud řádek neobsahuje rok (4 číslice), přeskočíme ho
            if not re.search(r"\d{4}", text):
                continue

            # Hledáme datum ve formátu "7. Leden 2025"
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

                # Překlad názvu
                final_name = TRANSLATIONS[self.language].get(type_id, "Unknown")

                results.append({
                    "date": date_obj.isoformat(),
                    "type": final_name,
                    "icon": icon,
                    "raw": text
                })
        
        return results