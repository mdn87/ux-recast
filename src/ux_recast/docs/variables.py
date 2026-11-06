"""The variable table: every value on a sheet, with its unit and where it came from (C-40, C-41, C-44).

An entry is ``{code, name, value | "[TBD]", unit, source, state, viewport, ...}``. ``code`` is what
the drawing shows (``S1``), ``name`` is the stable variable name (``row-pad-y``). Every value
names its unit; a bare number is refused because a CSS pixel, a screenshot pixel, a ratio and an
SVG user unit look the same without one (C-41). Unknown values stay ``[TBD]`` and are counted.

``source`` says where the value came from, and each source carries what a later check needs to
re-read it:

- ``token`` and ``css-literal``: ``file``, ``line``, ``revision`` and the ``literal`` text at that
  line with ``{}`` where the value sits (``padding:{} 12px``), so the check pins this value and
  not a neighbour (``token`` also names the custom property);
- ``accepted``: the same, pointing at the accepted design record, plus the ``decision``;
- ``rendered``: the ``part`` and ``property`` measured, at a ``revision``, ``viewport``,
  ``device_pixel_ratio`` and ``engine``, with the ``tolerance`` a re-measurement must meet;
- ``proposed``: the ``proposal`` it comes from; not traceable, so a reviewer checks it.

Any entry may add a ``formula`` over other codes (``H1 - 2*S1``); the value must equal its result.
"""
import ast
import math
import re

from ux_recast.contracts import ContractError

TBD = "[TBD]"
SOURCES = ("token", "css-literal", "rendered", "accepted", "proposed")
UNITS = {"px", "%", "ratio", "color", "integer", "weight", "svg-user", "em", "rem", "ms", "s", "deg", "keyword"}
NUMERIC_UNITS = UNITS - {"color", "keyword", "integer", "weight"}
CODE = re.compile(r"^[A-Z][A-Z0-9]{0,5}$")
NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
HEX = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
NUMERIC_TEXT = re.compile(r"^\s*[-+]?(?:\d+\.?\d*|\.\d+)")
VIEWPORT = re.compile(r"^(?:any|\d{2,5}x\d{2,5})$")
TRACE_FIELDS = {"token": ("file", "line", "revision", "literal", "token"),
                "css-literal": ("file", "line", "revision", "literal"),
                "accepted": ("file", "line", "revision", "literal", "decision"),
                "rendered": ("part", "property", "revision", "engine"),
                "proposed": ("proposal",)}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _check_value(entry, where):
    value, unit = entry.get("value"), entry.get("unit")
    if not isinstance(unit, str) or not unit.strip():
        raise ContractError(f"{where}.unit", "every value names its unit; an unlabeled number is ambiguous")
    if unit not in UNITS:
        raise ContractError(f"{where}.unit", f"{unit!r} not in {sorted(UNITS)}")
    if value == TBD:
        return
    if isinstance(value, str) and unit not in {"color", "keyword"} and NUMERIC_TEXT.match(value):
        raise ContractError(f"{where}.value", "a number is written as a JSON number with its unit in 'unit'")
    if unit == "color":
        if not (isinstance(value, str) and HEX.match(value)):
            raise ContractError(f"{where}.value", "a color is a hex value such as #ff685f")
    elif unit == "keyword":
        if not (isinstance(value, str) and value.strip()) or NUMERIC_TEXT.match(value):
            raise ContractError(f"{where}.value", "a keyword is a word; a number needs a numeric unit")
    elif unit == "integer":
        if not (isinstance(value, int) and not isinstance(value, bool)):
            raise ContractError(f"{where}.value", "an integer unit (z-index, count) takes a whole number")
    elif unit == "weight":
        if not (isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 1000):
            raise ContractError(f"{where}.value", "a font weight is a whole number from 1 to 1000")
    elif not _number(value):
        raise ContractError(f"{where}.value", f"a {unit} value is a number or {TBD}")


def validate_entry(entry, where="variable"):
    if not isinstance(entry, dict):
        raise ContractError(where, "expected object")
    if not (isinstance(entry.get("code"), str) and CODE.match(entry["code"])):
        raise ContractError(f"{where}.code", "a drawing code such as S1, H2 or R1")
    if not (isinstance(entry.get("name"), str) and NAME.match(entry["name"])):
        raise ContractError(f"{where}.name", "a stable lowercase hyphenated variable name")
    if "value" not in entry:
        raise ContractError(f"{where}.value", f"missing; an unknown value is {TBD}")
    _check_value(entry, where)
    source = entry.get("source")
    if source not in SOURCES:
        raise ContractError(f"{where}.source", f"{source!r} not in {list(SOURCES)}")
    for key in ("state", "viewport"):
        if not (isinstance(entry.get(key), str) and entry[key].strip()):
            raise ContractError(f"{where}.{key}", "say which state and viewport the value holds for")
    if not VIEWPORT.match(entry["viewport"]):
        raise ContractError(f"{where}.viewport", "WIDTHxHEIGHT in CSS px, or 'any'")
    if entry["value"] == TBD:
        return entry
    for key in TRACE_FIELDS[source]:
        if key not in entry or entry[key] in ("", None):
            raise ContractError(f"{where}.{key}", f"a {source} value records {key} so it can be re-checked")
    if source in {"token", "css-literal", "accepted"}:
        if not (isinstance(entry["line"], int) and entry["line"] >= 1):
            raise ContractError(f"{where}.line", "a 1-based line number")
        if not isinstance(entry["literal"], str) or entry["literal"].count("{}") != 1:
            raise ContractError(f"{where}.literal", "the source text with one {} where the value sits")
    if source == "rendered":
        if entry["viewport"] == "any":
            raise ContractError(f"{where}.viewport", "a rendered value was measured at one viewport")
        if not (_number(entry.get("device_pixel_ratio")) and entry["device_pixel_ratio"] > 0):
            raise ContractError(f"{where}.device_pixel_ratio", "a rendered value records the device pixel ratio")
        if not (_number(entry.get("tolerance")) and entry["tolerance"] >= 0):
            raise ContractError(f"{where}.tolerance", "a rendered value states the tolerance a re-measurement must meet")
        if entry["unit"] not in NUMERIC_UNITS:
            raise ContractError(f"{where}.unit", "a rendered measurement is numeric")
    return entry


def validate_table(entries, where="variables"):
    """Validate every entry and every formula; return ``{count, tbd, tbd_ratio}``."""
    if not isinstance(entries, list) or not entries:
        raise ContractError(where, "expected a non-empty list of variables")
    codes, names = {}, set()
    for index, entry in enumerate(entries):
        validate_entry(entry, f"{where}[{index}]")
        if entry["code"] in codes:
            raise ContractError(f"{where}[{index}].code", f"duplicate code {entry['code']}")
        if entry["name"] in names:
            raise ContractError(f"{where}[{index}].name", f"duplicate name {entry['name']}")
        codes[entry["code"]] = entry
        names.add(entry["name"])
    for index, entry in enumerate(entries):
        if "formula" not in entry:
            continue
        w = f"{where}[{index}].formula"
        if entry["value"] == TBD:
            raise ContractError(w, f"a formula has a result; a {TBD} value has no formula")
        result = evaluate(entry["formula"], codes, w)
        if not math.isclose(result, entry["value"], abs_tol=max(1e-6, entry.get("tolerance", 0) or 0)):
            raise ContractError(w, f"{entry['formula']} = {format_number(result)}, not {entry['value']}")
    tbd = sum(1 for entry in entries if entry["value"] == TBD)
    return {"count": len(entries), "tbd": tbd, "tbd_ratio": round(tbd / len(entries), 4)}


_OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b}


def evaluate(formula, codes, where="formula"):
    """Evaluate ``formula`` over the numeric values of ``codes``; only + - * / and parentheses."""
    if not isinstance(formula, str) or not formula.strip():
        raise ContractError(where, "empty formula")
    try:
        tree = ast.parse(formula.replace("·", "*").replace("÷", "/").replace("−", "-"), mode="eval")
    except SyntaxError as error:
        raise ContractError(where, f"not a formula: {error.msg}") from None

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.Constant) and _number(node.value):
            return node.value
        if isinstance(node, ast.Name):
            entry = codes.get(node.id)
            if entry is None:
                raise ContractError(where, f"{node.id} is not a code in this table")
            if not _number(entry["value"]):
                raise ContractError(where, f"{node.id} is {entry['value']!r}, not a number")
            return entry["value"]
        raise ContractError(where, "only codes, numbers, + - * / and parentheses")
    return walk(tree)


def format_number(value):
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return repr(value) if isinstance(value, float) else str(value)


def css_tokens(entry):
    """The spellings of ``entry``'s value that may appear in CSS source, most specific first."""
    value, unit = entry["value"], entry["unit"]
    if unit == "color":
        return [value.lower()]
    if unit == "keyword":
        return [value]
    number = format_number(value)
    suffix = {"px": "px", "%": "%", "em": "em", "rem": "rem", "ms": "ms", "s": "s", "deg": "deg"}.get(unit, "")
    # Design prose writes "44 px"; CSS writes "44px".
    spellings = [number + suffix] + ([f"{number} {suffix}"] if suffix not in {"", "%"} else [])
    if number.startswith("0.") and suffix != "%":
        spellings.append(number[1:] + suffix)
    if value == 0 and suffix:
        spellings.append("0")
    return spellings


def literal_holds(entry, text):
    """True when ``text`` (the recorded source line) holds the literal with this value in its slot."""
    if entry["unit"] == "color":
        text = text.lower()
    return any(entry["literal"].replace("{}", token) in text for token in css_tokens(entry))


def display(entry):
    """How a value reads in a sheet's table: ``10 px``, ``1.45``, ``#ff685f``, ``[TBD]``."""
    value, unit = entry["value"], entry["unit"]
    if value == TBD:
        return TBD
    if unit in {"color", "keyword"}:
        return value
    number = format_number(value)
    return number if unit in {"ratio", "integer", "weight", "svg-user"} else f"{number} {unit}" if unit != "%" else number + "%"
