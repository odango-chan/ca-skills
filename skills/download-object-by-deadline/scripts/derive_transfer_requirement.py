# /// connectionagent-tool
# name: derive-transfer-requirement
# inputSchema: registry://schemas/transfer-requirement-input@v1
# outputSchema: registry://schemas/transfer-requirement-output@v1
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 2s
# ///


class TransferRequirementInputV1:
    pass


class TransferRequirementOutputV1:
    pass


def main(input: TransferRequirementInputV1) -> TransferRequirementOutputV1:
    bytes_remaining = input["bytesRemaining"]
    seconds_remaining = input["secondsRemaining"]

    if seconds_remaining <= 0:
        raise ValueError("secondsRemaining must be positive")
    if bytes_remaining < 0:
        raise ValueError("bytesRemaining must be non-negative")

    # Deterministic integer ceiling: ceil(bytes * 8 / seconds).
    numerator = bytes_remaining * 8
    minimum_payload_bitrate_bps = (
        numerator // seconds_remaining
        + (1 if numerator % seconds_remaining != 0 else 0)
    )
    return {"minimumPayloadBitrateBps": minimum_payload_bitrate_bps}
