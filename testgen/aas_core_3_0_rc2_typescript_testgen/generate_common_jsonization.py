"""Generate the common functions to de/serialize instances of a class."""

import io
import os
import pathlib
import sys
from typing import List

import aas_core_codegen
import aas_core_codegen.common
import aas_core_codegen.naming
import aas_core_codegen.parse
import aas_core_codegen.run
from aas_core_codegen import intermediate
from aas_core_codegen.common import (
    Stripped,
    Identifier,
    indent_but_first_line
)
from aas_core_codegen.typescript import (
    common as typescript_common,
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

    # noinspection PyListCreation
    blocks = [
        Stripped(
            """\
/**
 * Provide functions for loading generated examples of AAS instances.
 */"""
        ),
        warning,
        Stripped(
            f"""\
import * as path from 'path';

import * as AasTypes from "../src/types";
import * as AasJsonization from "../src/jsonization";

import * as TestCommon from "./common";"""
        )
    ]  # type: List[Stripped]

    environment_cls = symbol_table.must_find_concrete_class(Identifier("Environment"))

    test_data_dir = repo_root / "test_data"

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

        cls_name_typescript = typescript_naming.class_name(our_type.name)
        cls_name_json = aas_core_codegen.naming.json_model_type(our_type.name)

        # NOTE (mristin, 2022-12-07):
        # The class is self-contained if the container class is equal to our type.
        if container_cls is our_type:
            deserialization_function = typescript_naming.function_name(
                Identifier(f"{our_type.name}_from_jsonable")
            )

            deserialization_snippet = Stripped(
                f"""\
const instanceOrError = AasJsonization.{deserialization_function}(
{I}jsonable
);
expect(instanceOrError.error).toBeNull();
const instance = instanceOrError.mustValue();"""
            )
            container_kind_directory = "SelfContained"
        else:
            deserialization_function = typescript_naming.function_name(
                Identifier(f"{container_cls.name}_from_jsonable")
            )

            is_function = typescript_naming.function_name(
                Identifier(f"is_{our_type.name}")
            )

            deserialization_snippet = Stripped(
                f"""\
const containerOrError = AasJsonization.{deserialization_function}(
{I}jsonable
);
expect(containerOrError.error).toBeNull();
const container = containerOrError.mustValue();
const instance = TestCommon.mustFind(
{I}container,
{I}AasTypes.{is_function}
);"""
                )
            assert container_cls.name == "Environment", (
                "Necessary for the container kind directory")
            container_kind_directory = "ContainedInEnvironment"

        load_complete_name = typescript_naming.function_name(
            Identifier(f"load_complete_{our_type.name}")
        )

        load_minimal_name = typescript_naming.function_name(
            Identifier(f"load_minimal_{our_type.name}")
        )

        as_function = typescript_naming.function_name(
            Identifier(f"as_{our_type.name}")
        )

        blocks.append(
            Stripped(
                f"""\
/**
 * Load a complete example of {{@link types.{cls_name_typescript}}} from
 * the test data directory.
 */
export function {load_complete_name}(
): AasTypes.{cls_name_typescript} {{
{I}const aPath = path.join(
{II}TestCommon.TEST_DATA_DIR,
{II}"Json",
{II}{typescript_common.string_literal(container_kind_directory)},
{II}"Expected",
{II}{typescript_common.string_literal(cls_name_json)},
{II}"complete.json"
{I});

{I}const jsonable = TestCommon.readJsonFromFileSync(aPath);

{I}{indent_but_first_line(deserialization_snippet, I)}

{I}const casted = AasTypes.{as_function}(instance);
{I}if (casted === null) {{
{II}throw new Error(
{III}`Expected instance of {cls_name_typescript} in ${{aPath}}, ` +
{III}`but got: ${{typeof instance}}`
{II});
{I}}}
{I}return casted;
}}"""
            )
        )

        blocks.append(
            Stripped(
                    f"""\
/**
 * Load a minimal example of {{@link types.{cls_name_typescript}}} from
 * the test data directory.
 */
export function {load_minimal_name}(
): AasTypes.{cls_name_typescript} {{
{I}const aPath = path.join(
{II}TestCommon.TEST_DATA_DIR,
{II}"Json",
{II}{typescript_common.string_literal(container_kind_directory)},
{II}"Expected",
{II}{typescript_common.string_literal(cls_name_json)},
{II}"minimal.json"
{I});

{I}const jsonable = TestCommon.readJsonFromFileSync(aPath);

{I}{indent_but_first_line(deserialization_snippet, I)}

{I}const casted = AasTypes.{as_function}(instance);
{I}if (casted === null) {{
{II}throw new Error(
{III}`Expected instance of {cls_name_typescript} in ${{aPath}}, ` +
{III}`but got: ${{typeof instance}}`
{II});
{I}}}
{I}return casted;
}}"""
            )
        )

    blocks.append(warning)

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)
    
    writer.write("\n")

    target_pth = repo_root / "test/commonJsonization.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
