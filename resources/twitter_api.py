import requests
import os

BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")


def bearer_oauth(r):
    """Method required by bearer token authentication."""

    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    """Sends GET request to specified url."""
    response = requests.request("GET", url, auth=bearer_oauth,)
    print(f"Request response code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
