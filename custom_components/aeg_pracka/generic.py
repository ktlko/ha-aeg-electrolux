"""Entities built from the capabilities the Electrolux API reports for an appliance.

Used for every appliance type without a curated model (ovens partly, fridges, hoods, hobs,
air conditioners, purifiers, dehumidifiers, robot vacuums) and – disabled by default – for the
extra settings of laundry and dish care appliances.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .const import COOK_TYPES
from .coordinator import Washer

# Properties shown by curated entities on every appliance type.
CURATED = {
    "applianceState", "cyclePhase", "cycleSubPhase", "timeToEnd", "doorState", "doorLock", "remoteControl",
    "alerts", "totalCycleCounter", "applianceTotalWorkingTime", "connectivityState",
    "userSelections/programUID", "userSelections/analogTemperature", "userSelections/analogSpinSpeed",
    "networkInterface/linkQualityIndicator", "waterHardness", "measuredLoadWeight", "fcOptisenseLoadWeight",
}
# Extra curated properties of ovens / steam ovens (read-only views; writable ones stay generic too).
CURATED_COOK = {"displayTemperatureC", "targetTemperatureC", "runningTime", "displayFoodProbeTemperatureC"}
# Fahrenheit twins and pure bookkeeping.
IGNORED = re.compile(
    r"(TemperatureF$|Fahrenheit|capabilityHash|applianceTypeProjection|programsOrder|cycleMemory|"
    r"applianceCareAndMaintenance|dummy_for_empty_cycle|^applianceInfo|^networkInterface|SwVersion$|"
    r"clearCyclePersonalizationCmd|^cyclePersonalization|^fCPN_|^category|^miscellaneous)"
)
DURATION_SECONDS = re.compile(r"(timeToEnd|runningTime|targetDuration|startTime|stopTime|Duration|Timer)$", re.I)


@dataclass(frozen=True)
class Spec:
    """One generated entity."""

    path: str
    platform: str  # sensor, binary_sensor, switch, select, number, button
    name: str
    kind: str  # number, string, boolean
    options: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    unit: str | None = None
    command: str | None = None  # button: value written to the property


def humanize(path: str) -> str:
    """'userSelections/EWX1493A_anticreaseNoSteam' -> 'Anticrease no steam'."""
    parts = [p for p in path.split("/") if p not in ("userSelections", "reported")]
    words = []
    for part in parts:
        part = re.sub(r"^[A-Z0-9]{6,}_", "", part)  # model prefixes like EWX1493A_
        part = re.sub(r"(Temperature|Temp)[CF]$", lambda m: m.group(1), part)  # unit suffix
        part = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", part).replace("_", " ").strip()
        words.append(part.lower())
    text = " – ".join(w for w in words if w)
    return text[:1].upper() + text[1:] if text else path


def _unit(path: str) -> str | None:
    last = path.split("/")[-1]
    if re.search(r"(Temperature|Temp)C?$", last) or last.lower() in ("temperature", "targettemperature"):
        return "°C"
    if "humidity" in last.lower():
        return "%"
    if DURATION_SECONDS.search(last):
        return "s"
    return None


def specs(w: Washer) -> list[Spec]:
    """Every entity that can be generated for this appliance."""
    if w.details is None:
        return []
    out: list[Spec] = []
    for path, cap in w.details.capabilities.items():
        if not isinstance(cap, dict) or "type" not in cap:
            continue
        if path in CURATED or IGNORED.search(path):
            continue
        if w.type in COOK_TYPES and path in CURATED_COOK:
            continue
        if w.is_care and path == "executeCommand":
            continue
        ctype = str(cap.get("type")).lower()
        access = str(cap.get("access", "read")).lower()
        name = humanize(path)
        values = w.capability_values(path)
        if ctype == "boolean":
            if "write" in access and "read" in access:
                out.append(Spec(path, "switch", name, "boolean"))
            elif access == "read":
                out.append(Spec(path, "binary_sensor", name, "boolean"))
        elif ctype == "string" and values:
            if access == "write":
                for value in values:
                    out.append(Spec(path, "button", humanize(value), "string", command=value))
            elif "write" in access:
                out.append(Spec(path, "select", name, "string", options=tuple(values)))
            else:
                out.append(Spec(path, "sensor", name, "string", options=tuple(values)))
        elif ctype in ("number", "int", "float", "temperature", "integer"):
            unit = _unit(path)
            if "write" in access and "read" in access and cap.get("min") is not None and cap.get("max") is not None:
                out.append(Spec(path, "number", name, "number", minimum=float(cap["min"]), maximum=float(cap["max"]),
                                step=float(cap.get("step") or 1), unit=unit))
            elif "read" in access:
                out.append(Spec(path, "sensor", name, "number", unit=unit))
    return out


def command(w: Washer, path: str, value: Any) -> dict[str, Any]:
    """Nested command payload for a property path; userSelections need the current programme."""
    keys = path.split("/")
    payload: dict[str, Any] = {}
    node = payload
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value
    if keys[0] == "userSelections" and len(keys) > 1 and (program := w.get("userSelections/programUID")):
        payload["userSelections"].setdefault("programUID", program)
    return payload


def raw_value(w: Washer, spec: Spec) -> Any:
    return w.get(spec.path)
