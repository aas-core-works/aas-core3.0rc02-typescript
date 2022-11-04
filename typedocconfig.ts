module.exports = {
  src: ["./src/.ts"],
  mode: "file",
  includeDeclarations: true,
  tsconfig: "tsconfig.json",
  excludePrivate: true,
  excludeProtected: true,
  excludeExternals: true,
  readme: "README.md",
  name: "aas-core3.0rc02-typescript",
  ignoreCompilerErrors: false,
  // From https://cancerberosgx.github.io/javascript-documentation-examples/examples/typedoc-tutorial-basic/docs/docco/src/index.html:
  // Installed plugins are loaded automatically by typedoc tool so installing
  // a plugin is all you need to do in order to use it.
  plugin: "none",
  listInvalidSymbolLinks: true
};
