import * as aas from "../src";

test("types match", () => {
  // Create a property
  const aProperty = new aas.types.Property(aas.types.DataTypeDefXsd.Int);

  // Create a blob
  const aBlob = new aas.types.Blob("text/plain");

  // Create another property
  const anotherProperty = new aas.types.Property(aas.types.DataTypeDefXsd.Decimal);

  // Check the type matches

  expect(aas.types.typesMatch(aProperty, aProperty)).toStrictEqual(true);

  expect(aas.types.typesMatch(aProperty, aBlob)).toStrictEqual(false);

  expect(aas.types.typesMatch(aProperty, anotherProperty)).toStrictEqual(true);
});
