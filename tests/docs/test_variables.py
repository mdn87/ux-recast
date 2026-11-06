"""S6.5: the variable schema accepts the corpus's valid cases, refuses the invalid ones, and reports the [TBD] ratio."""
import json
from pathlib import Path
import unittest

from ux_recast.contracts import ContractError
from ux_recast.docs import variables

CORPUS = Path(__file__).parent / "validator_corpus"


def cases(folder):
    return sorted((CORPUS / folder).glob("*.json"))


class Corpus(unittest.TestCase):
    def test_corpus_covers_the_required_shapes(self):
        names = {path.stem for path in cases("valid")} | {path.stem for path in cases("invalid")}
        for needed in ("zero-px", "unitless-line-height", "hex-color", "z-index", "percentage", "svg-attribute",
                       "bare-number", "zero-unlabelled", "line-height-unlabelled", "svg-attribute-unlabelled"):
            self.assertIn(needed, names)

    def test_valid_cases(self):
        for path in cases("valid"):
            with self.subTest(case=path.stem):
                variables.validate_table(json.loads(path.read_text(encoding="utf-8"))["entries"])

    def test_invalid_cases_name_the_field(self):
        for path in cases("invalid"):
            case = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(case=path.stem), self.assertRaises(ContractError) as caught:
                variables.validate_table(case["entries"])
            self.assertIn(case["field"], caught.exception.field, f"{path.stem}: {caught.exception}")

    def test_every_unlabelled_numeric_fails(self):
        for value in (0, 1, 1.45, 14, 999, -2):
            entry = json.loads((CORPUS / "valid" / "zero-px.json").read_text(encoding="utf-8"))["entries"][0]
            entry.update(value=value, unit="")
            with self.subTest(value=value), self.assertRaises(ContractError):
                variables.validate_table([entry])


class Ratio(unittest.TestCase):
    def test_tbd_ratio(self):
        entries = (json.loads((CORPUS / "valid" / "formula.json").read_text(encoding="utf-8"))["entries"]
                   + json.loads((CORPUS / "valid" / "tbd.json").read_text(encoding="utf-8"))["entries"])
        self.assertEqual(variables.validate_table(entries), {"count": 4, "tbd": 1, "tbd_ratio": 0.25})


class Literals(unittest.TestCase):
    def entry(self, value, unit, literal):
        return {"value": value, "unit": unit, "literal": literal}

    def test_the_slot_pins_one_value(self):
        line = ".row{padding:10px 12px;}"
        self.assertTrue(variables.literal_holds(self.entry(10, "px", "padding:{} 12px"), line))
        self.assertFalse(variables.literal_holds(self.entry(12, "px", "padding:{} 12px"), line))
        self.assertTrue(variables.literal_holds(self.entry(12, "px", "padding:10px {}"), line))

    def test_spellings(self):
        self.assertTrue(variables.literal_holds(self.entry(0, "px", "margin:{} auto"), "margin:0 auto"))
        self.assertTrue(variables.literal_holds(self.entry(0.5, "px", "inset:{}"), "inset:.5px"))
        self.assertTrue(variables.literal_holds(self.entry("#FF685F", "color", "--red:{}"), "--red:#ff685f;"))
        self.assertTrue(variables.literal_holds(self.entry(1.45, "ratio", "font:14px/{}"), "font:14px/1.45 x"))
        self.assertTrue(variables.literal_holds(self.entry(50, "%", "border-radius:{}"), "border-radius:50%"))

    def test_display(self):
        self.assertEqual(variables.display({"value": 10, "unit": "px"}), "10 px")
        self.assertEqual(variables.display({"value": 1.45, "unit": "ratio"}), "1.45")
        self.assertEqual(variables.display({"value": 100, "unit": "%"}), "100%")
        self.assertEqual(variables.display({"value": "[TBD]", "unit": "px"}), "[TBD]")


if __name__ == "__main__":
    unittest.main()
