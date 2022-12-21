"""Generate the test code for the JSON de/serialization of classes."""

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
    Identifier
)
from aas_core_codegen.typescript import (
    common as typescript_common,
    naming as typescript_naming
)
from aas_core_codegen.typescript.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
    INDENT4 as IIII,
    INDENT5 as IIIII
)

import aas_core_3_0_rc2_typescript_testgen.common


def _generate_for_self_contained(
        cls: intermediate.ConcreteClass
) -> List[Stripped]:
    """Generate the tests for a self-contained class."""
    cls_name_typescript = typescript_naming.class_name(cls.name)
    cls_name_json = aas_core_codegen.naming.json_model_type(cls.name)

    deserialization_function = typescript_naming.function_name(
        Identifier(f"{cls.name}_from_jsonable")
    )

    return [
        Stripped(
            f"""\
test("{cls_name_typescript} round-trip OK", () => {{
{I}const pths = Array.from(
{II}TestCommon.findFilesBySuffixRecursively(
{III}path.join(
{IIII}TestCommon.TEST_DATA_DIR,
{IIII}"Json",
{IIII}"SelfContained",
{IIII}"Expected",
{IIII}{typescript_common.string_literal(cls_name_json)}
{III}),
{III}".json"
{II})
{I});
{I}pths.sort();

{I}for (const pth of pths) {{
{II}const jsonable = TestCommon.readJsonFromFileSync(pth);

{II}const instanceOrError = AasJsonization.{deserialization_function}(
{III}jsonable
{II});
{II}expect(instanceOrError.error).toBeNull();
{II}const instance = instanceOrError.mustValue();

{II}TestCommon.assertNoVerificationErrors(AasVerification.verify(instance), pth);

{II}assertSerializeDeserializeEqualsOriginal(
{III}jsonable,
{III}instance,
{III}pth
{II});
{I}}}
}});"""
        ),
        Stripped(
            f"""\
test("{cls_name_typescript} deserialization fail", () => {{
{I}for (const cause of CAUSES_FOR_DESERIALIZATION_FAILURE) {{
{II}const baseDir = path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"Json",
{III}"SelfContained",
{III}"Unexpected",
{III}cause,
{III}{typescript_common.string_literal(cls_name_json)}
{II});

{II}if (!fs.existsSync(baseDir)) {{
{III}// No examples of {cls_name_typescript} exist for the failure cause.
{III}continue;
{II}}}

{II}const pths = Array.from(
{III}TestCommon.findFilesBySuffixRecursively(
{IIII}baseDir,
{IIII}".json"
{III})
{II});
{II}pths.sort();

{II}for (const pth of pths) {{
{III}const jsonable = TestCommon.readJsonFromFileSync(pth);

{III}const instanceOrError = AasJsonization.{deserialization_function}(
{IIII}jsonable
{III});
{III}if (instanceOrError.error === null) {{
{IIII}throw new Error(`Expected a de-serialization error for ${{pth}}, but got none`);
{III}}}

{III}assertDeserializationErrorEqualsExpectedOrRecord(
{IIII}instanceOrError.error,
{IIII}pth
{III});
{II}}}
{I}}}
}});"""
        ),
        Stripped(
            f"""\
test("{cls_name_typescript} verification fail", () => {{
{I}for (const cause of TestCommon.CAUSES_FOR_VERIFICATION_FAILURE) {{
{II}const baseDir = path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"Json",
{III}"SelfContained",
{III}"Unexpected",
{III}cause,
{III}{typescript_common.string_literal(cls_name_json)}
{II});

{II}if (!fs.existsSync(baseDir)) {{
{III}// No examples of {cls_name_typescript} exist for the failure cause.
{III}continue;
{II}}}

{II}const pths = Array.from(
{III}TestCommon.findFilesBySuffixRecursively(
{IIII}baseDir,
{IIII}".json"
{III})
{II});
{II}pths.sort();

{II}for (const pth of pths) {{
{III}const jsonable = TestCommon.readJsonFromFileSync(pth);

{III}const instanceOrError = AasJsonization.{deserialization_function}(
{IIII}jsonable
{III});
{III}if (instanceOrError.error !== null) {{
{IIII}throw new Error(
{IIIII}`Expected no de-serialization error for ${{pth}}, ` +
{IIIII}`but got: ${{instanceOrError.error.message}}: ${{instanceOrError.error.path}}`
{IIII});
{III}}}

{III}const instance = instanceOrError.mustValue();

{III}const verificationErrors = Array.from(AasVerification.verify(instance));
{III}assertVerificationErrorsEqualExpectedOrRecord(
{IIII}verificationErrors,
{IIII}pth
{III});
{II}}}
{I}}}
}});"""
        )
    ]  # type: List[Stripped]


def _generate_for_contained_in_container(
        container_cls: intermediate.ConcreteClass,
        cls: intermediate.ConcreteClass
) -> List[Stripped]:
    """Generate the tests for a class contained in a container."""
    cls_name_typescript = typescript_naming.class_name(cls.name)
    cls_name_json = aas_core_codegen.naming.json_model_type(cls.name)

    deserialization_function = typescript_naming.function_name(
        Identifier(f"{container_cls.name}_from_jsonable")
    )

    container_cls_json = aas_core_codegen.naming.json_model_type(container_cls.name)

    return [
        Stripped(
            f"""\
test("{cls_name_typescript} round-trip OK", () => {{
{I}const pths = Array.from(
{II}TestCommon.findFilesBySuffixRecursively(
{III}path.join(
{IIII}TestCommon.TEST_DATA_DIR,
{IIII}"Json",
{IIII}"ContainedIn{container_cls_json}",
{IIII}"Expected",
{IIII}{typescript_common.string_literal(cls_name_json)}
{III}),
{III}".json"
{II})
{I});
{I}pths.sort();

{I}for (const pth of pths) {{
{II}const jsonable = TestCommon.readJsonFromFileSync(pth);

{II}const containerOrError = AasJsonization.{deserialization_function}(
{III}jsonable
{II});
{II}if (containerOrError.error !== null) {{
{III}throw new Error(
{IIII}`Expected no de-serialization error for ${{pth}}, ` +
{IIII}`but got: ${{containerOrError.error.message}}: ${{containerOrError.error.path}}`
{III});
{II}}}

{II}const container = containerOrError.mustValue();
{II}TestCommon.assertNoVerificationErrors(AasVerification.verify(container), pth);

{II}assertSerializeDeserializeEqualsOriginal(
{III}jsonable,
{III}container,
{III}pth
{II});
{I}}}
}});"""
        ),
        Stripped(
            f"""\
test("{cls_name_typescript} deserialization fail", () => {{
{I}for (const cause of CAUSES_FOR_DESERIALIZATION_FAILURE) {{
{II}const baseDir = path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"Json",
{III}"ContainedIn{container_cls_json}",
{III}"Unexpected",
{III}cause,
{III}{typescript_common.string_literal(cls_name_json)}
{II});

{II}if (!fs.existsSync(baseDir)) {{
{III}// No examples of {cls_name_typescript} exist for the failure cause.
{III}continue;
{II}}}

{II}const pths = Array.from(
{III}TestCommon.findFilesBySuffixRecursively(
{IIII}baseDir,
{IIII}".json"
{III})
{II});
{II}pths.sort();

{II}for (const pth of pths) {{
{III}const jsonable = TestCommon.readJsonFromFileSync(pth);

{III}const containerOrError = AasJsonization.{deserialization_function}(
{IIII}jsonable
{III});
{III}if (containerOrError.error === null) {{
{IIII}throw new Error(
{IIIII}`Expected a de-serialization error for ${{pth}}, but got none`
{IIII});
{III}}}

{III}assertDeserializationErrorEqualsExpectedOrRecord(
{IIII}containerOrError.error,
{IIII}pth
{III});
{II}}}
{I}}}
}});"""
        ),
        Stripped(
            f"""\
test("{cls_name_typescript} verification fail", () => {{
{I}for (const cause of TestCommon.CAUSES_FOR_VERIFICATION_FAILURE) {{
{II}const baseDir = path.join(
{III}TestCommon.TEST_DATA_DIR,
{III}"Json",
{III}"ContainedIn{container_cls_json}",
{III}"Unexpected",
{III}cause,
{III}{typescript_common.string_literal(cls_name_json)}
{II});

{II}if (!fs.existsSync(baseDir)) {{
{III}// No examples of {cls_name_typescript} exist for the failure cause.
{III}continue;
{II}}}

{II}const pths = Array.from(
{III}TestCommon.findFilesBySuffixRecursively(
{IIII}baseDir,
{IIII}".json"
{III})
{II});
{II}pths.sort();

{II}for (const pth of pths) {{
{III}const jsonable = TestCommon.readJsonFromFileSync(pth);

{III}const containerOrError = AasJsonization.{deserialization_function}(
{IIII}jsonable
{III});
{III}if (containerOrError.error !== null) {{
{IIII}throw new Error(
{IIIII}`Expected no de-serialization error for ${{pth}}, ` +
{IIIII}`but got: ${{containerOrError.error.message}}: ${{containerOrError.error.path}}`
{IIII});
{III}}}

{III}const container = containerOrError.mustValue();

{III}const verificationErrors = Array.from(AasVerification.verify(container));
{III}assertVerificationErrorsEqualExpectedOrRecord(
{IIII}verificationErrors,
{IIII}pth
{III});
{II}}}
{I}}}
}});"""
        )
    ]  # type: List[Stripped]


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
 * Test JSON de/serialization of concrete classes which are either self-container
 * or contained in an {{@link types.Environment}}.
 */"""
        ),
        warning,
        Stripped(
            f"""\
import * as fs from 'fs';
import * as path from 'path';

import * as AasJsonization from "../src/jsonization";
import * as AasTypes from "../src/types";
import * as AasVerification from "../src/verification";

import * as TestCommon from "./common";"""
        ),
        Stripped(
            f"""\
/**
 * Assert that the result of the chain JSON 🠒 de-serialize 🠒 object 🠒 serialize 🠒 JSON
 * gives the input.
 */
function assertSerializeDeserializeEqualsOriginal(
{I}originalJsonable: AasJsonization.JsonValue,
{I}instance: AasTypes.Class,
{I}aPath: string
): void {{
{I}let jsonable: AasJsonization.JsonValue | null = null;
{I}try {{
{II}jsonable = AasJsonization.toJsonable(instance);
{I}}} catch (error) {{
{II}throw new Error(
{III}"Expected no exception during JSON serialization " +
{III}`of an instance of ${{instance.constructor.name}} from ${{aPath}}, ` +
{III}`but got: ${{error}}`
{II});
{I}}}

{I}const inequalityError = TestCommon.checkJsonablesEqual(
{II}originalJsonable,
{II}jsonable
{I});
{I}if (inequalityError !== null) {{
{II}throw new Error(
{III}`The original JSON from ${{aPath}} is unequal the serialized JSON: ` +
{III}`${{inequalityError.path}}: ${{inequalityError.message}}`
{II});
{I}}}
}}"""
        ),
        Stripped(
            f"""\
const CAUSES_FOR_DESERIALIZATION_FAILURE = [
{I}"TypeViolation",
{I}"RequiredViolation",
{I}"EnumViolation",
{I}"NullViolation",
{I}// NOTE (mristin, 2022-12-09):
{I}// Unlike other SDKs, we can not be really sure what additional properties
{I}// JavaScript might bring about. Therefore, we leave out the tests with
{I}// the validation of additional properties.
{I}// "UnexpectedAdditionalProperty"
];"""
        ),
        Stripped(
            f"""\
/**
 * Assert that the deserialization error equals the expected golden one,
 * or, if {{@link common.RECORD_MODE}} set, re-record the expected error.
 *
 * @param error - obtained error during the de-serialization
 * @param aPath - to the JSON file which caused the de-serialization error
 * @throws an {{@link Error}} if assertion fails
 */
function assertDeserializationErrorEqualsExpectedOrRecord(
{I}error: AasJsonization.DeserializationError,
{I}aPath: string
): void {{
{I}const errorPath = aPath + ".error";
{I}const got = `${{error.path}}: ${{error.message}}\\n`;

{I}if (TestCommon.RECORD_MODE) {{
{II}fs.writeFileSync(errorPath, got, "utf-8");
{I}}} else {{
{II}if (!fs.existsSync(errorPath)) {{
{III}throw new Error(
{IIII}`The file with the recorded error does not exist: ${{errorPath}}`
{III});
{II}}}

{II}const expected =
{III}fs.readFileSync(errorPath, "utf-8")
{III}.replace(/\\r\\n/g, "\\n");
{II}if (expected !== got) {{
{III}throw new Error(
{IIII}`Expected the error:\\n${{JSON.stringify(expected)}}\\n, ` +
{IIII}`but got:\\n${{JSON.stringify(got)}}\\n` +
{IIII}`when de-serializing from ${{aPath}}`
{III});
{II}}}
{I}}}
}}"""
        ),
        Stripped(
            f"""\
/**
 * Assert that the obtained verification errors equal the expected verification errors, 
 * or, if {{@link common.RECORD_MODE}} set, re-record the expected errors.
 *
 * @param errors - obtained verification errors
 * @param aPath - to the JSON file which caused the verification errors
 * @throws an {{@link Error}} if assertion fails
 */
function assertVerificationErrorsEqualExpectedOrRecord(
{I}errors: Array<AasVerification.VerificationError>,
{I}aPath: string
): void {{
{I}const errorsPath = aPath + ".errors";

{I}const lines = new Array<string>();
{I}for (const error of errors) {{
{II}lines.push(`${{error.path}}: ${{error.message}}`);
{I}}}
{I}// NOTE (mristin, 2022-12-09):
{I}// We add a new line for POSIX systems which prefer a new line
{I}// at the end of the file.
{I}lines.push("");
{I}const got = lines.join("\\n");

{I}if (TestCommon.RECORD_MODE) {{
{II}fs.writeFileSync(errorsPath, got, "utf-8");
{I}}} else {{
{II}if (!fs.existsSync(errorsPath)) {{
{III}throw new Error(
{IIII}`The file with the recorded errors does not exist: ${{errorsPath}}`
{III});
{II}}}

{II}const expected =
{III}fs.readFileSync(errorsPath, "utf-8")
{III}.replace(/\\r\\n/g, "\\n");
{II}if (expected !== got) {{
{III}throw new Error(
{IIII}`Expected the error(s):\\n${{JSON.stringify(expected)}}\\n, ` +
{IIII}`but got:\\n${{JSON.stringify(got)}}\\n` +
{IIII}`when verifying ${{aPath}}`
{III});
{II}}}
{I}}}
}}"""
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

        if container_cls is our_type:
            blocks.extend(
                _generate_for_self_contained(
                    cls=our_type
                )
            )
        else:
            blocks.extend(
                _generate_for_contained_in_container(
                    container_cls=container_cls,
                    cls=our_type
                )
            )

    blocks.append(warning)

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(block)

    writer.write("\n")

    target_pth = repo_root / "test/jsonization.concreteClasses.spec.ts"
    target_pth.write_text(writer.getvalue(), encoding='utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())
