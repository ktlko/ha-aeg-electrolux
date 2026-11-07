# AEG / Electrolux washer for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![GitHub release](https://img.shields.io/github/v/release/ktlko/ha-aeg-washer)](https://github.com/ktlko/ha-aeg-washer/releases)
[![Validate](https://github.com/ktlko/ha-aeg-washer/actions/workflows/validate.yml/badge.svg)](https://github.com/ktlko/ha-aeg-washer/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A clean, translated integration for **AEG and Electrolux washing machines** using the official **Electrolux Group Developer API** – live updates, programme selection, start / pause / stop and a ready-made dashboard card.

[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kotelino&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/kotelino)

**Languages:** English, Slovenčina, Čeština, Deutsch, Polski, Español, Italiano

## Features

- **status** (ready, washing, paused, delayed start, finished, off, fault), **programme**, **phase**
- **time remaining**, **ends at**, **progress %**, temperature, spin speed, measured load
- door, door lock, washing, finished, connection
- **buttons**: start, pause, resume, stop, on, off
- **selects**: programme, temperature, spin speed – options come from your washer
- wash cycle counter, operating hours, alerts, remote control, water hardness, Wi-Fi signal
- **live push updates** (Server-Sent Events) plus a 5-minute safety poll
- tokens are refreshed and saved automatically; re-authentication when they expire
- **bundled Lovelace card** – no extra resource needed

## Requirements

- An AEG / Electrolux washer connected to the **My AEG / My Electrolux** app
- A free account at **[developer.electrolux.one](https://developer.electrolux.one/)**:
  1. Sign in with the same account you use in the app.
  2. Create an **API key**.
  3. Generate an **access token** and a **refresh token**.
- Remote control enabled on the washer (Wi-Fi / Remote button) for start and stop

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ktlko&repository=ha-aeg-washer&category=integration)

1. In Home Assistant open **HACS → ⋮ → Custom repositories**.
2. Add `https://github.com/ktlko/ha-aeg-washer` with the type **Integration**.
3. Search for **AEG / Electrolux washer**, open it and click **Download**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and pick **AEG / Electrolux washer**.

[![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=aeg_pracka)

### Manual

Copy `custom_components/aeg_pracka` into the `custom_components` folder of your Home Assistant
configuration (the folder that contains `configuration.yaml`) and restart Home Assistant.

## Configuration

Enter the **API key**, **access token** and **refresh token**. All washers of the account are added.
The tokens rotate; the integration stores the new ones itself. When they become invalid Home Assistant asks
for new ones (re-authentication).

## Dashboard card

The card is served by the integration, it is available right after a restart:

```yaml
type: custom:aeg-pracka-card
name: Washer          # optional
device_id: abc123…    # optional, only with more than one washer
```

It shows a progress ring with a spinning drum, status, programme and phase, door state, temperature, spin,
time remaining and end time, and buttons that follow the state (start → pause/stop → resume) with a confirmation.
The card follows the Home Assistant language.

## Automation example

```yaml
triggers:
  - trigger: state
    entity_id: sensor.washer_status
    from: [running, paused]
    to: end_of_cycle
actions:
  - action: notify.mobile_app_phone
    data:
      message: "Washing finished ({{ states('sensor.washer_programme') }})."
```

States are keys (`running`, `end_of_cycle`, `cotton_pr_cottons` …) and shown translated in the UI.

## Troubleshooting

Add this to `configuration.yaml` to get debug logs, then reproduce the problem and attach the log to an issue:

```yaml
logger:
  logs:
    custom_components.aeg_pracka: debug
```

**Settings → Devices & services → (integration) → ⋮ → Download diagnostics** creates a file without passwords or tokens –
attach it to bug reports.

## Support

Found a bug or have an idea? [Open an issue](https://github.com/ktlko/ha-aeg-washer/issues).

If this integration saves you time, you can support the development:

[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kotelino&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/kotelino)

## License

[MIT](LICENSE) – this project is not affiliated with or endorsed by the device manufacturers.
