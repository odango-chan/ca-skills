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
    allowed_types = types.get("allowedSessionTypes")
    if allowed_types is None:
        allowed_types = [types["defaultSessionType"]]
    allowed_modes = modes.get("allowedSscModes")
    if allowed_modes is None:
        allowed_modes = [modes["defaultSscMode"]]
    if type(allowed_types) is not list or not allowed_types:
        raise ValueError("invalid subscribed PDU session type set")
    for value in allowed_types:
        if type(value) is not str:
            raise ValueError("invalid subscribed PDU session type set")
        if value != "IPV4" and value != "IPV6" and value != "IPV4V6":
            raise ValueError("unsupported subscribed PDU session type")
    if type(allowed_modes) is not list or not allowed_modes:
        raise ValueError("invalid subscribed SSC mode set")
    for value in allowed_modes:
        if type(value) is not int:
            raise ValueError("invalid subscribed SSC mode set")
        if value != 1 and value != 2 and value != 3:
            raise ValueError("unsupported subscribed SSC mode")
    if "IPV4" not in allowed_types or 1 not in allowed_modes:
        raise ValueError("UE request is not permitted by subscription")
    return {"dnn": request["dnn"], "sNssai": dict(request["sNssai"]), "pduSessionType": "IPV4", "sscMode": 1}
