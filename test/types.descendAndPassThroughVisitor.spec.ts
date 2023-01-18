/**
 * Test `descend*` functions and `PassThroughVisitor`.
 */

// This code has been automatically generated by:
// testgen/aas_core_3_0_rc2_typescript_testgen/generate_test_for_descend_and_pass_through_visitor.py
// Do NOT edit or append.

import * as path from "path";
import * as fs from "fs";

import * as AasTypes from "../src/types";
import * as TestCommon from "./common";
import * as TestCommonJsonization from "./commonJsonization";

/**
 * Record a human-readable trace of a descent over an object tree.
 */
class TracingVisitor extends AasTypes.PassThroughVisitor {
  readonly log = new Array<string>();

  visit(that: AasTypes.Class) {
    this.log.push(TestCommon.traceMark(that));
    super.visit(that);
  }
}

/**
 * Expect that the trace from {@link types.Class.descend} and
 * {@link TracingVisitor} are equal.
 *
 * @param instance - to be descended through
 * @throws an {@link Error} if the two traces are not equal
 */
function expectDescendAndPassThroughVisitorSame(instance: AasTypes.Class): void {
  const traceFromDescend = new Array<string>();
  for (const subInstance of instance.descend()) {
    traceFromDescend.push(TestCommon.traceMark(subInstance));
  }

  const visitor = new TracingVisitor();
  visitor.visit(instance);
  const traceFromVisitor = visitor.log;

  expect(traceFromVisitor.length).toBeGreaterThan(0);
  expect(TestCommon.traceMark(instance)).toStrictEqual(traceFromVisitor[0]);

  traceFromVisitor.shift();

  expect(traceFromVisitor).toStrictEqual(traceFromDescend);
}

/**
 * Compare the trace against the golden one from the test data,
 * or re-record the trace if {@link common.RECORD_MODE}.
 *
 * @param instance - to be traced
 * @param expectedPath - path to the golden trace
 */
function compareOrRecordTrace(instance: AasTypes.Class, expectedPath: string) {
  const lines = new Array<string>();
  for (const descendant of instance.descend()) {
    lines.push(TestCommon.traceMark(descendant));
  }
  // NOTE (mristin, 2022-12-09):
  // We add a new line for POSIX systems which prefer a new line
  // at the end of the file.
  lines.push("");
  const got = lines.join("\n");

  if (TestCommon.RECORD_MODE) {
    const parent = path.dirname(expectedPath);
    if (!fs.existsSync(parent)) {
      fs.mkdirSync(parent, { recursive: true });
    }
    fs.writeFileSync(expectedPath, got, "utf-8");
  } else {
    if (!fs.existsSync(expectedPath)) {
      throw new Error(
        `The file with the recorded trace does not exist: ${expectedPath}`
      );
    }

    const expected = fs.readFileSync(expectedPath, "utf-8").replace(/\r\n/g, "\n");
    expect(got).toStrictEqual(expected);
  }
}

test("descend of Extension", () => {
  const instance = TestCommonJsonization.loadCompleteExtension();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Extension", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteExtension();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of AdministrativeInformation", () => {
  const instance = TestCommonJsonization.loadCompleteAdministrativeInformation();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "AdministrativeInformation",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteAdministrativeInformation();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Qualifier", () => {
  const instance = TestCommonJsonization.loadCompleteQualifier();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Qualifier", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteQualifier();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of AssetAdministrationShell", () => {
  const instance = TestCommonJsonization.loadCompleteAssetAdministrationShell();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "AssetAdministrationShell",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteAssetAdministrationShell();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of AssetInformation", () => {
  const instance = TestCommonJsonization.loadCompleteAssetInformation();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "AssetInformation",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteAssetInformation();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Resource", () => {
  const instance = TestCommonJsonization.loadCompleteResource();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Resource", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteResource();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of SpecificAssetId", () => {
  const instance = TestCommonJsonization.loadCompleteSpecificAssetId();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "SpecificAssetId",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteSpecificAssetId();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Submodel", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodel();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Submodel", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodel();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of RelationshipElement", () => {
  const instance = TestCommonJsonization.loadCompleteRelationshipElement();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "RelationshipElement",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteRelationshipElement();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of SubmodelElementList", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodelElementList();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "SubmodelElementList",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodelElementList();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of SubmodelElementCollection", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodelElementCollection();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "SubmodelElementCollection",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteSubmodelElementCollection();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Property", () => {
  const instance = TestCommonJsonization.loadCompleteProperty();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Property", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteProperty();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of MultiLanguageProperty", () => {
  const instance = TestCommonJsonization.loadCompleteMultiLanguageProperty();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "MultiLanguageProperty",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteMultiLanguageProperty();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Range", () => {
  const instance = TestCommonJsonization.loadCompleteRange();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Range", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteRange();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of ReferenceElement", () => {
  const instance = TestCommonJsonization.loadCompleteReferenceElement();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "ReferenceElement",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteReferenceElement();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Blob", () => {
  const instance = TestCommonJsonization.loadCompleteBlob();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Blob", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteBlob();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of File", () => {
  const instance = TestCommonJsonization.loadCompleteFile();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "File", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteFile();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of AnnotatedRelationshipElement", () => {
  const instance = TestCommonJsonization.loadCompleteAnnotatedRelationshipElement();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "AnnotatedRelationshipElement",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteAnnotatedRelationshipElement();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Entity", () => {
  const instance = TestCommonJsonization.loadCompleteEntity();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Entity", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteEntity();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of EventPayload", () => {
  const instance = TestCommonJsonization.loadCompleteEventPayload();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "EventPayload",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteEventPayload();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of BasicEventElement", () => {
  const instance = TestCommonJsonization.loadCompleteBasicEventElement();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "BasicEventElement",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteBasicEventElement();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Operation", () => {
  const instance = TestCommonJsonization.loadCompleteOperation();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Operation", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteOperation();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of OperationVariable", () => {
  const instance = TestCommonJsonization.loadCompleteOperationVariable();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "OperationVariable",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteOperationVariable();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Capability", () => {
  const instance = TestCommonJsonization.loadCompleteCapability();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Capability", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteCapability();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of ConceptDescription", () => {
  const instance = TestCommonJsonization.loadCompleteConceptDescription();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "ConceptDescription",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteConceptDescription();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Reference", () => {
  const instance = TestCommonJsonization.loadCompleteReference();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Reference", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteReference();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Key", () => {
  const instance = TestCommonJsonization.loadCompleteKey();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Key", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteKey();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of LangString", () => {
  const instance = TestCommonJsonization.loadCompleteLangString();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "LangString", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteLangString();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of Environment", () => {
  const instance = TestCommonJsonization.loadCompleteEnvironment();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "Environment", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteEnvironment();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of EmbeddedDataSpecification", () => {
  const instance = TestCommonJsonization.loadCompleteEmbeddedDataSpecification();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "EmbeddedDataSpecification",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteEmbeddedDataSpecification();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of ValueReferencePair", () => {
  const instance = TestCommonJsonization.loadCompleteValueReferencePair();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "ValueReferencePair",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteValueReferencePair();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of ValueList", () => {
  const instance = TestCommonJsonization.loadCompleteValueList();

  compareOrRecordTrace(
    instance,
    path.join(TestCommon.TEST_DATA_DIR, "descend", "ValueList", "complete.json.trace")
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteValueList();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of DataSpecificationIec61360", () => {
  const instance = TestCommonJsonization.loadCompleteDataSpecificationIec61360();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "DataSpecificationIEC61360",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteDataSpecificationIec61360();

  expectDescendAndPassThroughVisitorSame(instance);
});

test("descend of DataSpecificationPhysicalUnit", () => {
  const instance = TestCommonJsonization.loadCompleteDataSpecificationPhysicalUnit();

  compareOrRecordTrace(
    instance,
    path.join(
      TestCommon.TEST_DATA_DIR,
      "descend",
      "DataSpecificationPhysicalUnit",
      "complete.json.trace"
    )
  );
});

test("descend against PassThroughVisitor", () => {
  const instance = TestCommonJsonization.loadCompleteDataSpecificationPhysicalUnit();

  expectDescendAndPassThroughVisitorSame(instance);
});