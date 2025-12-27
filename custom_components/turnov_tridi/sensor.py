from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import datetime

from .const import DOMAIN, DEFAULT_NAME, TRANSLATIONS, WASTE_TYPES
from .coordinator import TurnovOdpadCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavení senzorů."""
    coordinator: TurnovOdpadCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)

    entities = []
    
    # 1. Hlavní senzor (nejbližší svoz)
    entities.append(TurnovOdpadSensor(coordinator, name, entry.entry_id))

    # 2. Senzory "počet dní" pro každý typ odpadu
    for waste_type in WASTE_TYPES:
        entities.append(TurnovOdpadDaysSensor(coordinator, name, entry.entry_id, waste_type))

    async_add_entities(entities, True)


class TurnovOdpadSensor(CoordinatorEntity, SensorEntity):
    """Hlavní senzor - beze změny."""
    def __init__(self, coordinator: TurnovOdpadCoordinator, name: str, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{coordinator.street}"
        self._attr_icon = "mdi:trash-can"

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data[0]["type"]
        return TRANSLATIONS[self.coordinator.language]["unknown"]

    @property
    def icon(self):
        if self.coordinator.data:
            return self.coordinator.data[0]["icon"]
        return "mdi:trash-can"

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
            return {"data": self.coordinator.data}
        return {}


class TurnovOdpadDaysSensor(CoordinatorEntity, SensorEntity):
    """Senzor počítající dny do svozu konkrétního typu odpadu."""

    def __init__(self, coordinator: TurnovOdpadCoordinator, base_name: str, entry_id: str, waste_type: str) -> None:
        super().__init__(coordinator)
        self.waste_type = waste_type
        self._entry_id = entry_id
        
        # Překlad názvu typu pro hezké jméno senzoru
        type_name = TRANSLATIONS[coordinator.language].get(waste_type, waste_type.capitalize())
        
        self._attr_name = f"{base_name} {type_name}" # Např. "Svoz Odpadu Turnov Plasty"
        self._attr_unique_id = f"{entry_id}_{coordinator.street}_{waste_type}_days"
        self._attr_native_unit_of_measurement = "dní"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self):
        """Vrátí počet dní do nejbližšího svozu tohoto typu."""
        if not self.coordinator.data:
            return None

        today = datetime.date.today()

        # Projdeme seznam a hledáme první výskyt našeho typu
        for item in self.coordinator.data:
            if item.get("type_id") == self.waste_type:
                # Našli jsme! Spočítáme rozdíl
                collection_date = datetime.date.fromisoformat(item["date"])
                days_diff = (collection_date - today).days
                return days_diff
        
        # Pokud v seznamu tento typ vůbec není
        return None

    @property
    def icon(self):
        """Specifická ikona podle typu."""
        if self.waste_type == "mixed": return "mdi:trash-can"
        if self.waste_type == "bio": return "mdi:leaf"
        if self.waste_type == "paper": return "mdi:newspaper"
        if self.waste_type == "plastic": return "mdi:recycle"
        return "mdi:calendar-question"