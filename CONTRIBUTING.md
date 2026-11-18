# Contributing to ca-skills

## Report a problem

Use the [issue tracker](https://github.com/odango-chan/ca-skills/issues) for specification questions, broken examples, and documentation issues. Include the CA-SL version, the clause or file, and the expected and observed behavior. For a toolchain problem, include the component and commit you tested and the smallest input that reproduces it.

## Prepare a change

- Use the [current specification](docs/skill-language-spec.md) and [authoring guide](docs/authoring.md) for new Skill source. The [v1alpha5 examples](examples/README.md) show the repository's package layout.
- Cite the published clause when proposing a specification correction. Record editorial corrections in the [release record](docs/releases/ca-sl-v1alpha5.md) and describe any proposed semantic change in an issue.
- Give the source and applicable terms when adding material from another project or standard. See the [source provenance](docs/source-provenance.md) for existing imports and references.

## Verify and submit

Run `make verify` with Python 3.11 and Make. This checks package layout and local references, specification structure, and the Wait and Ingress registries. In the PR, record the checks you ran and their results. For changes that affect Compiler behavior or Runtime execution, link any separate acceptance evidence available for the change.
