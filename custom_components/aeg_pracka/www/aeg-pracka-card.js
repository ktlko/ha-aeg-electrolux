/* AEG / Electrolux washer card – bundled with the aeg_pracka integration. */
const KEYS = {
  sensor: ["stav", "program", "faza", "zostava", "koniec", "priebeh", "teplota", "odstredovanie", "upozornenia", "pocet_cyklov"],
  binary_sensor: ["perie", "dvierka", "zamok_dvierok", "pripojenie", "doprate"],
  button: ["start", "pauza", "pokracovat", "stop", "zapnut"],
};

const COLORS = {
  running: "#3b9cff",
  paused: "#f5a623",
  delayed_start: "#a78bfa",
  end_of_cycle: "#34c77b",
  ready_to_start: "#9aa4b2",
  idle: "#6b7280",
  off: "#4b5563",
  alarm: "#ef4444",
};

const I18N = {
  en: {
    name: "Washer", none: "The AEG / Electrolux integration has no entities yet.", unavailable: "Unavailable",
    remaining: "Remaining", ends: "Ends at", temp: "Temperature", spin: "Spin",
    pause: "Pause", stop: "Stop", resume: "Resume", cancel: "Cancel", start: "Start", on: "Turn on",
    q_stop: "Stop the wash?", q_cancel: "Cancel the wash?", q_delay: "Cancel the delayed start?", q_start: "Start programme {p}?",
    done: "Laundry is done – you can take it out", program: "Programme: {p}",
    door_open: "Door open", door_closed: "Door closed", locked: "Locked", alerts: "Alerts: {n}",
    h: "h", min: "min", desc: "Status, progress and control of the washer from the AEG / Electrolux integration.",
  },
  sk: {
    name: "Práčka", none: "Integrácia AEG / Electrolux zatiaľ nemá žiadne entity.", unavailable: "Nedostupná",
    remaining: "Zostáva", ends: "Koniec o", temp: "Teplota", spin: "Otáčky",
    pause: "Pauza", stop: "Stop", resume: "Pokračovať", cancel: "Zrušiť", start: "Štart", on: "Zapnúť",
    q_stop: "Naozaj zastaviť pranie?", q_cancel: "Naozaj zrušiť pranie?", q_delay: "Zrušiť odložený štart?", q_start: "Spustiť program {p}?",
    done: "Bielizeň je hotová – môžete vybrať", program: "Program: {p}",
    door_open: "Dvierka otvorené", door_closed: "Dvierka zatvorené", locked: "Zamknuté", alerts: "Upozornenia: {n}",
    h: "h", min: "min", desc: "Stav, priebeh a ovládanie práčky z integrácie AEG / Electrolux.",
  },
  cs: {
    name: "Pračka", none: "Integrace AEG / Electrolux zatím nemá žádné entity.", unavailable: "Nedostupná",
    remaining: "Zbývá", ends: "Konec v", temp: "Teplota", spin: "Otáčky",
    pause: "Pauza", stop: "Stop", resume: "Pokračovat", cancel: "Zrušit", start: "Start", on: "Zapnout",
    q_stop: "Opravdu zastavit praní?", q_cancel: "Opravdu zrušit praní?", q_delay: "Zrušit odložený start?", q_start: "Spustit program {p}?",
    done: "Prádlo je hotové – můžete ho vyndat", program: "Program: {p}",
    door_open: "Dvířka otevřená", door_closed: "Dvířka zavřená", locked: "Zamčeno", alerts: "Upozornění: {n}",
    h: "h", min: "min", desc: "Stav, průběh a ovládání pračky z integrace AEG / Electrolux.",
  },
  de: {
    name: "Waschmaschine", none: "Die Integration AEG / Electrolux hat noch keine Entitäten.", unavailable: "Nicht verfügbar",
    remaining: "Restzeit", ends: "Ende um", temp: "Temperatur", spin: "Schleudern",
    pause: "Pause", stop: "Stopp", resume: "Fortsetzen", cancel: "Abbrechen", start: "Start", on: "Einschalten",
    q_stop: "Waschgang wirklich stoppen?", q_cancel: "Waschgang wirklich abbrechen?", q_delay: "Startzeitvorwahl abbrechen?", q_start: "Programm {p} starten?",
    done: "Die Wäsche ist fertig – du kannst sie herausnehmen", program: "Programm: {p}",
    door_open: "Tür offen", door_closed: "Tür geschlossen", locked: "Verriegelt", alerts: "Hinweise: {n}",
    h: "Std.", min: "Min.", desc: "Status, Fortschritt und Steuerung der Waschmaschine aus der Integration AEG / Electrolux.",
  },
  pl: {
    name: "Pralka", none: "Integracja AEG / Electrolux nie ma jeszcze żadnych encji.", unavailable: "Niedostępna",
    remaining: "Pozostało", ends: "Koniec o", temp: "Temperatura", spin: "Wirowanie",
    pause: "Pauza", stop: "Stop", resume: "Wznów", cancel: "Anuluj", start: "Start", on: "Włącz",
    q_stop: "Na pewno zatrzymać pranie?", q_cancel: "Na pewno anulować pranie?", q_delay: "Anulować opóźniony start?", q_start: "Uruchomić program {p}?",
    done: "Pranie gotowe – możesz je wyjąć", program: "Program: {p}",
    door_open: "Drzwi otwarte", door_closed: "Drzwi zamknięte", locked: "Zablokowane", alerts: "Ostrzeżenia: {n}",
    h: "godz.", min: "min", desc: "Stan, postęp i sterowanie pralką z integracji AEG / Electrolux.",
  },
  es: {
    name: "Lavadora", none: "La integración AEG / Electrolux aún no tiene entidades.", unavailable: "No disponible",
    remaining: "Restante", ends: "Termina a las", temp: "Temperatura", spin: "Centrifugado",
    pause: "Pausa", stop: "Detener", resume: "Reanudar", cancel: "Cancelar", start: "Iniciar", on: "Encender",
    q_stop: "¿Detener el lavado?", q_cancel: "¿Cancelar el lavado?", q_delay: "¿Cancelar el inicio diferido?", q_start: "¿Iniciar el programa {p}?",
    done: "La colada está lista – ya puedes sacarla", program: "Programa: {p}",
    door_open: "Puerta abierta", door_closed: "Puerta cerrada", locked: "Bloqueada", alerts: "Avisos: {n}",
    h: "h", min: "min", desc: "Estado, progreso y control de la lavadora de la integración AEG / Electrolux.",
  },
  it: {
    name: "Lavatrice", none: "L'integrazione AEG / Electrolux non ha ancora entità.", unavailable: "Non disponibile",
    remaining: "Rimanente", ends: "Termina alle", temp: "Temperatura", spin: "Centrifuga",
    pause: "Pausa", stop: "Stop", resume: "Riprendi", cancel: "Annulla", start: "Avvia", on: "Accendi",
    q_stop: "Fermare il lavaggio?", q_cancel: "Annullare il lavaggio?", q_delay: "Annullare la partenza ritardata?", q_start: "Avviare il programma {p}?",
    done: "Il bucato è pronto – puoi estrarlo", program: "Programma: {p}",
    door_open: "Oblò aperto", door_closed: "Oblò chiuso", locked: "Bloccato", alerts: "Avvisi: {n}",
    h: "h", min: "min", desc: "Stato, avanzamento e controllo della lavatrice dall'integrazione AEG / Electrolux.",
  },
};

const lang = (hass) => {
  const code = (hass?.locale?.language || hass?.language || "en").slice(0, 2);
  return I18N[code] || I18N.en;
};

class AegPrackaCard extends HTMLElement {
  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._ids = null;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
  }

  getCardSize() {
    return 4;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, rows: "auto" };
  }

  _resolve(hass) {
    // Map translation keys -> entity ids for the chosen (or first) washer.
    const all = Object.values(hass.entities).filter((e) => e.platform === "aeg_pracka");
    const deviceId = this._config.device_id || all.find((e) => e.device_id)?.device_id;
    const mine = all.filter((e) => e.device_id === deviceId);
    const map = {};
    for (const [domain, keys] of Object.entries(KEYS)) {
      for (const key of keys) {
        const hit =
          mine.find((e) => e.translation_key === key && e.entity_id.startsWith(domain + ".")) ||
          mine.find((e) => e.entity_id.startsWith(domain + ".") && e.entity_id.endsWith("_" + key));
        if (hit) map[`${domain}.${key}`] = hit.entity_id;
      }
    }
    return map;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._config) return;
    if (!this._ids || !Object.keys(this._ids).length) this._ids = this._resolve(hass);
    const sig =
      (hass.locale?.language || "") +
      Object.values(this._ids)
        .map((id) => `${hass.states[id]?.state}|${hass.states[id]?.last_updated}`)
        .join(";");
    if (sig === this._sig && this.shadowRoot.innerHTML) return;
    this._sig = sig;
    this._render();
  }

  _st(key) {
    const id = this._ids[key];
    return id ? this._hass.states[id] : undefined;
  }

  _fmt(key) {
    const s = this._st(key);
    if (!s || ["unknown", "unavailable"].includes(s.state)) return null;
    return this._hass.formatEntityState ? this._hass.formatEntityState(s) : s.state;
  }

  _fmtDuration(min, t) {
    const m = Math.max(0, Math.round(Number(min) || 0));
    const h = Math.floor(m / 60);
    return h ? `${h} ${t.h} ${String(m % 60).padStart(2, "0")} ${t.min}` : `${m} ${t.min}`;
  }

  _fmtTime(iso) {
    if (!iso || iso === "unknown" || iso === "unavailable") return null;
    const d = new Date(iso);
    if (isNaN(d)) return null;
    return d.toLocaleTimeString(this._hass.locale?.language || undefined, { hour: "2-digit", minute: "2-digit" });
  }

  _press(key, question) {
    const id = this._ids[`button.${key}`];
    if (!id) return;
    if (question && !confirm(question)) return;
    this._hass.callService("button", "press", { entity_id: id });
  }

  _moreInfo(key) {
    const entityId = this._ids[key];
    if (!entityId) return;
    this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }));
  }

  _render() {
    const root = this.shadowRoot;
    const t = lang(this._hass);
    if (!Object.keys(this._ids).length) {
      root.innerHTML = `<ha-card><div style="padding:16px">${t.none}</div></ha-card>`;
      return;
    }
    const stateObj = this._st("sensor.stav");
    const state = stateObj?.state ?? "unavailable";
    const color = COLORS[state] || "#6b7280";
    const label = state === "unavailable" ? t.unavailable : this._fmt("sensor.stav") || state;
    const active = ["running", "paused", "delayed_start"].includes(state);
    const done = state === "end_of_cycle";

    const program = this._fmt("sensor.program");
    const phaseState = this._st("sensor.faza")?.state;
    const phase = phaseState && !["none", "unknown", "unavailable"].includes(phaseState) ? this._fmt("sensor.faza") : null;
    const progress = Number(this._st("sensor.priebeh")?.state);
    const pct = done ? 100 : active && !isNaN(progress) ? progress : 0;
    const remaining = this._st("sensor.zostava")?.state;
    const endAt = this._fmtTime(this._st("sensor.koniec")?.state);
    const temp = this._fmt("sensor.teplota");
    const spin = this._fmt("sensor.odstredovanie");
    const doorOpen = this._st("binary_sensor.dvierka")?.state === "on";
    const locked = this._st("binary_sensor.zamok_dvierok")?.state === "off";
    const online = this._st("binary_sensor.pripojenie")?.state !== "off";
    const alerts = Number(this._st("sensor.upozornenia")?.state) || 0;
    const name = this._config.name || t.name;

    const R = 46;
    const C = 2 * Math.PI * R;
    const spinning = state === "running";

    const chips = [];
    if (active && remaining && !isNaN(Number(remaining))) chips.push(["mdi:timer-sand", t.remaining, this._fmtDuration(remaining, t)]);
    if (active && endAt) chips.push(["mdi:clock-end", t.ends, endAt]);
    if (temp) chips.push(["mdi:thermometer-water", t.temp, temp]);
    if (spin) chips.push(["mdi:rotate-right", t.spin, spin]);

    const buttons = [];
    if (state === "running") {
      buttons.push(["pauza", "mdi:pause", t.pause]);
      buttons.push(["stop", "mdi:stop", t.stop, t.q_stop]);
    } else if (state === "paused") {
      buttons.push(["pokracovat", "mdi:play", t.resume]);
      buttons.push(["stop", "mdi:stop", t.stop, t.q_cancel]);
    } else if (state === "delayed_start") {
      buttons.push(["stop", "mdi:stop", t.cancel, t.q_delay]);
    } else if (state === "ready_to_start" || state === "idle") {
      buttons.push(["start", "mdi:play", t.start, t.q_start.replace("{p}", program || "")]);
    } else if (state === "off") {
      buttons.push(["zapnut", "mdi:power", t.on]);
    }

    const subtitle = done
      ? t.done
      : active
        ? [program, phase].filter(Boolean).join(" · ")
        : program
          ? t.program.replace("{p}", program)
          : "";

    root.innerHTML = `
      <style>
        :host { --c: ${color}; }
        ha-card { padding: 16px; overflow: hidden; position: relative; }
        ha-card::before {
          content: ""; position: absolute; inset: 0; pointer-events: none;
          background: radial-gradient(120% 90% at 0% 0%, color-mix(in srgb, var(--c) 22%, transparent), transparent 60%);
        }
        .top { display: flex; gap: 16px; align-items: center; position: relative; }
        .ring { position: relative; width: 108px; height: 108px; flex: none; cursor: pointer; }
        .ring svg { transform: rotate(-90deg); }
        .ring .bg { stroke: color-mix(in srgb, var(--primary-text-color) 10%, transparent); }
        .ring .fg { stroke: var(--c); transition: stroke-dashoffset .8s ease; stroke-linecap: round; }
        .drum {
          position: absolute; inset: 18px; border-radius: 50%;
          display: grid; place-items: center;
          background: color-mix(in srgb, var(--c) 16%, var(--card-background-color, #1c1c1c));
          border: 3px solid color-mix(in srgb, var(--c) 45%, transparent);
        }
        .drum ha-icon { --mdc-icon-size: 38px; color: var(--c); display: flex; }
        .drum.spin ha-icon { animation: spin 1.6s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .pct { position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%);
          font-size: 12px; font-weight: 700; padding: 1px 8px; border-radius: 10px;
          background: var(--c); color: #fff; }
        .info { min-width: 0; flex: 1; }
        .name { font-size: 13px; opacity: .65; display: flex; align-items: center; gap: 6px; }
        .name ha-icon { --mdc-icon-size: 16px; }
        .state { font-size: 22px; font-weight: 600; color: var(--c); margin: 2px 0; cursor: pointer; }
        .sub { font-size: 14px; opacity: .85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .badges { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
        .badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; display: inline-flex; gap: 4px; align-items: center;
          background: color-mix(in srgb, var(--primary-text-color) 8%, transparent); }
        .badge ha-icon { --mdc-icon-size: 14px; }
        .badge.warn { background: color-mix(in srgb, #ef4444 25%, transparent); color: #ef4444; }
        .chips { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 8px; margin-top: 16px; position: relative; }
        .chip { border-radius: 12px; padding: 8px 10px;
          background: color-mix(in srgb, var(--primary-text-color) 6%, transparent); }
        .chip .l { font-size: 11px; opacity: .6; display: flex; align-items: center; gap: 4px; }
        .chip .l ha-icon { --mdc-icon-size: 14px; }
        .chip .v { font-size: 15px; font-weight: 600; margin-top: 2px; }
        .actions { display: flex; gap: 8px; margin-top: 14px; position: relative; }
        button { flex: 1; border: 0; border-radius: 12px; padding: 10px; font: inherit; font-weight: 600;
          display: inline-flex; gap: 6px; justify-content: center; align-items: center; cursor: pointer;
          background: color-mix(in srgb, var(--c) 18%, transparent); color: var(--primary-text-color); }
        button:hover { background: color-mix(in srgb, var(--c) 30%, transparent); }
        button.stop { background: color-mix(in srgb, #ef4444 18%, transparent); }
        button ha-icon { --mdc-icon-size: 18px; }
      </style>
      <ha-card>
        <div class="top">
          <div class="ring" id="ring">
            <svg width="108" height="108" viewBox="0 0 108 108">
              <circle class="bg" cx="54" cy="54" r="${R}" fill="none" stroke-width="8"></circle>
              <circle class="fg" cx="54" cy="54" r="${R}" fill="none" stroke-width="8"
                stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - pct / 100)}"></circle>
            </svg>
            <div class="drum ${spinning ? "spin" : ""}">
              <ha-icon icon="${done ? "mdi:check-bold" : state === "off" ? "mdi:washing-machine-off" : "mdi:washing-machine"}"></ha-icon>
            </div>
            ${active || done ? `<div class="pct">${Math.round(pct)} %</div>` : ""}
          </div>
          <div class="info">
            <div class="name">${name}
              ${online ? "" : `<ha-icon icon="mdi:wifi-off" title="Offline"></ha-icon>`}</div>
            <div class="state" id="state">${label}</div>
            <div class="sub">${subtitle || "&nbsp;"}</div>
            <div class="badges">
              <span class="badge"><ha-icon icon="${doorOpen ? "mdi:door-open" : "mdi:door-closed"}"></ha-icon>${doorOpen ? t.door_open : t.door_closed}</span>
              ${locked ? `<span class="badge"><ha-icon icon="mdi:lock"></ha-icon>${t.locked}</span>` : ""}
              ${alerts ? `<span class="badge warn"><ha-icon icon="mdi:alert"></ha-icon>${t.alerts.replace("{n}", alerts)}</span>` : ""}
            </div>
          </div>
        </div>
        ${chips.length ? `<div class="chips">${chips
          .map(([i, l, v]) => `<div class="chip"><div class="l"><ha-icon icon="${i}"></ha-icon>${l}</div><div class="v">${v}</div></div>`)
          .join("")}</div>` : ""}
        ${buttons.length ? `<div class="actions">${buttons
          .map(([k, i, l, q]) => `<button data-k="${k}" data-q="${q || ""}" class="${k === "stop" ? "stop" : ""}"><ha-icon icon="${i}"></ha-icon>${l}</button>`)
          .join("")}</div>` : ""}
      </ha-card>`;

    root.querySelectorAll("button[data-k]").forEach((b) =>
      b.addEventListener("click", () => this._press(b.dataset.k, b.dataset.q))
    );
    root.getElementById("ring")?.addEventListener("click", () => this._moreInfo("sensor.priebeh"));
    root.getElementById("state")?.addEventListener("click", () => this._moreInfo("sensor.stav"));
  }
}

if (!customElements.get("aeg-pracka-card")) {
  customElements.define("aeg-pracka-card", AegPrackaCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "aeg-pracka-card",
    name: "AEG / Electrolux washer",
    description: lang(document.querySelector("home-assistant")?.hass).desc,
    preview: true,
  });
}
