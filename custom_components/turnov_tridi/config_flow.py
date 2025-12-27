import logging
import voluptuous as vol
import requests
import datetime

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, URL_PAGE, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

# Schéma je stejné pro Config i Options
DATA_SCHEMA = vol.Schema({
    vol.Required("street"): str,
    vol.Optional("name", default=DEFAULT_NAME): str,
    vol.Optional("language", default="cz"): vol.In(["cz", "en"]),
})

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Ověří spojení a vygeneruje název (sdílená funkce)."""
    street = data["street"]
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    def _test_connection():
        try:
            response = requests.get(
                URL_PAGE, 
                params={"combine": street, "field_datum_svozu_value": today},
                headers={"User-Agent": "Home Assistant Config Flow"},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Connection error: {e}")

    await hass.async_add_executor_job(_test_connection)
    title = data.get("name", f"Svoz {street}")
    return {"title": title}


class TurnovOdpadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hlavní konfigurační flow (při přidávání)."""
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Spustí Options Flow při kliknutí na Konfigurovat."""
        return TurnovOdpadOptionsFlowHandler(config_entry)

    async def async_step_import(self, import_config: dict) -> FlowResult:
        """Import z YAML."""
        await self.async_set_unique_id(import_config["street"])
        self._abort_if_unique_id_configured()
        try:
            info = await validate_input(self.hass, import_config)
            return self.async_create_entry(title=info["title"], data=import_config)
        except Exception:
            _LOGGER.error("Chyba při importu Turnov Odpad z YAML")
            return self.async_abort(reason="cannot_connect")

    async def async_step_user(self, user_input=None) -> FlowResult:
        """GUI formulář."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input["street"])
            self._abort_if_unique_id_configured()
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)


class TurnovOdpadOptionsFlowHandler(config_entries.OptionsFlow):
    """Handler pro změnu nastavení (tlačítko Konfigurovat)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Zobrazí formulář s předvyplněnými hodnotami."""
        if user_input is not None:
            # Aktualizujeme nastavení a reloadneme integraci
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data=None)

        # Načteme aktuální hodnoty jako výchozí
        current_config = self.config_entry.data
        
        options_schema = vol.Schema({
            vol.Required("street", default=current_config.get("street")): str,
            vol.Optional("name", default=current_config.get("name", DEFAULT_NAME)): str,
            vol.Optional("language", default=current_config.get("language", "cz")): vol.In(["cz", "en"]),
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)