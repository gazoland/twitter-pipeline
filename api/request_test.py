import os
import requests

BASE = "http://127.0.0.1:5021/v1/"
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


def test_unexisting_route(resource):
    resp = requests.request("GET", url=BASE + resource, headers=headers)
    print(resp)
    print(resp.text)
    print(resp.json())


if __name__ == "__main__":
    test_get("users")
    test_post("users")
    test_delete("users")
    test_unexisting_route("fail")
