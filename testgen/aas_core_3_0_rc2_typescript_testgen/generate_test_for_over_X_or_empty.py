"""Generate the test code for the ``OverXOrEmpty`` methods."""

import io
import os
import pathlib
import sys

from aas_core_codegen import intermediate
from aas_core_codegen.common import (
    Stripped,
    Identifier
)
from aas_core_codegen.typescript import (
    naming as typescript_naming
)
from aas_core_codegen.typescript.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III
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
 * Test `over*OrEmpty` methods.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as TestCommonJsonization from "./commonJsonization";"""
        )
    ]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.ConcreteClass):
            continue

        cls_name_typescript = typescript_naming.class_name(our_type.name)

        for prop in our_type.properties:
            if (
                    isinstance(
                        prop.type_annotation, intermediate.OptionalTypeAnnotation)
                    and isinstance(
                prop.type_annotation.value, intermediate.ListTypeAnnotation)
            ):
                method_name_typescript = typescript_naming.method_name(
                    Identifier(f"Over_{prop.name}_or_empty"))

                load_minimal_name = typescript_naming.function_name(
                    Identifier(f"load_minimal_{our_type.name}")
                )

                blocks.append(
                    Stripped(
                        f"""\
test("{cls_name_typescript}.{method_name_typescript} empty on default", () => {{
{I}const instance = TestCommonJsonization.{load_minimal_name}();

{I}let count = 0;
{I}for (const _ of instance.{method_name_typescript}()) {{
{II}count++;
{I}}}

{I}expect(count).toStrictEqual(0);
}});"""
                    )
                )

                load_complete_name = typescript_naming.function_name(
                    Identifier(f"load_complete_{our_type.name}")
                )

                blocks.append(
                    Stripped(
                        f"""\
test("{cls_name_typescript}.{method_name_typescript} non-default", () => {{
{I}const instance = TestCommonJsonization.{load_complete_name}();

{I}let count = 0;
{I}for (const _ of instance.{method_name_typescript}()) {{
{II}count++;
{I}}}

{I}expect(count).toBeGreaterThan(0);
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

    target_pth = repo_root / "test/types.overXOrEmpty.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
