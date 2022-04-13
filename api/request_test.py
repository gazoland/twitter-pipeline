import requests
import json

BASE = "http://127.0.0.1:5000/v1/"
# headers={"Content-type": "application/json"},


def test_get(resource):
    resp = requests.request("GET", url=BASE + resource)
    print(resp.json())


def test_post(resource):
    resp = requests.request("POST", url=BASE + resource, data={"usernames": "john,joe"})
    # resp = requests.post(BASE+resource, data={"username": "john"})
    print(resp.json())


if __name__ == "__main__":
    test_get("users")
    test_post("users")
