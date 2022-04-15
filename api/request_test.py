import requests
import json

BASE = "http://127.0.0.1:5000/v1/"
# headers={"Content-type": "application/json"},


def test_get(resource):
    resp = requests.request("GET", url=BASE + resource)
    print(resp.json())


def test_post(resource):
    resp = requests.request("POST", url=BASE + resource, data={"usernames": "joe,neil,john,liam"})
    # resp = requests.post(BASE+resource, data={"username": "john"})
    print(resp.json())


def test_delete(resource):
    resp = requests.request("DELETE", url=BASE + resource, data={"usernames": "john,liam,joe,neil"})
    print(resp.json())


if __name__ == "__main__":
    test_get("users")
    test_post("users")
    test_delete("users")
