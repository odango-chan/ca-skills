"""Repository-local CA-SL v1alpha4 example Script hygiene and local type check.

Not a Compiler or trusted Owner/Capability/Schema/Evidence validator.
The only assignability checked here is static local Script -> Script binding.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

NODE = re.compile(r"^  ([A-Za-z][A-Za-z0-9_-]*):\s*$")
SCRIPT = re.compile(r"^      script:\s+(\S+)\s*$")
ARGUMENT = re.compile(r"^        ([A-Za-z][A-Za-z0-9_]*):\s*(\S.*)\s*$")
SOURCE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)\.operation\.output(?:\.([A-Za-z][A-Za-z0-9_.]*))?$")
ALLOWED_METADATA = {
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minLength", "maxLength", "minItems", "maxItems",
}
BANNED_IMPORTS = {"os", "sys", "pathlib", "time", "datetime", "random", "socket",
                  "subprocess", "requests", "http", "urllib", "importlib", "ctypes"}
BANNED_CALLS = {"open", "eval", "exec", "compile", "__import__", "globals", "locals",
                "getattr", "setattr", "delattr"}

def _type_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _type_name(node.value) + "." + node.attr
    return ""

def _fields(module: ast.Module) -> dict[str, dict[str, tuple[ast.expr, bool]]]:
    items: dict[str, dict[str, tuple[ast.expr, bool]]] = {}
    for stmt in module.body:
        if isinstance(stmt, ast.ClassDef) and any(_type_name(b) == "TypedDict" for b in stmt.bases):
            fields: dict[str, tuple[ast.expr, bool]] = {}
            for item in stmt.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    name = item.target.id
                    if name in fields:
                        raise ValueError(f"duplicate TypedDict field {name}")
                    ann = item.annotation
                    optional = isinstance(ann, ast.Subscript) and _type_name(ann.value) == "NotRequired"
                    required = isinstance(ann, ast.Subscript) and _type_name(ann.value) == "Required"
                    if optional or required:
                        ann = ann.slice
                    fields[name] = (ann, not optional)
            items[stmt.name] = fields
        elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if _type_name(call.func) != "TypedDict" or len(call.args) != 2:
                continue
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name) or not isinstance(call.args[1], ast.Dict):
                raise ValueError("unsupported TypedDict declaration")
            fields = {}
            for key, value in zip(call.args[1].keys, call.args[1].values):
                if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                    raise ValueError("functional TypedDict keys must be string literals")
                ann = value
                optional = isinstance(ann, ast.Subscript) and _type_name(ann.value) == "NotRequired"
                if optional:
                    ann = ann.slice
                fields[key.value] = (ann, not optional)
            items[stmt.targets[0].id] = fields
    return items

def _schema(expr: ast.expr, defs: dict[str, dict[str, tuple[ast.expr, bool]]],
            stack: tuple[str, ...] = ()) -> tuple:
    if isinstance(expr, ast.Name):
        if expr.id in ("str", "int", "float", "bool"):
            return ("primitive", expr.id)
        if expr.id not in defs or expr.id in stack:
            raise ValueError(f"unresolved/recursive script type {expr.id}")
        return ("object", tuple(sorted(
            (name, required, _schema(ann, defs, (*stack, expr.id)))
            for name, (ann, required) in defs[expr.id].items()
        )))
    if isinstance(expr, ast.Subscript):
        name = _type_name(expr.value)
        if name == "list":
            return ("list", _schema(expr.slice, defs, stack))
        if name == "Literal":
            values = expr.slice.elts if isinstance(expr.slice, ast.Tuple) else [expr.slice]
            if not values or any(not isinstance(v, ast.Constant) for v in values):
                raise ValueError("Literal requires constant values")
            return ("literal", tuple(ast.literal_eval(v) for v in values))
        if name == "Annotated":
            if not isinstance(expr.slice, ast.Tuple) or len(expr.slice.elts) != 2:
                raise ValueError("Annotated requires type and metadata mapping")
            ty, meta = expr.slice.elts
            value = ast.literal_eval(meta)
            if not isinstance(value, dict) or not set(value) <= ALLOWED_METADATA:
                raise ValueError("unsupported Annotated metadata (G.4/F.6)")
            return ("annotated", _schema(ty, defs, stack), tuple(sorted(value.items())))
    raise ValueError(f"unsupported Script type: {ast.dump(expr)}")

def _subtype(source: tuple, target: tuple) -> bool:
    if source == target:
        return True
    if source[0] == "annotated" and target[0] != "annotated":
        return _subtype(source[1], target)
    if source[0] == "literal":
        if target[0] == "primitive":
            return all((type(x) in (str, int, float, bool)) and
                       (("str" if type(x) is str else "int" if type(x) is int else
                         "float" if type(x) is float else "bool") == target[1]) for x in source[1])
        if target[0] == "literal":
            return set(source[1]) <= set(target[1])
    if source[0] == "object" and target[0] == "object":
        a = {k: (required, typ) for k, required, typ in source[1]}
        b = {k: (required, typ) for k, required, typ in target[1]}
        # Strict TypedDicts are additionalProperties:false: extra keys fail F.5.
        return set(a) == set(b) and all(
            (not b[key][0] or a[key][0]) and _subtype(a[key][1], b[key][1])
            for key in b
        )
    if source[0] == "list" and target[0] == "list":
        return _subtype(source[1], target[1])
    return False

def _navigate(schema: tuple, path: str) -> tuple | None:
    result = schema
    for part in path.split(".") if path else []:
        if result[0] != "object":
            return None
        fields = {name: typ for name, _, typ in result[1]}
        result = fields.get(part)
        if result is None:
            return None
    return result

def validate_3gpp_traceability(skill: Path, errors: list[str]) -> None:
    """Require every current 5GC Procedure Node to have a 3GPP/CA mapping."""
    procedure = skill / "assurance" / "procedure.yaml"
    skill_doc = skill / "SKILL.md"
    if not procedure.is_file() or not skill_doc.is_file():
        return  # Small isolated unit-test fixtures may omit the authoring document.
    lines = procedure.read_text(encoding="utf-8").splitlines()
    node_ids: list[str] = []
    for index, line in enumerate(lines):
        match = NODE.match(line)
        if not match:
            continue
        node = match[1]
        node_ids.append(node)
        previous = lines[index - 1] if index else ""
        if not previous.startswith("  # 3GPP: "):
            errors.append(f"{skill.name}/{node}: missing adjacent '# 3GPP:' mapping comment")
        elif not any(tag in previous for tag in
                     ("3GPP_NATIVE", "3GPP_ADAPTER", "CA_ADAPTER", "CA_EXTENSION")):
            errors.append(f"{skill.name}/{node}: mapping comment lacks a valid classification")

    doc = skill_doc.read_text(encoding="utf-8")
    if "## 3GPP Traceability" not in doc:
        errors.append(f"{skill.name}: missing '## 3GPP Traceability' table")
        return
    if "TS 23.502 V18.12.0" not in doc:
        errors.append(f"{skill.name}: 3GPP reference version is not pinned")
    documented = set(re.findall(r"^\\|\\s*\\x60([A-Za-z][A-Za-z0-9_-]*)\\x60\\s*\\|",
                                doc, flags=re.MULTILINE))
    expected = set(node_ids)
    for node in sorted(expected - documented):
        errors.append(f"{skill.name}/{node}: missing SKILL.md 3GPP traceability row")
    for node in sorted(documented - expected):
        errors.append(f"{skill.name}/{node}: traceability row has no Procedure Node")


def validate_example_scripts(skill: Path, errors: list[str]) -> None:
    validate_3gpp_traceability(skill, errors)
    procedure = skill / "assurance" / "procedure.yaml"
    text = procedure.read_text(encoding="utf-8")
    script_nodes: dict[str, tuple[Path, dict[str, str]]] = {}
    current = ""
    active_script: Path | None = None
    in_args = False
    for line in text.splitlines():
        match = NODE.match(line)
        if match:
            current, active_script, in_args = match[1], None, False
            continue
        match = SCRIPT.match(line)
        if match:
            ref = match[1]
            if not re.fullmatch(r"scripts/[A-Za-z0-9_-]+\.py", ref) or "/" in ref[8:]:
                errors.append(f"{skill.name}/{current}: unsafe Script ref {ref}")
                continue
            active_script = skill / ref
            script_nodes[current] = (active_script, {})
            continue
        if line == "      arguments:" and active_script is not None:
            in_args = True
            continue
        if in_args and active_script is not None:
            match = ARGUMENT.match(line)
            if match:
                script_nodes[current][1][match[1]] = match[2]
            elif line.startswith("      ") or not line.startswith("        "):
                in_args = False

    referenced = {p.resolve() for p, _ in script_nodes.values()}
    directory = skill / "scripts"
    for file in sorted(directory.glob("*.py")) if directory.exists() else []:
        if file.resolve() not in referenced:
            errors.append(f"{skill.name}: unreferenced Script {file.relative_to(skill)}")
    models: dict[str, dict[str, tuple]] = {}
    for node, (script, args) in script_nodes.items():
        if not script.is_file():
            errors.append(f"{skill.name}/{node}: Script not found {script.relative_to(skill)}")
            continue
        try:
            source = script.read_text(encoding="utf-8")
            module = ast.parse(source, filename=str(script))
            defs = _fields(module)
            mains = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "main"]
            if len(mains) != 1 or not isinstance(mains[0], ast.FunctionDef):
                raise ValueError("exactly one synchronous main required")
            main = mains[0]
            if (len(main.args.args) != 1 or main.args.args[0].arg != "input"
                or main.args.vararg or main.args.kwarg or main.args.defaults
                or main.args.kwonlyargs or main.args.posonlyargs or main.returns is None):
                raise ValueError("main(input: InputTypedDict) -> OutputTypedDict required")
            ann = main.args.args[0].annotation
            if not isinstance(ann, ast.Name) or not isinstance(main.returns, ast.Name):
                raise ValueError("main signature must name strict TypedDict classes")
            ins = _schema(ann, defs)
            outs = _schema(main.returns, defs)
            if ins[0] != "object" or outs[0] != "object":
                raise ValueError("main annotations must be strict TypedDict")
            required_inputs = {k for k, needed, _ in ins[1] if needed}
            input_names = {k for k, _, _ in ins[1]}
            if not required_inputs <= args.keys() or not args.keys() <= input_names:
                raise ValueError(f"arguments missing={sorted(required_inputs - args.keys())}, extra={sorted(args.keys()-input_names)}")
            for n in ast.walk(module):
                if isinstance(n, ast.Import) and any(x.name.split(".")[0] in BANNED_IMPORTS for x in n.names):
                    raise ValueError("forbidden external/ambient import")
                if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] in BANNED_IMPORTS:
                    raise ValueError("forbidden external/ambient import")
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in BANNED_CALLS:
                    raise ValueError("forbidden dynamic or external call")
            # Static return mapping minimum: reject extra/absent literal keys.
            out_fields = {k for k, _, _ in outs[1]}
            out_required = {k for k, need, _ in outs[1] if need}
            for n in ast.walk(main):
                if not isinstance(n, ast.Return) or not isinstance(n.value, ast.Dict):
                    continue
                literal = {key.value for key in n.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}
                if len(literal) != len(n.value.keys) or not out_required <= literal or not literal <= out_fields:
                    raise ValueError(f"return mapping not compatible with strict output TypedDict {main.returns.id}")
            models[node] = {"input": ins, "output": outs}
        except (SyntaxError, ValueError, TypeError) as exc:
            errors.append(f"{skill.name}/{node}: invalid v1alpha4 Script {script.name}: {exc}")

    for node, (_, args) in script_nodes.items():
        model = models.get(node)
        if model is None:
            continue
        input_fields = {k: typ for k, _, typ in model["input"][1]}
        for key, value in args.items():
            match = SOURCE.fullmatch(value)
            if not match or match[1] not in models:
                continue  # Owner/Context paths need trusted Compiler link; do not infer schemas.
            produced = _navigate(models[match[1]]["output"], match[2] or "")
            if produced is None:
                errors.append(f"{skill.name}/{node}: Script SourcePath missing: {value}")
            elif not _subtype(produced, input_fields[key]):
                errors.append(f"{skill.name}/{node}: INPUT_TYPE_MISMATCH for {key}: {value} incompatible with closed Script input")
