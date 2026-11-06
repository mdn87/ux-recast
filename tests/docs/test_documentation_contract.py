"""S6.1: the documentation request's three flags are independent, and motion needs a sheet."""
import copy
import unittest

from ux_recast.contracts import ContractError, schema, validate

BASE = {"schema": "ux-recast/documentation-request@1", "request_kind": "documentation", "project": "demo",
        "subject": "Card", "basis": "accepted", "basis_reference": "D-1",
        "outputs": {"guide": True, "sheets": True, "motion": False}, "components": ["card"],
        "inputs": [{"path": "DESIGN.md", "role": "design"}], "out_dir": "docs/design"}


def request(**changes):
    value = copy.deepcopy(BASE)
    value.update(changes)
    return value


class Flags(unittest.TestCase):
    def test_each_output_alone(self):
        validate("documentation", request(outputs={"guide": True}, components=[]))
        validate("documentation", request(outputs={"sheets": True}))
        validate("documentation", request(outputs={"motion": True}, components=[], existing_sheets=["docs/design/sheets/card.html"]))

    def test_guide_with_sheets_and_motion(self):
        validate("documentation", request(outputs={"guide": True, "sheets": True, "motion": True}))

    def test_motion_without_a_sheet_is_refused(self):
        with self.assertRaises(ContractError) as caught:
            validate("documentation", request(outputs={"guide": True, "motion": True}, components=[]))
        self.assertEqual(caught.exception.field, "documentation.outputs.motion")

    def test_nothing_requested_is_refused(self):
        with self.assertRaises(ContractError):
            validate("documentation", request(outputs={"guide": False, "sheets": False, "motion": False}, components=[]))

    def test_flags_are_booleans(self):
        with self.assertRaises(ContractError):
            validate("documentation", request(outputs={"guide": "yes"}))

    def test_sheets_name_components(self):
        with self.assertRaises(ContractError):
            validate("documentation", request(outputs={"sheets": True}, components=[]))
        with self.assertRaises(ContractError):
            validate("documentation", request(outputs={"guide": True}, components=["card"]))


class Basis(unittest.TestCase):
    def test_basis_values(self):
        validate("documentation", request(basis="observed", basis_reference=""))
        with self.assertRaises(ContractError):
            validate("documentation", request(basis="inferred"))

    def test_accepted_and_proposed_name_what_they_rest_on(self):
        for basis in ("accepted", "proposed"):
            with self.subTest(basis=basis), self.assertRaises(ContractError):
                validate("documentation", request(basis=basis, basis_reference=""))


class Inputs(unittest.TestCase):
    def test_a_reference_is_never_approved_guidance(self):
        with self.assertRaises(ContractError):
            validate("documentation", request(inputs=[{"path": "x.png", "role": "reference", "authority": "approved"}]))
        validate("documentation", request(inputs=[{"path": "DESIGN.md", "role": "design"},
                                                   {"path": "x.png", "role": "reference"}]))

    def test_review_mode_is_a_different_request(self):
        with self.assertRaises(ContractError):
            validate("documentation", request(request_kind="review"))

    def test_schema_is_published(self):
        self.assertEqual(schema("documentation")["properties"]["request_kind"]["const"], "documentation")


if __name__ == "__main__":
    unittest.main()
