"""Repository-local CA-SL v1alpha4 example Script hygiene and local type check.

Not a Compiler or trusted Owner/Capability/Schema/Evidence validator.
The only assignability checked here is static local Script -> Script binding.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

TS_23_502_BASELINE = "TS 23.502 V19.9.0"
STAGE3_REQUIRED_BY_NODE = {
    "get-sm-subscription-data": ("TS 29.503 V19.7.0",),
    "subscribe-sm-data": ("TS 29.503 V19.7.0",),
    "establish-sm-policy-association": ("TS 29.512 V19.6.0",),
    "establish-n4-session": ("TS 29.244 V19.6.0",),
    "transfer-n1n2-message": ("TS 29.518 V19.8.0", "TS 29.571 V19.7.0"),
    "update-sm-context": ("TS 29.502 V19.7.0", "TS 29.571 V19.7.0"),
    "modify-n4-session": ("TS 29.244 V19.6.0",),
    "ensure-uecm-registration": ("TS 29.503 V19.7.0",),
    "validate-sm-subscription": ("TS 29.503 V19.7.0",),
    "create-sm-context": ("TS 29.502 V19.7.0", "TS 29.571 V19.7.0"),
    "register-uecm": ("TS 29.503 V19.7.0",),
    "modify-sm-policy-association": ("TS 29.512 V19.6.0",),
    "signal-ue-and-access-network": ("TS 29.518 V19.8.0", "TS 29.502 V19.7.0", "TS 29.571 V19.7.0"),
}

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

# v1alpha4 forbids author-level Wait/Await/Poll Nodes; Owner holdRef is only an opaque correlation handle.
def validate_3gpp_traceability(skill: Path, errors: list[str]) -> None:
    """Require every current 5GC Procedure Node to have a 3GPP/CA mapping."""
    procedure = skill / "assurance" / "procedure.yaml"
    skill_doc = skill / "SKILL.md"
    if not procedure.is_file() or not skill_doc.is_file():
        return  # Small isolated unit-test fixtures may omit the authoring document.
    procedure_text = procedure.read_text(encoding="utf-8")
    lines = procedure_text.splitlines()
    if "waiterRef:" in procedure_text:
        errors.append(f"{skill.name}: legacy waiterRef is not a v1alpha4 author field; use an Owner-defined holdRef if required")
    node_ids: list[str] = []
    for index, line in enumerate(lines):
        match = NODE.match(line)
        if not match:
            continue
        node = match[1]
        node_ids.append(node)
        if re.search(r"(?:^|[-_])(wait|await|poll)(?:$|[-_])", node, flags=re.IGNORECASE):
            errors.append(f"{skill.name}/{node}: author-level Wait/Await/Poll Nodes are forbidden in v1alpha4")
        previous = lines[index - 1] if index else ""
        if not previous.startswith("  # 3GPP: "):
            errors.append(f"{skill.name}/{node}: missing adjacent '# 3GPP:' mapping comment")
        elif not any(tag in previous for tag in
                     ("3GPP_NATIVE", "3GPP_LOCAL", "CA_ADAPTER", "CA_EXTENSION")):
            errors.append(f"{skill.name}/{node}: mapping comment lacks a valid classification")
        elif re.search(r"\b(?:steps?)\s*\d|Nudm_|Npcf_|Namf_|Nsmf_|N4 Session", previous, flags=re.IGNORECASE):
            if TS_23_502_BASELINE not in previous:
                errors.append(f"{skill.name}/{node}: 3GPP step/API mapping comment must pin {TS_23_502_BASELINE}")
        for stage3 in STAGE3_REQUIRED_BY_NODE.get(node, ()):
            if stage3 not in previous:
                errors.append(f"{skill.name}/{node}: mapping comment must pin {stage3}")

    doc = skill_doc.read_text(encoding="utf-8")
    if "## 3GPP Traceability" not in doc:
        errors.append(f"{skill.name}: missing '## 3GPP Traceability' table")
        return
    if TS_23_502_BASELINE not in doc:
        errors.append(f"{skill.name}: 3GPP reference version is not pinned")
    documented = set(re.findall(r"^\|\s*\x60([A-Za-z][A-Za-z0-9_-]*)\x60\s*\|",
                                doc, flags=re.MULTILINE))
    expected = set(node_ids)
    for node in sorted(expected - documented):
        errors.append(f"{skill.name}/{node}: missing SKILL.md 3GPP traceability row")
    for node in sorted(documented - expected):
        errors.append(f"{skill.name}/{node}: traceability row has no Procedure Node")


def validate_host_context_separation(skill: Path, errors: list[str]) -> None:
    """Keep Host execution metadata outside the two current 5GC Skill graphs."""
    if skill.name not in {"establish-pdu-session", "establish-pdu-session-mas"}:
        return
    procedure = skill / "assurance" / "procedure.yaml"
    contract = skill / "assurance" / "contract.yaml"
    if not procedure.is_file() or not contract.is_file():
        return
    procedure_text = procedure.read_text(encoding="utf-8")
    contract_text = contract.read_text(encoding="utf-8")

    forbidden = (
        (r"\bcontext\.(?:ingress|lifecycle|correlation)\b", "Host ingress/lifecycle/correlation context"),
        (r"(?m)^\s*(?:ingressRef|lifecycleRef|currentInstanceRef|instanceId|invocationId|holdRef|claimRef|waiterRef|journalRef)\s*:", "Host dispatch metadata"),
    )
    for pattern, label in forbidden:
        if re.search(pattern, procedure_text):
            errors.append(f"{skill.name}: {label} must not be a Skill Procedure input")

    if re.search(r"(?m)^  admit-create-sm-context-request:\s*$", procedure_text):
        errors.append(f"{skill.name}: Host ingress admission must not be an authored Procedure Node")

    start = re.search(r"(?m)^start:\s*([A-Za-z][A-Za-z0-9_-]*)\s*$", procedure_text)
    precondition = re.search(r"(?m)^precondition:\s*([A-Za-z][A-Za-z0-9_-]*)\.precondition\s*$", contract_text)
    if not start or not precondition or start.group(1) != precondition.group(1):
        errors.append(f"{skill.name}: the business request-profile global Precondition must be attached to the first business Node")

    context_schema = re.search(r"(?m)^contextSchema:\s*(\S+)\s*$", contract_text)
    if not context_schema or context_schema.group(1) != "ca-context::urn:connectionagent:ca:context:subject:v1":
        errors.append(f"{skill.name}: Skill Host Context must use the subject-only contextSchema")


def validate_pcf_owner_boundary(skill: Path, errors: list[str]) -> None:
    """Keep PCF request preparation, profile gates and association handles inside the Owner."""
    if skill.name != "establish-pdu-session":
        return
    procedure = skill / "assurance" / "procedure.yaml"
    predicates = skill / "assurance" / "predicates.yaml"
    if not procedure.is_file() or not predicates.is_file():
        return
    procedure_text = procedure.read_text(encoding="utf-8")
    predicate_text = predicates.read_text(encoding="utf-8")
    if "build-sm-policy-association-inputs" in procedure_text or "scripts/build-pcf-policy-inputs.py" in procedure_text:
        errors.append(f"{skill.name}: PCF request-only preparation must not be a separate Skill Node or Script")
    if (skill / "scripts" / "build-pcf-policy-inputs.py").exists():
        errors.append(f"{skill.name}: obsolete PCF input-builder Script must be removed")
    node = re.search(r"(?ms)^  establish-sm-policy-association:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not node:
        errors.append(f"{skill.name}: missing establish-sm-policy-association business Node")
    else:
        block = node.group(1)
        if not re.search(r"(?m)^      tool: ca::sbi\.pcf\.sm_policy\.create\s*$", block):
            errors.append(f"{skill.name}: Step 7b must be the PCF Create Owner Operation")
        if not re.search(r"(?m)^        udmReadResult: get-sm-subscription-data\.operation\.output\.result\s*$", block):
            errors.append(f"{skill.name}: PCF Owner must consume the validated UDM read result directly")
        if re.search(r"(?m)^\s*(?:policyInputs|sdmSubscriptionRef|subscriptionRef|policyAssociationRef|policyResultRef):", block):
            errors.append(f"{skill.name}: PCF request data and association handles must remain Owner-managed")
    predicate = re.search(r"(?ms)^  establishment\.pcf\.association_owned:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_.-]*:\s*$|\Z)", predicate_text)
    if not predicate:
        errors.append(f"{skill.name}: missing establishment.pcf.association_owned business Postcondition")
    else:
        block = predicate.group(1)
        if re.search(r"(?m)^\s*(?:- )?inputs:", block) or "create-inputs-current" in block:
            errors.append(f"{skill.name}: PCF input-readiness Evidence must remain internal to the PCF Owner")
        if "association.profile.secondaryAuthenticationRequired == false" not in block:
            errors.append(f"{skill.name}: PCF association Evidence must prove the Step 6 no-secondary-auth profile gate")
        if "association.profile.step9ModificationRequired == false" not in block:
            errors.append(f"{skill.name}: PCF association Evidence must prove the Step 9 no-trigger profile gate")


def validate_n4_owner_boundary(skill: Path, errors: list[str]) -> None:
    """Keep native Step 8 selection inside the single public SMF N4 Owner interaction."""
    if skill.name != "establish-pdu-session":
        return
    procedure = skill / "assurance" / "procedure.yaml"
    predicates = skill / "assurance" / "predicates.yaml"
    skill_doc = skill / "SKILL.md"
    if not procedure.is_file() or not predicates.is_file() or not skill_doc.is_file():
        return
    procedure_text = procedure.read_text(encoding="utf-8")
    predicate_text = predicates.read_text(encoding="utf-8")
    skill_text = skill_doc.read_text(encoding="utf-8")
    if "select-session-configuration" in procedure_text or "scripts/select-establishment-configuration.py" in procedure_text:
        errors.append(f"{skill.name}: Step 8 native selection must not be a separate Procedure Node or Operation Script")
    if (skill / "scripts" / "select-establishment-configuration.py").exists():
        errors.append(f"{skill.name}: obsolete Step 8 selection Script must be removed")
    n4 = re.search(r"(?ms)^  establish-n4-session:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not n4:
        errors.append(f"{skill.name}: missing establish-n4-session business Node")
    else:
        block = n4.group(1)
        if not re.search(r"(?m)^      tool: smf::n4\.session\.establish\s*$", block):
            errors.append(f"{skill.name}: Step 8 and N4 must use the public SMF N4 Owner Operation")
        if not re.search(r"(?m)^        request: context\.request\s*$", block):
            errors.append(f"{skill.name}: SMF N4 Owner must receive the admitted request for native Step 8 selection")
        if not re.search(r"(?m)^        udmReadResult: get-sm-subscription-data\.operation\.output\.result\s*$", block):
            errors.append(f"{skill.name}: SMF N4 Owner must receive the validated UDM subscription result")
        if not re.search(r"(?m)^        policyResult: establish-sm-policy-association\.operation\.output\.policyResult\s*$", block):
            errors.append(f"{skill.name}: SMF N4 Owner must receive normalized PCF policy data")
        if re.search(r"(?m)^\s*(?:selection|policyAssociationRef|policyResultRef):", block):
            errors.append(f"{skill.name}: SMF N4 Owner must not receive a Skill-generated selection or Owner handle")
    transfer = re.search(r"(?ms)^  transfer-n1n2-message:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not transfer:
        errors.append(f"{skill.name}: missing transfer-n1n2-message business Node")
    else:
        block = transfer.group(1)
        if re.search(r"(?m)^\s*selection:", block):
            errors.append(f"{skill.name}: N1/N2 must not consume a separate Step 8 Script payload")
        if not re.search(r"(?m)^        initialN4Result: establish-n4-session\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: N1/N2 must consume the effective configuration from the N4 Owner result")
    n4_predicate = re.search(r"(?ms)^  establishment\.n4\.initial_resources_ready:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_.-]*:\s*$|\Z)", predicate_text)
    if not n4_predicate or not all(field in n4_predicate.group(1) for field in ("allocatedIpv4", "selectedPduSessionType", "selectedSscMode", "sessionConfigurationDigest")):
        errors.append(f"{skill.name}: N4 initial-resource Predicate must verify allocated IPv4, selected profile and configuration digest")
    if "establishment.subscription.request_valid:" not in predicate_text:
        errors.append(f"{skill.name}: missing Step 4 subscription/request compatibility Predicate")
    if "script: scripts/validate-subscription-request.py" not in predicate_text:
        errors.append(f"{skill.name}: subscription compatibility must use a Step 4 Predicate Script")
    if not re.search(r"(?m)^\| \x60establish-n4-session\x60 \| .*step 8 .*steps 10a–10b;.*\| `CA_ADAPTER`: SMF N4 Owner", skill_text):
        errors.append(f"{skill.name}: SKILL.md must map Step 8 to the SMF N4 Owner boundary")


def validate_async_update_sm_context_boundary(skill: Path, errors: list[str]) -> None:
    """Enforce the public SMF service boundary and co-locate the two SMF context reads."""
    if skill.name != "establish-pdu-session":
        return
    procedure = skill / "assurance" / "procedure.yaml"
    predicates = skill / "assurance" / "predicates.yaml"
    contract = skill / "assurance" / "contract.yaml"
    skill_doc = skill / "SKILL.md"
    if not all(path.is_file() for path in (procedure, predicates, contract, skill_doc)):
        return
    procedure_text = procedure.read_text(encoding="utf-8")
    predicate_text = predicates.read_text(encoding="utf-8")
    contract_text = contract.read_text(encoding="utf-8")
    skill_text = skill_doc.read_text(encoding="utf-8")
    public_source = procedure_text + "\n" + contract_text + "\n" + skill_text
    if re.search(r"(?i)\bMAS\b|smf[-.]mas|ca-observations|openamsm|upn::|ssm::|\bUPN\b|\bSSM\b", public_source):
        errors.append(f"{skill.name}: conventional Skill files must not declare or mention MAS implementation details or OpenAMSM internal module names")
    if re.search(r"(?m)^\s*(?:ingressRef|lifecycleRef|transferOperationRef|udmInvocationRef|udmTransactionRef|sdmSubscriptionRef|subscriptionRef|policyAssociationRef|policyResultRef|operationContextRef|responseArtifactRef|holdRef|waiterRef|claimRef|journalRef):", procedure_text):
        errors.append(f"{skill.name}: Host ingress, lifecycle and transport response metadata or Owner handles must remain private")
    node_blocks = [
        (match.group(1), match.group(2))
        for match in re.finditer(r"(?ms)^  ([A-Za-z][A-Za-z0-9_-]*):\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    ]
    for node_id, block in node_blocks:
        if re.search(r"(?m)^    observation:\s*$", block):
            operation_pos = block.find("    operation:")
            observation_pos = block.find("    observation:")
            postcondition_pos = block.find("    postcondition:")
            if operation_pos < 0:
                errors.append(f"{skill.name}/{node_id}: standalone Observation-only Node is forbidden for this Skill")
            elif not (operation_pos < observation_pos < postcondition_pos):
                errors.append(f"{skill.name}/{node_id}: Observation must follow the primary Operation and precede Postcondition")
    if "establishment.smf.session_context_absent:" not in predicate_text:
        errors.append(f"{skill.name}: missing the explicit SM Context ABSENT Predicate")
    if "script: scripts/validate-smf-session-context-entry.py" not in predicate_text:
        errors.append(f"{skill.name}: missing the entry-time context-presence Predicate Script")
    entry_script = skill / "scripts" / "validate-smf-session-context-entry.py"
    if not entry_script.is_file():
        errors.append(f"{skill.name}: missing the entry-time context-presence Predicate Script")
    else:
        entry_script_text = entry_script.read_text(encoding="utf-8")
        if not all(token in entry_script_text for token in ('"ABSENT"', '"PRESENT"', '"SESSION_NOT_FOUND"', '"NOT_APPLICABLE"')):
            errors.append(f"{skill.name}: entry Predicate must distinguish evidenced ABSENT from PRESENT and malformed results")
        if "SMF_SESSION_CONTEXT_CONFIRMED_ABSENT" not in entry_script_text:
            errors.append(f"{skill.name}: ABSENT must be an explicit business outcome, not generic query success")
    update = re.search(r"(?ms)^  update-sm-context:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not update:
        errors.append(f"{skill.name}: missing step-15 update-sm-context continuation Node")
    else:
        block = update.group(1)
        if not re.search(r"(?m)^      tool: smf::nsmf\.pdu_session\.update_sm_context\s*$", block):
            errors.append(f"{skill.name}: update-sm-context must use the public SMF UpdateSMContext Owner Operation")
        if re.search(r"(?m)^\s*transferOperationRef:", block):
            errors.append(f"{skill.name}: Step 15 transfer correlation must remain Host/Owner-private")
        if not re.search(r"(?m)^      tool: ca-session-context::context\.smf\.session\.read\s*$", block):
            errors.append(f"{skill.name}: fresh post-Step-15 Observation must be co-located in update-sm-context")
        if not re.search(r"(?m)^        supi: context\.supi\s*$", block) or not re.search(r"(?m)^        pduSessionId: context\.request\.pduSessionId\s*$", block):
            errors.append(f"{skill.name}: post-Step-15 Observation must be scoped by exact UE and PDU Session ID")
        if not re.search(r"(?m)^            - update-sm-context\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: RAN adoption Predicate must consume the UpdateSMContext Operation Result")
        if not re.search(r"(?m)^            - update-sm-context\.observation\.output\s*$", block):
            errors.append(f"{skill.name}: context profile Predicate must consume the co-located Observation Result")
        if not re.search(r"(?m)^        PASS: modify-n4-session\s*$", block):
            errors.append(f"{skill.name}: only a passing post-Step-15 context decision may advance to N4 Modification")
        stage_positions = [block.find("    operation:"), block.find("    observation:"), block.find("    postcondition:")]
        if any(position < 0 for position in stage_positions) or stage_positions != sorted(stage_positions):
            errors.append(f"{skill.name}: post-Step-15 Observation must follow the asynchronous Operation and precede Postcondition")
    transfer = re.search(r"(?ms)^  transfer-n1n2-message:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not transfer or not re.search(r"(?m)^        PASS: update-sm-context\s*$", transfer.group(1)):
        errors.append(f"{skill.name}: N1/N2 transfer success must continue to the pending UpdateSMContext Operation")
    if "establishment.smf.session_context_profile_ready:" not in predicate_text:
        errors.append(f"{skill.name}: missing the SMF session-context business Predicate")
    post_script = skill / "scripts" / "validate-smf-session-context.py"
    if not post_script.is_file():
        errors.append(f"{skill.name}: missing the post-Step-15 SMF context Predicate Script")
    else:
        post_script_text = post_script.read_text(encoding="utf-8")
        for token in ("sessionPresence", "projectionStatus", "sourceOutcome", '"uecmRegistered"'):
            if token not in post_script_text:
                errors.append(f"{skill.name}: post-Step-15 Predicate must validate {token}")
    if "sessionContext: ca-session-context::urn:connectionagent:ca:observation:smf-session-context-read-result:v1" not in predicate_text:
        errors.append(f"{skill.name}: SMF session-context Predicate must use the generic context result Schema")
    if "sessionContext: [ca-session-context::smf.session-context.read-evidence]" not in predicate_text:
        errors.append(f"{skill.name}: SMF session-context Predicate must require its declared read Evidence")
    if "script: scripts/validate-smf-session-context.py" not in predicate_text:
        errors.append(f"{skill.name}: missing the three-state SMF session-context Predicate Script")
    if "urn:example:connectionagent:capability:ca:smf-session-context-read:v1" not in contract_text or "ca-session-context: urn:connectionagent:ca:host:smf-session-context" not in contract_text:
        errors.append(f"{skill.name}: Skill must declare the generic read-only SMF session-context Capability")
    if not re.search(r"(?m)^  smf: urn:example:connectionagent:smf-tool-contracts\s*$", contract_text):
        errors.append(f"{skill.name}: Skill must declare the generic SMF business Tool dependency")
    modify = re.search(r"(?ms)^  modify-n4-session:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not modify:
        errors.append(f"{skill.name}: missing the SMF N4 Session Modification business Node")
    else:
        block = modify.group(1)
        if not re.search(r"(?m)^      tool: smf::n4\.session\.modify\s*$", block):
            errors.append(f"{skill.name}: N4 Session Modification must use the public SMF N4 Owner Operation")
        if not re.search(r"(?m)^        initialN4Result: establish-n4-session\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: N4 Modification must consume the initial N4 Owner result")
        if not re.search(r"(?m)^        ranResult: update-sm-context\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: N4 Modification must consume the validated UpdateSMContext/RAN result")
        if not re.search(r"(?m)^            - modify-n4-session\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: N4 forwarding Predicate must consume the N4 Modification result")
    ensure = re.search(r"(?ms)^  ensure-uecm-registration:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not ensure:
        errors.append(f"{skill.name}: missing the Step 16c UECM Registration business Node")
    else:
        block = ensure.group(1)
        if not re.search(r"(?m)^      tool: ca::sbi\.udm\.uecm\.register\s*$", block):
            errors.append(f"{skill.name}: Step 16c must use the UDM UECM Registration Tool")
        if not re.search(r"(?m)^        uecmRegistered: update-sm-context\.observation\.output\.context\.uecmRegistered\s*$", block):
            errors.append(f"{skill.name}: Step 16c must consume the fresh SMF UECM registration state")
        if not re.search(r"(?m)^        udmReadResult: get-sm-subscription-data\.operation\.output\.result\s*$", block):
            errors.append(f"{skill.name}: Step 16c must consume the validated UDM subscription result")
        if not re.search(r"(?m)^            - ensure-uecm-registration\.operation\.output\s*$", block):
            errors.append(f"{skill.name}: Step 16c Postcondition must consume its own Operation Result")
        if not re.search(r"(?m)^        PASS: verify-pdu-session-establishment\s*$", block):
            errors.append(f"{skill.name}: Step 16c success must continue to the final Goal proof")
    verify = re.search(r"(?ms)^  verify-pdu-session-establishment:\n(.*?)(?=^  [A-Za-z][A-Za-z0-9_-]*:\s*$|\Z)", procedure_text)
    if not verify:
        errors.append(f"{skill.name}: missing final verify-pdu-session-establishment Goal Node")
    else:
        block = verify.group(1)
        for source in ("transfer-n1n2-message.operation.output", "establish-n4-session.operation.output", "update-sm-context.operation.output", "modify-n4-session.operation.output", "ensure-uecm-registration.operation.output"):
            if not re.search(rf"(?m)^\s+- {re.escape(source)}\s*$", block):
                errors.append(f"{skill.name}: final Goal proof must consume {source}")
    if re.search(r"(?m)^  ca-transfer-(?:failed-)?resource-responsibility:\s*$", procedure_text):
        errors.append(f"{skill.name}: resource responsibility is a Host/Runtime finalizer, not a Skill Node")
    if "establishment.resources.managed:" in predicate_text:
        errors.append(f"{skill.name}: resource responsibility must not be modeled as a Skill business Predicate")
    for note in ("Step 17 reject response", "Step 18 SM Context Status Notify", "Step 21 unsubscribe", "SAFE_STOPPED preserves responsibility"):
        if note not in procedure_text:
            errors.append(f"{skill.name}: comment-only failure handling must document {note}")
    if not re.search(r"(?m)^\| \x60get-sm-subscription-data\x60 \| .*step 4 .*SM Context presence read before any mutation", skill_text):
        errors.append(f"{skill.name}: SKILL.md must trace the Step 4 Node and its entry context Observation")
    if not re.search(r"(?m)^\| \x60update-sm-context\x60 \| .*step 15 .*fresh SM Context read", skill_text):
        errors.append(f"{skill.name}: SKILL.md must trace update-sm-context to step 15 and its co-located Observation")
    if not re.search(r"(?m)^\| \x60modify-n4-session\x60 \| .*steps 16a–16b;.*\| `CA_ADAPTER`: SMF N4 Owner", skill_text):
        errors.append(f"{skill.name}: SKILL.md must trace N4 Modification to the SMF N4 Owner Operation")
    if not re.search(r"(?m)^\| \x60ensure-uecm-registration\x60 \| .*step 16c .*Nudm_UECM_Registration", skill_text):
        errors.append(f"{skill.name}: SKILL.md must trace Step 16c UECM Registration")
    if "resumes the same Invocation" not in skill_text or "paired Step 17" not in skill_text:
        errors.append(f"{skill.name}: SKILL.md must define same-Invocation resume and paired Step 17 Host response")
    if "Host/Runtime performs the terminal resource-responsibility finalizer" not in skill_text:
        errors.append(f"{skill.name}: SKILL.md must keep terminal resource responsibility in the Host/Runtime finalizer")


def validate_predicate_scripts(skill: Path, errors: list[str]) -> set[Path]:
    """Validate local Predicate Script refs and their generated-result contract."""
    predicates = skill / "assurance" / "predicates.yaml"
    if not predicates.is_file():
        return set()
    refs: list[tuple[str, Path]] = []
    for line in predicates.read_text(encoding="utf-8").splitlines():
        match = SCRIPT.match(line)
        if not match:
            continue
        ref = match[1]
        if not re.fullmatch(r"scripts/[A-Za-z0-9_-]+\.py", ref) or "/" in ref[8:]:
            errors.append(f"{skill.name}: unsafe Predicate Script ref {ref}")
            continue
        refs.append((f"predicate-script-{len(refs) + 1}", skill / ref))

    referenced: set[Path] = set()
    for predicate, script in refs:
        referenced.add(script.resolve())
        if not script.is_file():
            errors.append(f"{skill.name}/{predicate}: Predicate Script not found {script.relative_to(skill)}")
            continue
        try:
            module = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            defs = _fields(module)
            mains = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "main"]
            if len(mains) != 1 or not isinstance(mains[0], ast.FunctionDef):
                raise ValueError("exactly one synchronous main required")
            main = mains[0]
            if (len(main.args.args) != 1 or main.args.args[0].arg != "input"
                or main.args.vararg or main.args.kwarg or main.args.defaults
                or main.args.kwonlyargs or main.args.posonlyargs or main.returns is None):
                raise ValueError("main(input: PredicateInput) -> PredicateEvaluationResult required")
            if (not isinstance(main.args.args[0].annotation, ast.Name)
                or main.args.args[0].annotation.id != "PredicateInput"
                or not isinstance(main.returns, ast.Name)
                or main.returns.id != "PredicateEvaluationResult"):
                raise ValueError("main signature must use generated PredicateInput and strict PredicateEvaluationResult")
            output = _schema(main.returns, defs)
            if output[0] != "object":
                raise ValueError("PredicateEvaluationResult must be a strict TypedDict")
            fields = {name for name, _, _ in output[1]}
            required = {name for name, needed, _ in output[1] if needed}
            expected = {"result", "reasonCode", "evidenceUsed"}
            if fields != expected or required != expected:
                raise ValueError(f"PredicateEvaluationResult fields must be exactly {sorted(expected)}")
            for node in ast.walk(module):
                if isinstance(node, ast.Import) and any(x.name.split(".")[0] in BANNED_IMPORTS for x in node.names):
                    raise ValueError("forbidden external/ambient import")
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in BANNED_IMPORTS:
                    raise ValueError("forbidden external/ambient import")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
                    raise ValueError("forbidden dynamic or external call")
            for node in ast.walk(main):
                if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
                    continue
                literal = {key.value for key in node.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}
                if literal != expected or len(literal) != len(node.value.keys):
                    raise ValueError("every Predicate Script return must provide exactly result, reasonCode and evidenceUsed")
        except (SyntaxError, ValueError, TypeError) as exc:
            errors.append(f"{skill.name}/{predicate}: invalid Predicate Script {script.name}: {exc}")
    return referenced


def validate_example_scripts(skill: Path, errors: list[str]) -> None:
    validate_3gpp_traceability(skill, errors)
    validate_host_context_separation(skill, errors)
    validate_pcf_owner_boundary(skill, errors)
    validate_n4_owner_boundary(skill, errors)
    validate_async_update_sm_context_boundary(skill, errors)
    predicate_script_refs = validate_predicate_scripts(skill, errors)
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

    referenced = {p.resolve() for p, _ in script_nodes.values()} | predicate_script_refs
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
