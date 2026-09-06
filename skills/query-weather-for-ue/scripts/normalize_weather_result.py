# /// connectionagent-tool
# name: normalize-weather-result
# inputSchema: registry://schemas/external-weather-raw-result@v1
# outputSchema: WeatherResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 2s
# ///


class ExternalWeatherRawResultV1(dict):
    pass


class WeatherResult(dict):
    pass


def main(input: ExternalWeatherRawResultV1) -> WeatherResult:
    city = input["city"].strip()
    temperature = float(input["temperature"])
    condition = input["condition"].strip()

    if not city:
        raise ValueError("city must not be empty")
    if not condition:
        raise ValueError("condition must not be empty")
    if temperature != temperature or temperature == float("inf") or temperature == float("-inf"):
        raise ValueError("temperature must be finite")

    return {
        "city": city,
        "temperature": temperature,
        "condition": condition,
    }
