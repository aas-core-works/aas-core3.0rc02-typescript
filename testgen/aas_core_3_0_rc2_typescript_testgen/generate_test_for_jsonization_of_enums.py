"""Generate the test code for the JSON de/serialization of enums."""

import io
import json
import os
import pathlib
import sys

from aas_core_codegen import intermediate
from aas_core_codegen.common import (
    Stripped,
    Identifier
)
from aas_core_codegen.typescript import (
    common as typescript_common,
    naming as typescript_naming
)
from aas_core_codegen.typescript.common import (
    INDENT as I,
    INDENT2 as II
)

import aas_core_3_0_rc2_typescript_testgen.common


def main() -> int:
    """Execute the main routine."""
    symbol_table = aas_core_3_0_rc2_typescript_testgen.common.load_symbol_table()

    this_path = pathlib.Path(os.path.realpath(__file__))
    repo_root = this_path.parent.parent.parent

    warning = aas_core_3_0_rc2_typescript_testgen.common.generate_warning_comment(
        this_path.relative_to(repo_root)
    )

    blocks = [
        Stripped(
            """\
/**
 * Test JSON de/serialization of enumeration literals.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as AasJsonization from "../src/jsonization";
import * as AasTypes from "../src/types";"""
        )
    ]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.Enumeration):
            continue

        enum_name_typescript = typescript_naming.enum_name(our_type.name)

        assert len(our_type.literals) > 0, (
            f"Unexpected enumeration without literals: {our_type.name}"
        )

        literal = our_type.literals[0]
        literal_name_typescript = typescript_naming.enum_literal_name(literal.name)

        deserialization_function = typescript_naming.function_name(
            Identifier(f"{our_type.name}_from_jsonable")
        )

        blocks.append(
            Stripped(
                f"""\
test("{enum_name_typescript} round-trip OK", () => {{
{I}const jsonable = {typescript_common.string_literal(literal.value)};

{I}const literalOrError = AasJsonization.{deserialization_function}(
{II}jsonable
{I});

{I}expect(literalOrError.error).toBeNull();
{I}const literal = literalOrError.mustValue();

{I}expect(literal).toStrictEqual(
{II}AasTypes.{enum_name_typescript}.{literal_name_typescript}
{I});
}});"""
            )
        )

        literal_value_set = set(literal.value for literal in our_type.literals)
        invalid_literal_value = "invalid-literal"
        while invalid_literal_value in literal_value_set:
            invalid_literal_value = f"very-{invalid_literal_value}"

        expected_message = (
            f"Not a valid string representation of a literal "
            f"of {enum_name_typescript}: {invalid_literal_value}"
        )

        blocks.append(
            Stripped(
                f"""\
test("{enum_name_typescript} deserialization fail", () => {{
{I}const jsonable = {typescript_common.string_literal(invalid_literal_value)};

{I}const literalOrError = AasJsonization.{deserialization_function}(
{II}jsonable
{I});

{I}expect(literalOrError.error.message).toStrictEqual(
{II}{typescript_common.string_literal(expected_message)}
{I});
}});"""
            )
        )

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)

    writer.write('\n')

    target_pth = repo_root / "test/jsonization.enums.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
