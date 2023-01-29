"""Generate the test code for the ``types_match`` function."""

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
    INDENT as I, INDENT2 as II
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
 * Test `typesMatch`.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as AasTypes from "../src/types";
import * as TestCommonJsonization from "./commonJsonization";"""
        )
    ]  # type: List[Stripped]

    concrete_classes = [
        our_type
        for our_type in symbol_table.our_types
        if isinstance(our_type, intermediate.ConcreteClass)
    ]

    for cls in concrete_classes:
        if not isinstance(cls, intermediate.ConcreteClass):
            continue

        load_minimal_name = typescript_naming.function_name(
            Identifier(f"load_minimal_{cls.name}")
        )

        instance_var = typescript_naming.constant_name(
            Identifier(f"the_{cls.name}")
        )

        blocks.append(
            Stripped(
                f"""\
const {instance_var} = TestCommonJsonization.{load_minimal_name}();"""
            )
        )

    for cls in concrete_classes:
        body_blocks = []  # type: List[Stripped]

        that_var = typescript_naming.constant_name(
            Identifier(f"the_{cls.name}")
        )

        for other_cls in concrete_classes:
            other_var = typescript_naming.constant_name(
                Identifier(f"the_{other_cls.name}")
            )

            if other_cls.is_subclass_of(cls):
                body_blocks.append(
                    Stripped(
                        f"""\
expect(
{I}AasTypes.typesMatch(
{II}{that_var},
{II}{other_var}
{I})
).toStrictEqual(true);"""
                    )
                )
            else:
                body_blocks.append(
                    Stripped(
                        f"""\
expect(
{I}AasTypes.typesMatch(
{II}{that_var},
{II}{other_var}
{I})
).toStrictEqual(false);"""
                    )
                )

        body = "\n\n".join(body_blocks)

        cls_name_typescript = typescript_naming.class_name(cls.name)
        blocks.append(
            Stripped(
                f"""\
test("type matches for {cls_name_typescript}", () => {{
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

    target_pth = repo_root / "test/types.typeMatches.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
