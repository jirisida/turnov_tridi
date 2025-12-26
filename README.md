# Svoz odpadu Turnov / Turnov Waste Collection

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()

**[CZ]** Integrace pro Home Assistant, která stahuje termíny svozu odpadu z webu [turnovtridi.cz](https://www.turnovtridi.cz). 
Podporuje nastavení přes **grafické rozhraní (UI)** i přes YAML.

**[EN]** Home Assistant integration that retrieves waste collection schedules from [turnovtridi.cz](https://www.turnovtridi.cz). 
Supports configuration via **UI (Config Flow)** and YAML.

---

## 🇨🇿 Návod (Czech)

### 1. Instalace

1. **HACS:** Jděte do HACS > Integrations > Menu > Custom repositories > Vložte URL tohoto repozitáře > Stáhněte integraci.
2. **Restart:** Restartujte Home Assistant.

### 2. Konfigurace (Doporučeno)

Integraci lze přidat přímo v nastavení (není nutné psát YAML).

1. Jděte do **Nastavení** > **Zařízení a služby**.
2. Klikněte na **Přidat integraci**.
3. Vyhledejte **Svoz odpadu Turnov**.
4. Zadejte název ulice (např. `Zborovska`).

### 3. Konfigurace přes YAML (Volitelné)

Pokud preferujete YAML (např. pro zálohování), použijte tento formát v `configuration.yaml`. Integrace se po restartu automaticky naimportuje do UI.

```yaml
# configuration.yaml
turnov_odpad:
  - street: "Zborovska"
    name: "Můj Odpad"
    language: "cz"
  
  # Můžete přidat více ulic
  - street: "Trávnice"
    name: "Odpad Babička"
```

### 4. Část: CZ Karty a Automatizace

#### Karta na Dashboard (Lovelace)

Pro zobrazení seznamu svozů použijte kartu **Markdown**. V příkladu jsou zobrazeny následující 3 svozy.

```yaml
type: markdown
content: |
  ## 🚛 Plán svozu
  {% set data = state_attr('sensor.svoz_odpadu_turnov', 'data') %}
  {% if data %}
  {% for item in data[:3] %}
  <ha-icon icon="{{ item.icon }}"></ha-icon> **{{ item.type }}** - {{ as_timestamp(item.date) | timestamp_custom('%d. %m.') }}
  {% endfor %}
  {% else %}
  Žádná data k dispozici.
  {% endif %}
```

#### Automatizace: Upozornění na mobil

Pošle notifikaci den předem v 18:00.

```yaml
alias: "Upozornění na svoz odpadu"
trigger:
  - platform: time
    at: "18:00:00"
condition:
  - condition: template
    value_template: >-
      {{ state_attr('sensor.svoz_odpadu_turnov', 'data')[0]['date'] == (now() + timedelta(days=1)).strftime('%Y-%m-%d') }}
action:
  - service: notify.mobile_app_vas_telefon
    data:
      title: "🚛 Zítra je svoz odpadu!"
      message: "{{ state_attr('sensor.svoz_odpadu_turnov', 'data')[0]['type'] }}"
```



## 🇬🇧 Instructions (English)

### 1. Installation

1. **HACS:** Go to HACS > Integrations > Menu > Custom repositories > Paste URL > Download.
2. **Restart:** Restart Home Assistant.

### 2. Configuration (UI - Recommended)

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Svoz odpadu Turnov**.
4. Enter the street name (Must be in Czech, e.g., `Zborovska`).

### 3. Configuration via YAML (Optional)

Add this to your `configuration.yaml`. It will be automatically imported into the UI upon restart.

```yaml
# configuration.yaml
turnov_odpad:
  - street: "Zborovska"
    name: "Waste Collection"
    language: "en"
```

## License

MIT License

Copyright (c) 2025 @xsida
