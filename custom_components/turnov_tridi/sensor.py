from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME, TRANSLATIONS
from .coordinator import TurnovOdpadCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavení senzoru."""
    # Vyzvedneme si připraveného koordinátora
    coordinator: TurnovOdpadCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    name = entry.data.get("name", DEFAULT_NAME)

    async_add_entities([TurnovOdpadSensor(coordinator, name, entry.entry_id)], True)


class TurnovOdpadSensor(CoordinatorEntity, SensorEntity):
    """Hlavní senzor, který zobrazuje nejbližší svoz."""

    def __init__(self, coordinator: TurnovOdpadCoordinator, name: str, entry_id: str) -> None:
        # Předáme koordinátora rodičovské třídě - ta se postará o aktualizace
        super().__init__(coordinator)
        
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{coordinator.street}"
        self._attr_icon = "mdi:trash-can"

    @property
    def native_value(self):
        """Stav senzoru (text)."""
        # Data jsou dostupná v self.coordinator.data
        if self.coordinator.data:
            return self.coordinator.data[0]["type"]
        
        # Fallback pokud nejsou data
        return TRANSLATIONS[self.coordinator.language]["unknown"]

    @property
    def icon(self):
        """Dynamická ikona podle typu odpadu."""
        if self.coordinator.data:
            return self.coordinator.data[0]["icon"]
        return "mdi:trash-can"

    @property
    def extra_state_attributes(self):
        """Atributy (celý seznam svozů)."""
        if self.coordinator.data:
            return {"data": self.coordinator.data}
        return {}