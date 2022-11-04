"""Generate the test code for the ``xOrDefault`` methods."""

import io
import os
import pathlib
import sys
from typing import List, Optional

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
    INDENT3 as III,
    INDENT4 as IIII
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
 * Test `*OrDefault` functions.
 */"""
        ),
        warning,
        Stripped(
            """\
import * as path from "path";
import * as fs from "fs";

import * as AasStringification from "../src/stringification";
import * as AasTypes from "../src/types";
import * as TestCommon from "./common";
import * as TestCommonJsonization from "./commonJsonization";"""
        ),
        Stripped(
            f"""\
/**
 * Represent explicitly a literal of an enumeration.
 */
class EnumerationLiteral {{
{I}constructor(public enumerationName: string, public literalName) {{
{II}// Intentionally empty.
{I}}}

{I}toString(): string {{
{II}return `${{this.enumerationName}}.${{this.literalName}}`;
{I}}}
}}"""
        ),
        Stripped(
            f"""\
/**
 * Represent a value such that we can immediately check whether it is the default value
 * or the set one.
 *
 * @remark
 * We compare it against the recorded golden file, if not {{@link common.RECORD_MODE}}.
 * Otherwise, when {{@link common.RECORD_MODE}} is set, we re-record the golden file. 
 *
 * @param value - to be represented
 * @param expectedPath - to the golden file
 */
function compareOrRecordValue(
{I}value: boolean | number | string | null | EnumerationLiteral | AasTypes.Class,
{I}expectedPath: string
): void {{
{I}let got = "";
{I}if (
{II}typeof value === "boolean"
{II}|| typeof value === "number"
{II}|| typeof value === "string"
{II}|| value === null
{I}) {{
{II}got = JSON.stringify(value);
{I}}} else if (value instanceof EnumerationLiteral) {{
{II}got = value.toString();
{I}}} else if (value instanceof AasTypes.Class) {{
{II}got = TestCommon.traceMark(value)
{I}}} else {{
{II}throw new Error(`We do not know how to represent the value ${{value}}`);
{I}}}

{I}// NOTE (mristin, 2022-12-09):
{I}// We add a new line for POSIX systems which prefer a new line
{I}// at the end of the file.
{I}got += "\\n";

{I}if (TestCommon.RECORD_MODE) {{
{II}const parent = path.dirname(expectedPath);
{II}if (!fs.existsSync(parent)) {{
{III}fs.mkdirSync(parent, {{recursive: true}});
{II}}}
{II}fs.writeFileSync(expectedPath, got, "utf-8");
{I}}} else {{
{II}if (!fs.existsSync(expectedPath)) {{
{III}throw new Error(
{IIII}`The file with the recorded value does not exist: ${{expectedPath}}`
{III});
{II}}}

{II}const expected =
{III}fs.readFileSync(expectedPath, "utf-8")
{III}.replace(/\\r\\n/g, "\\n");
{II}expect(got).toStrictEqual(expected);
{I}}}
}}"""
        )
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.ConcreteClass):
            continue

        cls_name_typescript = typescript_naming.class_name(our_type.name)
        cls_name_json = aas_core_codegen.naming.json_model_type(our_type.name)

        x_or_default_methods = []  # type: List[intermediate.Method]
        for method in our_type.methods:
            if method.name.endswith("_or_default"):
                x_or_default_methods.append(method)

        for method in x_or_default_methods:
            method_name_typescript = typescript_naming.method_name(method.name)

            result_enum = None  # type: Optional[intermediate.Enumeration]
            assert method.returns is not None, (
                f"Expected all X_or_default to return something, "
                f"but got None for {our_type}.{method.name}"
            )

            if (
                    isinstance(method.returns, intermediate.OurTypeAnnotation)
                    and isinstance(method.returns.our_type, intermediate.Enumeration)
            ):
                result_enum = method.returns.our_type

            if result_enum is None:
                value_assignment_snippet = Stripped(
                    f"const value = instance.{method_name_typescript}();")
            else:
                enum_to_string_name = typescript_naming.function_name(
                    Identifier(f"must_{result_enum.name}_to_string")
                )

                value_assignment_snippet = Stripped(
                    f"""\
const value = new EnumerationLiteral(
{I}{typescript_common.string_literal(typescript_naming.enum_name(result_enum.name))},
{I}AasStringification.{enum_to_string_name}(
{II}instance.{method_name_typescript}()
{I})
);"""
                )

            load_complete_name = typescript_naming.function_name(
                Identifier(f"load_complete_{our_type.name}")
            )

            # noinspection SpellCheckingInspection
            blocks.append(
                Stripped(
                    f"""\
test("{cls_name_typescript}.{method_name_typescript} with non-default", () => {{
{I}const instance = TestCommonJsonization.{load_complete_name}();

{I}{indent_but_first_line(value_assignment_snippet, I)}

{I}compareOrRecordValue(
{II}value,
{II}path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"xOrDefault",
{III}{typescript_common.string_literal(cls_name_json)},
{III}"{method_name_typescript}.non-default.json"
{II})
{I});
}});"""
                )
            )

            load_minimal_name = typescript_naming.function_name(
                Identifier(f"load_minimal_{our_type.name}")
            )

            blocks.append(
                Stripped(
                    f"""\
test("{cls_name_typescript}.{method_name_typescript} with default", () => {{
{I}const instance = TestCommonJsonization.{load_minimal_name}();

{I}{indent_but_first_line(value_assignment_snippet, I)}

{I}compareOrRecordValue(
{II}value,
{II}path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"xOrDefault",
{III}{typescript_common.string_literal(cls_name_json)},
{III}"{method_name_typescript}.default.json"
{II})
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

    target_pth = repo_root / "test/types.xOrDefault.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
