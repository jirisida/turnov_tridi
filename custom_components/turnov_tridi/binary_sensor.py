"""Binární senzor pro Svoz odpadu Turnov."""
import datetime
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME
from .coordinator import TurnovOdpadCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavení binárních senzorů."""
    coordinator: TurnovOdpadCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)

    async_add_entities([
        TurnovOdpadBinarySensor(coordinator, name, entry.entry_id, "today"),
        TurnovOdpadBinarySensor(coordinator, name, entry.entry_id, "tomorrow"),
    ], True)


class TurnovOdpadBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Senzor, který je ON, pokud se vyváží dnes/zítra."""

    def __init__(self, coordinator: TurnovOdpadCoordinator, base_name: str, entry_id: str, mode: str) -> None:
        super().__init__(coordinator)
        self.mode = mode  # 'today' nebo 'tomorrow'
        self._entry_id = entry_id
        
        # Určení názvu a ID
        suffix = "Dnes" if mode == "today" else "Zítra"
        self._attr_name = f"{base_name} {suffix}"
        self._attr_unique_id = f"{entry_id}_{coordinator.street}_{mode}"
        self._attr_icon = "mdi:truck-check-outline"

    @property
    def is_on(self) -> bool:
        """Vrátí True, pokud je svoz v daný den."""
        if not self.coordinator.data:
            return False

        # Zjistíme cílové datum
        target_date = datetime.date.today()
        if self.mode == "tomorrow":
            target_date += datetime.timedelta(days=1)
        
        target_str = target_date.isoformat()

        # Projdeme data a hledáme shodu
        # (Coordinator vrací seznam, musíme zkontrolovat, jestli v něm je naše datum)
        for item in self.coordinator.data:
            if item["date"] == target_str:
                return True
        
        return False

    @property
    def extra_state_attributes(self):
        """Přidá typ odpadu do atributů, pokud je aktivní."""
        if not self.is_on:
            return {}
        
        # Najdeme, co se konkrétně vyváží
        target_date = datetime.date.today()
        if self.mode == "tomorrow":
            target_date += datetime.timedelta(days=1)
        target_str = target_date.isoformat()

        types = [item["type"] for item in self.coordinator.data if item["date"] == target_str]
        
        return {"waste_types": types}