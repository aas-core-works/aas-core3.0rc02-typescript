# aas-core3.0rc02-typescript

Manipulate, verify and de/serialize Asset Administration Shells based on the version 3.0VRC02 of the meta-model. 

[![CI](https://github.com/aas-core-works/aas-core3.0rc02-typescript/actions/workflows/ci.yml/badge.svg)](https://github.com/aas-core-works/aas-core3.0rc02-typescript/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/aas-core-works/aas-core3.0rc02-typescript/badge.svg?branch=main)](https://coveralls.io/github/aas-core-works/aas-core3.0rc02-typescript?branch=main)

This is a software development kit (SDK) to:

* manipulate,
* verify, and
* de/serialize to and from JSON

… Asset Administration Shells based on the version 3.0VRC02 of the meta-model.

For a brief introduction, see [Getting Started].

For a detailed documentation of the API, see [API Documentation].

We documented most of the rationale behind the implementation and interface choices in the section [Design Decisions]. 

If you want to contribute, see our [Contributing Guide].

Please see the [Changelog] for the list of changes between versions.

[Getting Started]: #getting-started
[API documentation]: https://aas-core-works.github.io/aas-core3.0rc02-typescript
[Design Decisions]: #design-decisions
[contributing guide]: #contributing-guide
[changelog]: #changelog

## Getting Started

Here's a quick intro to get you started with the SDK.
See how you can:

* [Install the SDK](#install-the-sdk),
* [Programmatically create, get and set properties of an AAS model](#create-get-and-set),
* [Switch on runtime types of instances](#switch-on-runtime-types),
* [Iterate over, copy and transform a model](#iterate-and-transform),
* [Verify a model](#verify), and
* [De/serialize a model from and to JSON](#json-deserialization).

### Install the SDK

The SDK is available as the npm package [@aas-core-works/aas-core3.0rc02-typescript].

Install it using `npm`:

```
npm install @aas-core-works/aas-core3.0rc02-typescript
```

[@aas-core-works/aas-core3.0rc02-typescript]: https://www.npmjs.com/package/@aas-core-works/aas-core3.0rc02-typescript

### Create, Get and Set

The module [`types`] defines all the data types of the meta-model.
This includes classes, interfaces and enumerations.

The module [`types`] also contains abstract visitors and transformers, but we will write more about them in [Iterate and Transform](#iterate-and-transform) section.

[`types`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/modules/types.html

#### Creation

We use constructors to create an AAS model.

Usually you start bottom-up, all the way up to the [`types.Environment`].

[`types.Environment`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Environment.html

#### Getting and Setting Properties

All properties of the classes are modeled as TypeScript properties.

After initialization of a class, you can directly get and modify its properties.

The properties which are not set should be assigned `null`.
To avoid confusion and unnecessary complexity, the SDK does not expect `undefined` property values.  

#### Getters with a Default Value

For optional properties which come with a default value, we provide special getters, `{property name}OrDefault`.
If the property is `null`, this getter will give you the default value.
Otherwise, if the property is set, the actual value of the property will be returned.

For example, see [`types.IHasKind.kindOrDefault`].

[`types.IHasKind.kindOrDefault`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/interfaces/types.IHasKind.html#kindOrDefault

#### Example: Create an Environment with a Submodel

Here is a very rudimentary example where we show how to create an environment which contains a submodel.

The submodel will contain two elements, a property and a blob.

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Create the first element
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

// Create the second element
const anotherElement = new aas.types.Blob(
  "application/octet-stream"
);
anotherElement.idShort = "someBlob";
anotherElement.value = new Uint8Array([0xDE, 0xAD, 0xBE, 0xEF]);

// You can directly access the element properties.
anotherElement.value = new Uint8Array([0xDE, 0xAD, 0xC0, 0xDE]); 

// Nest the elements in a submodel
const submodel = new aas.types.Submodel(
  "some-unique-global-identifier"
);
submodel.submodelElements = [
  someElement,
  anotherElement
];

// Now create the environment to wrap it all up
const environment = new aas.types.Environment();
environment.submodels = [submodel];

// You can access the propreties from the children as well.
(<aas.types.Blob>environment.submodels![0].submodelElements![1]).value =
  new Uint8Array([0xC0, 0x01, 0xCA, 0xFE]);

// Now you can do something with the `environment`...
``` 

### Switch on Runtime Types

JavaScript, and consequently TypeScript, do not support multiple inheritance.
We therefore introduce only a single, most general abstract class [`types.Class`].
What is defined as "abstract class" in the meta-model, we implement as *interfaces* in TypeScript.

All the concrete classes inherit from [`types.Class`] and specify which interfaces ("abstract classes") they implement.

While TypeScript allows us to define interfaces, they are merely used to assure type safety at compile time, but cannot be used for type switches at runtime.
This has repercussions, for example, when you want to select submodel elements which are of type [`types.Property`].
TypeScript does not provide an efficient way to check the runtime type based on interfaces alone.

To allow for efficient type casts and checks, we implement functions `as{class name}` and `is{class name}` for all the classes of the meta-model.
The implementation is based on transformer pattern (see Section [Iterate and Transform] below), and performs only a couple of dispatch function calls.

The functions `as{class name}` allow you to *try* a cast to a given type.
If the cast is possible, the input is simply returned.
Otherwise, the function returns `null`.

Here is a short example with [`types.asProperty`] and [`types.asBlob`]:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Create the first element
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

console.log(aas.types.asProperty(someElement) === someElement)
// Prints: true

console.log(aas.types.asBlob(someElement) === null);
// Prints: true
```

The functions `is{class name}` provide you with runtime type checks.
Thanks to [TypeScript type assertions] provided in its signature, the TypeScript compiler can automatically infer the appropriate type on successful checks.

Here is a short example with [`types.isProperty`] and [`types.isBlob`]:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Create the first element
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

console.log(aas.types.isProperty(someElement))
// Prints: true

console.log(aas.types.isBlob(someElement));
// Prints: false

if (aas.types.isProperty(someElement)) {
  // TypeScript compiler will automatically infer that `someElement`
  // is a `types.Property` thanks to type assertions from
  // `types.isProperty`.
  console.log(someElement.value);
  // Prints: 1984
}
```

[`types.Class`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Class.html
[`types.Property`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Property.html
[Iterate and Transform]: #iterate-and-transform
[`types.asProperty`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/types.asProperty.html
[`types.asBlob`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/types.asBlob.html
[TypeScript type assertions]: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions
[`types.isProperty`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/types.isProperty.html
[`types.isBlob`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/types.isBlob.html

The `is*` and `as*` functions assume that you know the expected type in the check ahead of time.
This does not work if you use a prototype to define a type, or want to check whether two instances share the same type, since you can not extract the type information from an instance.
For those situations, we provide [`typesMatch`] function:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Create a property
const aProperty = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);

// Create a blob
const aBlob = new aas.types.Blob(
  "text/plain"
);

// Create another property
const anotherProperty = new aas.types.Property(
  aas.types.DataTypeDefXsd.Decimal
);

// Check the type matches

console.log(aas.types.typesMatch(aProperty, aProperty))
// Prints: true

console.log(aas.types.typesMatch(aProperty, aBlob))
// Prints: false

console.log(aas.types.typesMatch(aProperty, anotherProperty))
// Prints: true
```

### Iterate and Transform

The SDK provides various ways how you can loop through the elements of the model, and how these elements can be transformed.
Each following section will look into one of the approaches.

#### `over*OrEmpty`

For all the optional lists, there is a corresponding `over{property name}OrEmpty` getter.
It gives you an [`IterableIterator`].
If the property is not set (*i.e.* set to `null`), this getter will yield empty.
Otherwise, it will yield from the actual property value.

For example, see [`types.Environment.overSubmodelsOrEmpty`].

[`IterableIterator`]: https://www.typescriptlang.org/docs/handbook/iterators-and-generators.html
[`types.Environment.overSubmodelsOrEmpty`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Environment.html#overSubmodelsOrEmpty

#### `descend` and `descendOnce`

If you are writing a simple script and do not care about the performance, the SDK provides two methods in the most abstract class [`types.Class`], [`descendOnce`] and [`descend`], which you can use to loop through the instances.

[`descendOnce`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Class.html#descendOnce
[`descend`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Class.html#descend

Both [`descendOnce`] and [`descend`] iterate over referenced children of an instance of [`types.Class`].
The method [`descendOnce`], as it names suggests, stops after all the immediate children has been iterated over.
The method [`descend`] continues recursively to grand-children, grand-grand-children *etc.*

Here is a short example how you can get all the properties from an environment whose ID-short starts with another:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Prepare the environment
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

const anotherElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
anotherElement.idShort = "anotherProperty";
anotherElement.value = "1985";

const yetAnotherElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
yetAnotherElement.idShort = "yetAnotherProperty";
yetAnotherElement.value = "1986";

const submodel = new aas.types.Submodel(
  "some-unique-global-identifier"
);
submodel.submodelElements = [
  someElement,
  anotherElement,
  yetAnotherElement
];

const environment = new aas.types.Environment();
environment.submodels = [submodel];

// Iterate using `descend`
for (const something of environment.descend()) {
  if (
    aas.types.isProperty(something)
    && something.idShort?.toLowerCase().includes("another")
  ) {
    console.log(something.idShort);
  }
}

// Prints:
// anotherProperty
// yetAnotherProperty
```

Iteration with [`descendOnce`] and [`descend`] works well if the performance is irrelevant.
However, if the performance matters, this is not a good approach.
First, all the children will be visited (even though you need only a small subset).
Second, you execute the loop body on every single instance in the loop.
In the example above, you check the runtime type with [`types.isProperty`] on every single instance referenced from the [`types.Environment`].

Let’s see in the next section how we could use a more efficient, albeit also a more complex approach.

#### Visitor

[Visitor pattern] is a common design pattern in software engineering.
We will not explain the details of the pattern here as you can read about in the ample literature in books or in Internet.

[Visitor pattern]: https://en.wikipedia.org/wiki/Visitor_pattern

The cornerstone of the visitor pattern is [double dispatch]: instead of casting to the desired type during the iteration, the method [`accept`] of [`types.Class`] directly dispatches to the appropriate visitation method.

[double dispatch]: https://en.wikipedia.org/wiki/Double_dispatch
[`accept`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.Class.html#accept

This allows us to spare runtime type switches and directly dispatch the execution.
The SDK already implements [`accept`] methods, so you only have to implement the visitor.

The visitor class has a visiting method for each class of the meta-model.
In the SDK, we provide different flavors of the visitor abstract classes which you can readily implement:

* [`AbstractVisitor`] which needs all the visit methods to be implemented,
* [`PassThroughVisitor`] which visits all the elements and does nothing, and
* [`AbstractVisitorWithContext`] which propagates a context object along the iteration.

[`AbstractVisitor`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.AbstractVisitor.html
[`PassThroughVisitor`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.PassThroughVisitor.html
[`AbstractVisitorWithContext`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.AbstractVisitorWithContext.html 

Let us re-write the above example related to [`descend`] method with a visitor pattern: 

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Prepare the environment
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

const anotherElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
anotherElement.idShort = "anotherProperty";
anotherElement.value = "1985";

const yetAnotherElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
yetAnotherElement.idShort = "yetAnotherProperty";
yetAnotherElement.value = "1986";

const submodel = new aas.types.Submodel(
  "some-unique-global-identifier"
);
submodel.submodelElements = [
  someElement,
  anotherElement,
  yetAnotherElement
];

const environment = new aas.types.Environment();
environment.submodels = [submodel];

// Implement the visitor
class Visitor extends aas.types.PassThroughVisitor {
  visitProperty(that: aas.types.Property): void {
    if (that.idShort?.toLowerCase().includes("another")) {
      console.log(that.idShort);
    }
  }
}

// Iterate
const visitor = new Visitor();
visitor.visit(environment);

// Prints:
// anotherProperty
// yetAnotherProperty 
```

There are important differences to iteration with [`descend`]:

* Due to double dispatch, we spare a cast.
  This is usually more efficient.
* The iteration logic in [`descend`] lives very close to where it is executed.
  In contrast, the visitor needs to be defined as a separate class.
  While sometimes faster, writing the visitor makes the code less readable.

#### Descend or Visitor?

In general, people familiar with the [visitor pattern] and object-oriented programming will prefer, obviously, visitor class.
People who like functional programming, generator expressions and ilks will prefer [`descend`].

It is difficult to discuss different tastes, so you should probably come up with explicit code guidelines in your code and stick to them.

Make sure you always profile before you sacrifice readability and blindly apply one or the other approach for performance reasons.

#### Transformer

A transformer pattern is an analogous to [visitor pattern], where we "transform" the visited element into some other form (be it a string or a different object).
It is very common in compiler design, where the abstract syntax tree is transformed into a different representation.

The SDK provides different flavors of a transformer:

* [`AbstractTransformer`], where the model element is directly transformed into something, and
* [`AbstractTransformerWithContext`], which propagates the context object along the transformations.

Usually you implement for each concrete class how it should be transformed.
If you want to specify only a subset of transformations, and provide the default value for the remainder, the SDK provides [`TransformerWithDefault`] and [`TransformerWithDefaultAndContext`].

We deliberately omit an example due to the length of the code.
Please let us know by [creating an issue] if you would like to have an example here.

[`AbstractTransformer`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.AbstractTransformer.html
[`AbstractTransformerWithContext`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.AbstractTransformerWithContext.html
[`TransformerWithDefault`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.TransformerWithDefault.html
[`TransformerWithDefaultAndContext`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/types.TransformerWithDefaultAndContext.html

#### Iterate over Enumeration Literals

TypeScript features [enumerations] as a core part of the language.
However, the enumerations are not supported in JavaScript, and it is up to the transpiler how they are going to be represented in JavaScript.

We use numeric literals to capture the enumerations from the meta-model (see Section [design decisions]).
While there are [ways to iterate over enumerations], the code is not particularly type-safe when used with numeric enumeration literals.
For example, the literals are often iterated as strings even though the enumeration literals are originally given as integers.
Moreover, all the code snippets looked rather confusing to us.
We therefore provide `over{enumeration name}` functions in [`types`] module which you can use to iterate over enumeration literals.
See, for example, [`types.overAasSubmodelElements`].

[enumerations]: https://www.typescriptlang.org/docs/handbook/enums.html
[design-decisions]: #design-decisions
[ways to iterate over enumerations]: https://stackoverflow.com/questions/39372804/how-can-i-loop-through-enum-values-for-display-in-radio-buttons

If you want to obtain the string representation of the literal, we provide the [`stringification`] module.
The functions `stringification.{enumeration name}ToString` gives you back either the string representation of the literal, or `null` if the literal was invalid.
For the client's convenience, our SDK also implements the functions `stringification.must{enumeration name}ToString` which returns the string representation, or throws an error.
If you are certain that your code deals with only correct literals, `stringification.must{enumeration name}ToString` will spare you a nullability check.
For example, see [`stringification.modelingKindToString`] and [`stringification.mustModelingKindToString`].

[`stringification.modelingKindToString`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/stringification.modelingKindToString.html
[`stringification.mustModelingKindToString`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/stringification.mustModelingKindToString.html

Here is a short example that illustrates how to loop over enumeration literals of the enumeration [`types.ModelingKind`] using the function [`types.overModelingKind`]:

[`types.ModelingKind`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/enums/types.ModelingKind.html
[`types.overModelingKind`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/types.overModelingKind.html

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

for (const literal of aas.types.overModelingKind()) {
  const asString = aas.stringification.mustModelingKindToString(literal);
  console.log(
    `${literal} ${typeof (literal)} ${asString}`
  );
}
// Prints:
// 0 number Template
// 1 number Instance
```

### Verify

Our SDK allows you to verify that a model satisfies the constraints of the meta-model.

The verification logic is concentrated in the module [`verification`], and all it takes is a call to [`verification.verify`] function.
The function [`verification.verify`] will check that constraints in the given model element are satisfied, including the recursion into children elements.
The function returns an [`IterableIterator`] of [`verification.VerificationError`]'s, which you can use for further processing (*e.g.*, report to the user).

[`verification`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/modules/verification.html
[`verification.verify`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/verification.verify.html
[`verification.VerificationError`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/verification.VerificationError.html

Here is a short example snippet:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Prepare the environment
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
// The ID-shorts must be proper variable names,
// but there is a dash (`-`) in this ID-short. 
someElement.idShort = "some-property";
someElement.value = "1984";

const submodel = new aas.types.Submodel(
  "some-unique-global-identifier"
);
submodel.submodelElements = [someElement];

const environment = new aas.types.Environment();
environment.submodels = [submodel];

for (const error of aas.verification.verify(environment)) {
  console.log(`${error.path}: ${error.message}`);
}

// Prints:
// .submodels[0].submodelElements[0].idShort: ID-short of Referables 
// shall only feature letters, digits, underscore (``_``); 
// starting mandatory with a letter. *I.e.* ``[a-zA-Z][a-zA-Z0-9_]+``.
```

If you only want to check the immediate instance, and you do not want the verification to recurse into children, supply the second parameter `recurse` set to `false` to the call of [`verification.verify`]:

```
for (const error of verification.verify(environment, false)) {
  console.log(`${error.path}: ${error.message}`);
}

// Does not print anything as environment instance for itself
// is valid. However, the submodel elements beneath the environment
// are invalid, but this verification is not recursive.
```

#### Limit the Number of Reported Errors

Since the function [`verification.verify`] gives you an [`IterableIterator`], you can simply break out of the loop.

For example, to report only the first 10 errors (assuming the code from the example above):

```typescript
let reportedErrors = 0;

for (const error of verification.verify(environment)) {
  console.log(`${error.path}: ${error.message}`);
  reportedErrors++;
  
  if (reportedErrors === 10) {
    break;
  }
}
```

#### Omitted Constraints

Not all constraints specified in the meta-model can be verified.
Some constraints require external dependencies such as an AAS registry.
Verifying the constraints with external dependencies is out-of-scope of our SDK, as we still lack standardized interfaces to those dependencies.

However, all the constraints which need *no* external dependency are verified.
For a full list of exception, please see the description of the module [`types`].

### JSON de/serialization

Our SDK handles the de/serialization of the AAS models from and to JSON format through the module [`jsonization`].

[`jsonization`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/modules/jsonization.html

#### Serialize

To serialize, you call the function [`jsonization.toJsonable`] on an instance of [`types.Class`] which will convert it to a JSON-able JavaScript object.

[`jsonization.toJsonable`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/jsonization.toJsonable.html

Here is a snippet that converts the environment first into a JSON-able object, and next converts the JSON-able object to text:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

// Prepare the environment
const someElement = new aas.types.Property(
  aas.types.DataTypeDefXsd.Int
);
someElement.idShort = "someProperty";
someElement.value = "1984";

const submodel = new aas.types.Submodel(
  "some-unique-global-identifier"
);
submodel.submodelElements = [someElement];

const environment = new aas.types.Environment();
environment.submodels = [submodel];

// Serialize to a JSON-able object
const jsonable = aas.jsonization.toJsonable(environment);

// Convert the JSON-able object to a string
const text = JSON.stringify(jsonable, null, 2);

console.log(text);
// Prints:
// {
//   "submodels": [
//     {
//       "id": "some-unique-global-identifier",
//       "submodelElements": [
//         {
//           "idShort": "some_property",
//           "valueType": "xs:int",
//           "value": "1984",
//           "modelType": "Property"
//         }
//       ],
//       "modelType": "Submodel"
//     }
//   ]
// }
```

#### De-serialize

Our SDK can convert a JSON-able object back to an instance of [`types.Class`]. 
To that end, you call the appropriate function `jsonization.{class name}FromJsonable`.
For example, if you want to de-serialize an instance of [`types.Environment`], call [`jsonization.environmentFromJsonable`].

Note that the SDK cannot de-serialize classes automatically as the discriminator property `modelType` is not included in the serializations for *all* the classes.
Without the discriminator property provided, we thus cannot know the actual type of the instance just from the serialization.
See [this sections on discriminators in AAS Specs] for more details. 

[`jsonization.environmentFromJsonable`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/functions/jsonization.environmentFromJsonable.html
[this sections on discriminators in AAS Specs]: https://github.com/admin-shell-io/aas-specs/tree/master/schemas/json#discriminator

The functions `jsonization.{class name}FromJsonable` return an ["either" structure]: either the successfully de-serialized instance, or a de-serialization error, if there was any.
If there was an error, its property [`error`] will be set.
Otherwise, the property [`value`] will contain the de-serialized instance.
If you prefer an exception to be thrown in case of de-serialization errors, and do not want to check for [`error`] explicitly, then call the method [`mustValue`]. 

["either" structure]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/common.Either.html
[`error`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/common.Either.html#error
[`value`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/common.Either.html#value
[`mustValue`]: https://aas-core-works.github.io/aas-core3.0rc02-typescript/classes/common.Either.html#mustValue

We use the ["either" structure] (sometimes also called "disjoint union") instead of exceptions to avoid the costly stack unwinding. 
Stack unwinding makes sense if you want since the line of code is irrelevant in case of de-serialization errors.   

Here is an example snippet to show you how to de-serialize an instance of [`types.Environment`]:

```typescript
import * as aas from "@aas-core-works/aas-core3.0rc02-typescript";

const text = `
{
  "submodels": [
    {
      "id": "some-unique-global-identifier",
      "submodelElements": [
        {
          "idShort": "someProperty",
          "valueType": "xs:boolean",
          "modelType": "Property"
        }
      ],
      "modelType": "Submodel"
    }
  ]
}
`;

const jsonable = JSON.parse(text);

const instanceOrError = aas.jsonization.environmentFromJsonable(
  jsonable
);
if (instanceOrError.error !== null) {
  console.log(
    "De-serialization failed: " +
    `${instanceOrError.error.path}: ` +
    `${instanceOrError.error.message}`
  );
}
// Doesn't print anything as `text` is
// a valid representation.

const environment = instanceOrError.mustValue();

for (const something of environment.descend()) {
  console.log(something.constructor.name);
}
// Prints:
// Submodel
// Property
```

## API

For a detailed documentation of the API, see [API documentation].

## Design Decisions

We present here some of the choices we made during the design and implementation of the SDK.
While it is not necessary to understand our thread of thought to *use* the SDK, we explain the rationale here behind why we structured and programmed the SDK the way we did.
This should hopefully clear up some confusion, or ease the frustration, if you prefer certain features to be implemented differently.

### Enumerations as Numbers

We optimize the enumerations for look-ups and comparisons instead of string representation.
Thus, we implement literals as numbers (instead of strings).
For example, this makes lookups faster as hash values are directly computed on a numeric literal involving usually only a few arithmetic operations.

In contrast, if the enumeration literals were listed as strings, the hash value of the literal would need to be computed by iterating through *all the characters* of the string.

### No Parameter Properties in Constructors

[Parameter properties] in constructor signatures are a succinct way to define public and private properties of a class.

[Parameter properties]: https://www.typescriptlang.org/docs/handbook/classes.html#parameter-properties

As we use TSDoc to write documentation, documenting the properties *in the constructor* hurts the readability.
Therefore, we generate properties (with documentation) separately from constructors in the class body.

### Inheritance Hierarchy Different From Meta-model

The AAS meta-model uses multiple inheritance.
However, TypeScript only supports single inheritance.
Moreover, in case of long inheritance chains, the type checks with `instanceof` might be linear in time complexity.
Please see, for example, this [StackOverflow question about the efficiency of `instanceof`]

[StackOverflow question about the efficiency of `instanceof`]: https://stackoverflow.com/questions/5925063/how-exactly-does-javascript-instanceof-work-is-it-slow-style

Instead of multiple inheritance we use interfaces and provide `is*` and `as*` functions to dynamically decide the instance type at runtime.
All the classes inherit from the most general class [`types.Class`]. 
Please see Section [Switch on Runtime Types].

[Switch on Runtime Types]: #switch-on-runtime-types

### Use of `Either` Construct

We use ["either" structure] in de-serialization since JavaScript engines are not guaranteed to be optimized for try-catch blocks.
See, for example, [this StackOverflow question about the efficiency of try/catch blocks].

[this StackOverflow question about the efficiency of try/catch blocks]: https://stackoverflow.com/questions/19727905/in-javascript-is-it-expensive-to-use-try-catch-blocks-even-if-an-exception-is-n

By using `Either`, we can do away with try/catch blocks and shave off quite a few cycles.
See Section [De-serialize] for more information.

[De-serialize]: #de-serialize

### No XML

We do not implement XML as we could not find a solid library as of time of this writing (2022-12-21) which works both for NodeJS and in the browsers.
The closest we got is [sax.js], but it seems not maintained anymore (see [this issue in sax.js repository about maintenance]).
There are multiple forks, such as [saxes], but they seem to have much lower visibility and attention.

[sax.js]: https://github.com/isaacs/sax-js
[this issue in sax.js repository about maintenance]: https://github.com/isaacs/sax-js/issues/238
[saxes]: https://github.com/lddubeau/saxes

We are open to suggestions, and we are of course ready to re-evaluate our current decision to skip XML de/serialization of AAS models.

### Bytes as `Uint8Array`

There are various ways how to implement an array of bytes in TypeScript (and JavaScript).
For example, we could use plain strings (with constraint that the code points are limited to the range `[0, 255]`).
Another representation would be to use arrays of numbers (`Array<number>`) and restrict numbers to the range `[0, 255]`.
There are many others.

We finally settled down on [`Uint8Array`] that felt most natural to us.
Opposed to string and arrays of numbers, [`Uint8Array`] are usually implemented in a memory-efficient way (one byte per byte point, instead of 2 bytes for strings or 8 bytes for array of numbers).

However, [`Uint8Array`]'s are immutable, so any changes involve a copy-on-write.
We deemed such cases to be rare in applications, but this is open for a debate.
Please [create an issue] if your application needs mutable byte arrays so that we can discuss the alternatives.

[create an issue]: https://github.com/aas-core-works/aas-core3.0rc02-typescript/issues
[`Uint8Array`]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array

### In-house Base64 De/coding

The [base64 encoding] is differently implemented for the browser and for nodejs.
The browser platforms provide [atob] and [btoa] functions, while it is common to use [Buffers in nodejs].

We implement our own [base64 encoding] and decoding as we wanted to have a single implementation across different platforms (*e.g.*, browser and nodejs).

Additionally, we represent byte values as [`Uint8Array`], so we also make sure that our base64 implementation directly feeds into [`Uint8Array`]'s.
For example, if we used [atob] we would have to convert the string into [`Uint8Array`], which costs at least an additional memory copy.

[base64 encoding]: https://en.wikipedia.org/wiki/Base64
[atob]: https://developer.mozilla.org/en-US/docs/Web/API/atob
[btoa]: https://developer.mozilla.org/en-US/docs/Web/API/btoa
[Buffers in nodejs]: https://nodejs.org/docs/latest/api/buffer.html

Please note that our implementation also suffers from the lack of padding check (see this [paper on padding check]) as we followed widely used algorithms in the wild.
According to the same [paper on padding check], this vulnerability exists in standard libraries for Python, PHP, JavaScript, Node.js and others.

[paper on padding check]: https://eprint.iacr.org/2022/361.pdf

## Contributing Guide

### Issues

Please report bugs or feature requests by [creating GitHub issues].

[creating GitHub issues]: https://github.com/aas-core-works/aas-core3.0rc02-typescript/issues

### In Code

If you want to contribute in code, pull requests are welcome!

Please do [create a new issue] before you dive into coding.
It can well be that we already started working on the feature, or that there are upstream or downstream complexities involved which you might not be aware of.

[create a new issue]: https://github.com/aas-core-works/aas-core3.0rc02-typescript/issues

### SDK Code Generation

The biggest part of the code has been automatically generated by [aas-core-codegen].
It probably makes most sense to change the generator rather than add new functionality.
However, this needs to be decided on a case-by-case basis.

[aas-core-codegen]: https://github.com/aas-core-works/aas-core-codegen

### Test Code Generation

The majority of the unit tests has been automatically generated using the Python scripts in the [`testgen/`] directory.

[`testgen/`]: https://github.com/aas-core-works/aas-core3.0rc02-typescript/tree/main/testgen

To re-generate the test code: 

* Create the virtual environment:

  ```
  python3 -m venv venv
  ```

* Activate the virtual environment (on Windows):

  ```
  venv/Scripts/activate
  ```

  ... or on Linux/Mac:

  ```
  source venv/bin/activate
  ```

* Install the development dependencies:

  ```
  pip3 install --editable testgen
  ```

* Run the main script:

  ```
  python testgen/generate_all.py  
  ```


### Test Data

The test data is automatically generated by [aas-core3.0rc02-testgen], and copied to this repository on every change.

[aas-core3.0rc02-testgen]: https://github.com/aas-core-works/aas-core3.0rc02-testgen

### Building the Documentation

We use [TypeDoc] to build the documentation:

```
npx typedoc --out doc-local src/
```

After this command, the documentation is available in `doc-local` directory.

[TypeDoc]: https://typedoc.org/

### Pre-commit Checks

Please run:

```
npm run lint && npm run build && npm run test
```

... before every commit.

To automatically re-format the code:

```
npm run format
```

### Pull Requests

**Feature branches.** We develop using the feature branches, see [this section of the Git book].

[this section of the Git book]: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows

If you are a member of the development team, create a feature branch directly within the repository.

Otherwise, if you are a non-member contributor, fork the repository and create the feature branch in your forked repository.
See [this GitHub tutorial] for more guidance.

[this GitHub tutorial]: https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork

**Branch Prefix.** Please prefix the branch with your Github user name (*e.g.*, `mristin/Add-some-feature`).

**Continuous Integration.** GitHub will run the continuous integration (CI) automatically through GitHub actions.
The CI includes running the tests, inspecting the code, re-building the documentation *etc.*

### Commit Message

The commit messages follow the guidelines from https://chris.beams.io/posts/git-commit:

* Separate subject from body with a blank line,
* Limit the subject line to 50 characters,
* Capitalize the subject line,
* Do not end the subject line with a period,
* Use the imperative mood in the subject line,
* Wrap the body at 72 characters, and
* Use the body to explain *what* and *why* (instead of *how*).

## Changelog

### 1.0.0-rc.5

* Add type matching between two instances (#7)

### 1.0.0-rc.4

* Add bundling scripts (#4)

### 1.0.0-rc.3

* Fix readme to use the main module (#2)

### 1.0.0-rc.2

* Include stringification in the public modules
* Extend documentation with design decisions and iteration over enumeration literals
* Test that GitHub publishing workflow works

### 1.0.0-rc.1

* Initial version, ready for the first reviews
