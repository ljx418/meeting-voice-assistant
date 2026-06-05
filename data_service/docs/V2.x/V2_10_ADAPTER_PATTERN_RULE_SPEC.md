# V2.10 Adapter Pattern Rule Spec

## Purpose

Define generic adapter rules so implementation does not drift into project-specific hardcoding.

## Built-in Adapter Rules

### python_registry_assignment

Matches:

- dictionary assignments with string keys and symbol/class/function values;
- list/tuple assignments with symbol elements.

Accepted when:

- registry line range is valid;
- value symbol resolves to definition;
- definition line range truth check passes.

### python_decorator_registration

Matches:

- function/class decorators that include registration-like names;
- decorator arguments with string identifiers.

Accepted when:

- decorated function/class definition line range is valid;
- decorator line range is valid;
- registration label is deterministic.

### python_class_inheritance

Matches:

- classes inheriting from base classes with configured/generic architecture names.

Accepted when:

- class definition line range is valid;
- base class reference is resolvable or configured as known base;
- no runtime behavior is claimed.

### python_factory_call

Matches:

- call expressions that register named handlers, workflows, agents, or adapters.

Accepted when:

- call line range is valid;
- handler argument resolves to definition;
- call target is deterministic.

### cli_parser_registration

Matches:

- argparse/click/typer-style parser registrations.

Accepted when:

- command registration line range is valid;
- handler or callback resolves where applicable.

### tui_command_table

Matches:

- command maps or keybinding tables in Python source.

Accepted when:

- command row line range is valid;
- action handler resolves or remains `needs_review`.

### workflow_manifest / architecture_manifest

Matches:

- JSON/YAML/TOML manifest entries.

Accepted only after:

- manifest schema validation;
- declared symbol/path binds to code;
- code truth check passes.

### runtime_introspection_candidate

Matches:

- allowlisted command JSON output.

Accepted only after:

- static binding to code evidence;
- runtime candidate never accepted by itself.

## Universal Rejections

- no line range;
- absolute source path in public output;
- token-only match;
- import treated as runtime call;
- manifest/document/runtime-only evidence accepted;
- project-specific names embedded in generic rule code.
