"""Svoz odpadu Turnov integration."""
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import TurnovOdpadCoordinator

PLATFORMS: list[str] = ["sensor"]

# Schéma pro YAML konfiguraci
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [vol.Schema({
        vol.Required("street"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("language", default="cz"): vol.In(["cz", "en"]),
    })])
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Import z YAML."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    for entry_conf in conf:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=entry_conf
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Nastavení integrace (voláno při startu nebo přidání)."""
    hass.data.setdefault(DOMAIN, {})

    # Načteme konfiguraci
    config = entry.data
    street = config["street"]
    language = config.get("language", "cz")

    # Vytvoříme instanci Koordinátora
    coordinator = TurnovOdpadCoordinator(hass, street, language)

    # Stáhneme první data hned teď (aby senzor nebyl po startu prázdný)
    await coordinator.async_config_entry_first_refresh()

    # Uložíme koordinátora do paměti HA, aby k němu měly přístup senzory
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Odstranění integrace."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok