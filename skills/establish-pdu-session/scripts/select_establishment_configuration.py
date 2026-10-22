# /// connectionagent-tool
# name: select-establishment-configuration
# inputSchema: EstablishmentSelectionInput
# outputSchema: EstablishmentSelection
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

class EstablishmentSelectionInput(dict):
    pass

class EstablishmentSelection(dict):
    pass

def main(input: EstablishmentSelectionInput) -> EstablishmentSelection:
    request = input
    subscription = input["subscription"]
    if request["requestedPduSessionType"] != "IPV4" or type(request["requestedSscMode"]) is not int or request["requestedSscMode"] != 1:
        raise ValueError("unsupported explicitly decoded UE request")
    if subscription["dnn"] != request["dnn"] or subscription["sNssai"] != request["sNssai"]:
        raise ValueError("subscription scope mismatch")
    types = subscription["pduSessionTypes"]
    modes = subscription["sscModes"]
    allowed_types = types.get("allowedSessionTypes", [types["defaultSessionType"]])
    allowed_modes = modes.get("allowedSscModes", [modes["defaultSscMode"]])
    if "IPV4" not in allowed_types or 1 not in allowed_modes:
        raise ValueError("UE request is not permitted by subscription")
    return {"dnn": request["dnn"], "sNssai": dict(request["sNssai"]), "pduSessionType": "IPV4", "sscMode": 1}
