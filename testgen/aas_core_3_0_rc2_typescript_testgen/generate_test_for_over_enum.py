"""Generate the test code for the ``XOrDefault`` methods."""

import io
import os
import pathlib
import sys
from typing import List

from aas_core_codegen import intermediate
from aas_core_codegen.common import (
    Stripped,
    Identifier,
    indent_but_first_line
)
from aas_core_codegen.typescript import (
    naming as typescript_naming
)
from aas_core_codegen.typescript.common import (
    INDENT as I
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
 * Test `over{Enum}` functions.
 */"""
        ),
        warning,
        Stripped('import * as AasTypes from "../src/types";'),
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.Enumeration):
            continue

        name = typescript_naming.enum_name(our_type.name)

        body_writer = io.StringIO()
        body_writer.write(
            f"""\
const expected: Array<AasTypes.{name}> = [
"""
        )
        for i, literal in enumerate(our_type.literals):
            literal_name = typescript_naming.enum_literal_name(literal.name)
            body_writer.write(f"{I}AasTypes.{name}.{literal_name}")

            if i < len(our_type.literals) - 1:
                body_writer.write(",")

            body_writer.write("\n")

        body_writer.write("];\n\n")

        over_enum_name = typescript_naming.function_name(
            Identifier(f"over_{our_type.name}")
        )

        body_writer.write(
            f"""\
const got = new Array<AasTypes.{name}>();
for (const literal of AasTypes.{over_enum_name}()) {{
{I}got.push(literal);
}}

expect(got).toStrictEqual(expected);"""
        )

        blocks.append(
            Stripped(
                f"""\
test("over {name}", () => {{
{I}{indent_but_first_line(body_writer.getvalue(), I)}
}});"""
            )
        )

    blocks.append(warning)

    writer = io.StringIO()

    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)

    writer.write("\n")

    target_pth = repo_root / "test/types.overEnum.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
