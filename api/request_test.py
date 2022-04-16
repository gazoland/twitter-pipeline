import os

import requests
import json

BASE = "http://127.0.0.1:5000/v1/"
# headers={"Content-type": "application/json"},
API_TOKEN = os.environ.get("API_TOKEN")
headers = {"Accept": "application/json",
           "Authorization": f"Bearer {API_TOKEN}"}


def test_get(resource):
    resp = requests.request("GET", url=BASE + resource, headers=headers)
    print(resp.json())
    print(resp)


def test_post(resource):
    resp = requests.request("POST", url=BASE + resource, headers=headers, data={"usernames": "joe,neil,john,liam"})
    print(resp.json())
    print(resp)


def test_delete(resource):
    resp = requests.request("DELETE", url=BASE + resource, headers=headers, data={"usernames": "john,liam,joe,neil"})
    print(resp.json())
    print(resp)


if __name__ == "__main__":
    test_get("users")
    test_post("users")
    test_delete("users")
