"""Generate the test code for the jsonization of classes outside a container."""

import io
import os
import pathlib
import sys

import aas_core_codegen
import aas_core_codegen.common
import aas_core_codegen.naming
import aas_core_codegen.parse
import aas_core_codegen.run
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

    test_data_dir = repo_root / "test_data"

    warning = aas_core_3_0_rc2_typescript_testgen.common.generate_warning_comment(
        this_path.relative_to(repo_root)
    )

    blocks = [
        Stripped(
            """\
/**
 * Test JSON de/serialization of concrete classes outside a container.
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

    environment_cls = symbol_table.must_find_concrete_class(
        aas_core_codegen.common.Identifier("Environment"))

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.ConcreteClass):
            continue

        # fmt: off
        container_cls = (
            aas_core_3_0_rc2_typescript_testgen.common.determine_container_class(
                cls=our_type,
                test_data_dir=test_data_dir,
                environment_cls=environment_cls
            )
        )
        # fmt: on

        if container_cls is our_type:
            # NOTE (mristin, 2022-12-10):
            # These classes are tested already in jsonization.concreteClasses.spec.ts.
            # We only need to test for class instances contained in a container.
            continue

        cls_name_typescript = typescript_naming.class_name(our_type.name)

        load_complete_name = typescript_naming.function_name(
            Identifier(f"load_complete_{our_type.name}")
        )

        deserialization_function = typescript_naming.function_name(
            Identifier(f"{our_type.name}_from_jsonable")
        )

        blocks.append(
            Stripped(
                f"""\
test("{cls_name_typescript} round-trip OK", () => {{
{I}const instance = TestCommonJsonization.{load_complete_name}();

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
{III}"The complete example of {cls_name_typescript} serialized " +
{III}"to JSON, then de-serialized and serialized again does not match " +
{III}`the first JSON: ${{inequalityError.path}}: ${{inequalityError.message}}`
{II});
{I}}}
}});"""
            )
        )

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)

    writer.write('\n')

    target_pth = repo_root / "test/jsonization.concreteClassesOutsideContainer.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
