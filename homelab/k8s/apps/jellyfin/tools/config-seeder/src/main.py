import json
import requests

if __name__ == "__main__":
    with open("dev/dump/jellyfin.har.json", "r") as fptr:
        jellyfin = json.load(fptr)

    # print(jellyfin["log"]["entries"][0].keys())

    for entry in jellyfin["log"]["entries"]:
        # print(entry)
        request = entry["request"]
        print(
            f"""{request['httpVersion']} {request['method']} {request['url']}

        """
        )
