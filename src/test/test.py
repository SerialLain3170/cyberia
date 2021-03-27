import unittest
import sys
import os

from pathlib import Path
from apps.spotify import SpotifyManager
from fastapi.testclient import TestClient
from server import app

sp = SpotifyManager()
client = TestClient(app)


class SpotifyManagerTest(unittest.TestCase):
    def test_sp_setup(self):
        if sp is not None:
            print("SpotifyManager Setup")

    def test_search_invalid_id(self):
        _, code = sp.searchNearest("XXXXXX", num=50)
        assert code == "00001"

    def test_search_invalid_num(self):
        _, code = sp.searchNearest("XXXXXX", num="50")
        assert code == "00003"

    def test_search_toolong_num(self):
        _, code = sp.searchNearest("XXXXXX", num=100000)
        assert code == "00004"


class ServerTest(unittest.TestCase):
    def test_access(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_access_invalid_id(self):
        response = client.post("/search",
                               data={"trackid": "XXXXX", "num": 50})
        assert response.status_code == 200


if __name__ == "__main__":
    unittest.main()