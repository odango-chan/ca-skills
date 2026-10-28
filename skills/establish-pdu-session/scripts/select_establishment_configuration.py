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
    ambr = subscription.get("sessionAmbr")
    if type(ambr) is not dict or sorted(ambr.keys()) != ["downlink", "uplink"]:
        raise ValueError("subscribed session AMBR is unavailable or invalid")
    for direction in ("uplink", "downlink"):
        value = ambr[direction]
        if type(value) is not str or not value:
            raise ValueError("subscribed session AMBR is unavailable or invalid")
    qos = subscription.get("defaultQos")
    if type(qos) is not dict or sorted(qos.keys()) != ["arp", "fiveQi"]:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    if type(qos["fiveQi"]) is not int:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    if qos["fiveQi"] < 0 or qos["fiveQi"] > 255:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    arp = qos["arp"]
    if type(arp) is not dict or sorted(arp.keys()) != ["preemptCap", "preemptVuln", "priorityLevel"]:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    if type(arp["priorityLevel"]) is not int:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    if arp["priorityLevel"] < 1 or arp["priorityLevel"] > 15:
        raise ValueError("subscribed default QoS is unavailable or invalid")
    if arp["preemptCap"] not in ("MAY_PREEMPT", "NOT_PREEMPT") or arp["preemptVuln"] not in ("PREEMPTABLE", "NOT_PREEMPTABLE"):
        raise ValueError("subscribed default QoS is unavailable or invalid")
    return {
        "configuration": {
            "dnn": request["dnn"],
            "sNssai": dict(request["sNssai"]),
            "pduSessionType": "IPV4",
            "sscMode": 1,
        },
        "subscribedAmbr": dict(ambr),
        "subscribedDefaultQos": {
            "5qi": qos["fiveQi"],
            "arp": dict(arp),
        },
    }
