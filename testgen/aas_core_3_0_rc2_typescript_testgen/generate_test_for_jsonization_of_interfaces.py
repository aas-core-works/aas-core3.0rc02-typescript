"""Generate the test code for the JSON de/serialization of interfaces."""

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
 * Test JSON de/serialization of interfaces.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as AasJsonization from "../src/jsonization";
import * as TestCommon from "./common";
import * as TestCommonJsonization from "./commonJsonization";"""
        )
    ]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.Class):
            continue

        if our_type.interface is None or len(our_type.interface.implementers) == 0:
            continue

        interface_name_typescript = typescript_naming.interface_name(our_type.name)

        deserialization_function = typescript_naming.function_name(
            Identifier(f"{our_type.name}_from_jsonable")
        )

        for cls in our_type.interface.implementers:
            if cls.serialization is None or not cls.serialization.with_model_type:
                continue

            cls_name_typescript = typescript_naming.class_name(cls.name)

            load_minimal_name = typescript_naming.function_name(
                Identifier(f"load_minimal_{cls.name}")
            )

            blocks.append(
                Stripped(
                    f"""\
test(
{I}"{interface_name_typescript} round-trip " +
{I}"starting from {cls_name_typescript} OK",
{I}() => {{
{I}const instance = TestCommonJsonization.{load_minimal_name}();

{I}const jsonable = AasJsonization.toJsonable(instance);

{I}const anotherInstanceOrError = AasJsonization.{deserialization_function}(
{II}jsonable
{I});
{I}expect(anotherInstanceOrError.error).toBeNull();
{I}const anotherInstance = anotherInstanceOrError.mustValue();

{I}const anotherJsonable = AasJsonization.toJsonable(anotherInstance);

{I}const inequalityError = TestCommon.checkJsonablesEqual(
{II}jsonable,
{II}anotherJsonable
{I});
{I}if (inequalityError !== null) {{
{II}throw new Error(
{III}"The minimal example of {interface_name_typescript} " +
{III}"as an instance of {cls_name_typescript} serialized " +
{III}"to JSON, then de-serialized and serialized again does not match " +
{III}`the first JSON: ${{inequalityError.path}}: ${{inequalityError.message}}`
{II});
{I}}}
}});"""
                )
            )

        blocks.append(
            Stripped(
                f"""\
test("{interface_name_typescript} deserialization fail", () => {{
{I}const jsonable = "This is not a {interface_name_typescript}.";

{I}const instanceOrError = AasJsonization.{deserialization_function}(
{II}jsonable
{I});
{I}expect(instanceOrError.error.message).toStrictEqual(
{II}"Expected a JSON object, but got: string"
{I});
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

    target_pth = repo_root / "test/jsonization.interfaces.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
