"""Generate the test code for the ``as*`` and ``is*`` functions."""

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
 * Test `as*` and `is*` functions.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as AasTypes from "../src/types";
import * as TestCommonJsonization from "./commonJsonization";"""
        )
    ]  # type: List[Stripped]

    classes = [
        our_type
        for our_type in symbol_table.our_types
        if
        isinstance(our_type, (intermediate.ConcreteClass, intermediate.AbstractClass))
    ]

    for cls in classes:
        if not isinstance(cls, intermediate.ConcreteClass):
            continue

        cls_name_typescript = typescript_naming.class_name(cls.name)

        load_minimal_name = typescript_naming.function_name(
            Identifier(f"load_minimal_{cls.name}")
        )

        instance_var = typescript_naming.variable_name(
            Identifier(f"the_{cls.name}")
        )

        body_blocks = [
            Stripped(
                f"""\
const {instance_var} =
{I}TestCommonJsonization.{load_minimal_name}();"""
            )
        ]  # type: List[Stripped]

        for other_cls in classes:
            is_function_name = typescript_naming.function_name(
                Identifier(f"is_{other_cls.name}")
            )

            as_function_name = typescript_naming.function_name(
                Identifier(f"as_{other_cls.name}")
            )

            if cls.is_subclass_of(other_cls):
                body_blocks.append(
                    Stripped(
                        f"""\
expect(
{I}AasTypes.{is_function_name}({instance_var})
).toStrictEqual(true);
expect(
{I}AasTypes.{as_function_name}({instance_var})
).toStrictEqual({instance_var});"""
                    )
                )
            else:
                body_blocks.append(
                    Stripped(
                        f"""\
expect(
{I}AasTypes.{is_function_name}({instance_var})
).toStrictEqual(false);
expect(
{I}AasTypes.{as_function_name}({instance_var})
).toBeNull();"""
                    )
                )

        body = "\n\n".join(body_blocks)
        blocks.append(
            Stripped(
                f"""\
test("casts over an instance of {cls_name_typescript}", () => {{
{I}{indent_but_first_line(body, I)}
}});"""
            )
        )

    blocks.append(warning)

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)

    writer.write('\n')

    target_pth = repo_root / "test/types.casts.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
