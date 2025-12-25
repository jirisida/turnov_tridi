# Svoz odpadu Turnov - Home Assistant Integrace

Integrace pro získání termínů svozu odpadu z webu [turnovtridi.cz](https://www.turnovtridi.cz).

## Instalace přes HACS

1. Otevřete HACS > Integrations > Menu > Custom repositories.
2. Vložte URL tohoto repozitáře.
3. Kategorie: **Integration**.
4. Klikněte na **Add** a poté **Download**.
5. Restartujte Home Assistant.

## Konfigurace

Přidejte do souboru `configuration.yaml`:

```yaml
sensor:
  - platform: turnov_odpad
    street: "Stanislava Srazila"
    name: "Můj Odpad"
    # scan_interval: 86400 (volitelné, default je 1h, doporučuji nastavit vyšší)


### Parametry

| Parametr | Povinný | Popis | Výchozí |
| :--- | :---: | :--- | :--- |
| `platform` | ✅ | Musí být `turnov_odpad`. | - |
| `street` | ✅ | Název ulice v Turnově. Musí se přesně shodovat s našeptávačem na webu turnovtridi.cz. | - |
| `name` | ❌ | Vlastní název senzoru v HA. | Svoz odpadu Turnov |
| `language` | ❌ | Jazyk pro stavy senzoru (`cz` nebo `en`). | `cz` |
| `scan_interval`| ❌ | Jak často aktualizovat data (v sekundách). | `3600` (1h) |