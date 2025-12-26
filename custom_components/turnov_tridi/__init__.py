"""Svoz odpadu Turnov integration."""
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

PLATFORMS: list[str] = ["sensor"]

# --- DEFINICE SCHÉMATU PRO YAML ---
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [vol.Schema({
        vol.Required("street"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("language", default="cz"): vol.In(["cz", "en"]),
    })])
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Import konfigurace z YAML (pokud existuje)."""
    conf = config.get(DOMAIN)
    
    if conf is None:
        return True

    for entry_conf in conf:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=entry_conf,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Standardní načtení integrace."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Odstranění integrace."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)