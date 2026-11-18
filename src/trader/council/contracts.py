from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ROLES = ("technical", "news", "regime", "portfolio", "liquidity")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Reference(Strict):
    path: str = Field(max_length=200)
    value: Any


class Vote(Strict):
    symbol: str
    action: Literal["buy", "sell", "hold"]
    confidence: float = Field(ge=0, le=1)
    evidence: list[Reference] = Field(max_length=12)
    risk_flags: list[str] = Field(max_length=12)


class Report(Strict):
    evidence_pack_id: str
    role: Literal["technical", "news", "regime", "portfolio", "liquidity"]
    votes: list[Vote] = Field(max_length=100)
    rationale: str = Field(max_length=3000)


class Candidate(Strict):
    symbol: str
    action: Literal["buy", "sell", "hold"]
    conviction: float = Field(ge=0, le=1)
    evidence: list[Reference] = Field(max_length=12)


class Draft(Strict):
    evidence_pack_id: str
    candidates: list[Candidate] = Field(max_length=100)
    rationale: str = Field(default="", min_length=1, max_length=800)


class Skeptic(Strict):
    evidence_pack_id: str
    vetoes: list[str] = Field(max_length=100)
    reason_codes: list[str] = Field(max_length=30)


def response_schema(role, pack):
    """Provider constraints complement, rather than replace, local evidence validation."""
    cls = Draft if role == "chair" else (Skeptic if role == "skeptic" else Report)
    schema = cls.model_json_schema()
    if role == "chair":
        # New providers must explain the decision; old stored drafts remain readable.
        schema["required"] = list(schema["properties"])
    schema["properties"]["evidence_pack_id"] = {"type": "string", "enum": [pack.evidence_pack_id]}
    if role in ROLES:
        schema["properties"]["role"] = {"type": "string", "enum": [role]}
    for name in ("Vote", "Candidate"):
        if name in schema.get("$defs", {}):
            schema["$defs"][name]["properties"]["symbol"] = {"type": "string", "enum": sorted(pack.content["symbols"])}
    if "Reference" in schema.get("$defs", {}):
        from trader.council.evidence import compact

        view = compact(pack.content, role)
        paths = []
        groups = [
            *(("symbols." + symbol, values) for symbol, values in view["symbols"].items()),
            ("portfolio", view["portfolio"]),
            ("market", view["market"]),
        ]
        for prefix, values in groups:
            for name, row in values.items():
                value = row["v"]
                citable = isinstance(value, (str, int, float, bool)) or (
                    isinstance(value, list) and all(isinstance(v, str) for v in value)
                )
                if row["status"] == "OK" and value is not None and citable and not name.startswith("recent_price_"):
                    paths.append(prefix + "." + name)
        if paths:
            schema["$defs"]["Reference"]["properties"]["path"] = {"type": "string", "enum": sorted(paths)}
        else:
            for name in ("Vote", "Candidate"):
                if name in schema.get("$defs", {}):
                    schema["$defs"][name]["properties"]["evidence"]["maxItems"] = 0
        # Citable features have scalar or string-array values; candle objects are context only. Avoid Any
        # objects, which strict JSON-schema providers cannot represent as a closed object.
        schema["$defs"]["Reference"]["properties"]["value"] = {
            "anyOf": [
                {"type": "number"},
                {"type": "string"},
                {"type": "boolean"},
                {"type": "array", "items": {"type": "string"}},
            ]
        }
    return schema


def validate_output(role, raw, pack):
    cls = Draft if role == "chair" else (Skeptic if role == "skeptic" else Report)
    result = cls.model_validate_json(raw)
    if result.evidence_pack_id != pack.evidence_pack_id:
        raise ValueError("wrong evidence pack")
    if isinstance(result, Report) and result.role != role:
        raise ValueError("wrong council role")
    symbols = set(pack.content["symbols"])
    items = result.votes if isinstance(result, Report) else (result.candidates if isinstance(result, Draft) else [])
    seen = set()
    for item in items:
        if item.symbol not in symbols or item.symbol in seen:
            raise ValueError("unknown or duplicate symbol")
        seen.add(item.symbol)
        if item.action != "hold" and not item.evidence:
            raise ValueError("action lacks evidence")
        for ref in item.evidence:
            path = ref.path.split(".")
            if path[0] not in ("symbols", "market", "portfolio"):
                raise ValueError("invalid evidence path")
            value = pack.content
            for segment in path:
                value = value[segment]
            if not isinstance(value, dict) or value.get("status") != "OK" or value.get("v") != ref.value:
                raise ValueError("unsupported evidence claim")
    if isinstance(result, Report) and seen != symbols:
        raise ValueError("member omitted symbols")
    if isinstance(result, Skeptic) and set(result.vetoes) - symbols:
        raise ValueError("unknown skeptic veto")
    return result
