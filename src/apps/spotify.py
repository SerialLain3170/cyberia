import spotipy
import os
import yaml
import json
import pprint
import requests
import time
import random
import numpy as np

from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import util
from pathlib import Path
from typing import List, Dict, Union, Optional
from apps.db import DB
from apps.utils import norm, cosine_sim
from apps.code import num_check


class SpotifyManager:
    def __init__(self):
        self.wavdir, self.imgdir, self.sp = self._setup()
        self.db = DB()
        self.stat_dict = self._statistics()
        self.src_dict = self._getVector(self.stat_dict)

    @staticmethod
    def _setup() -> (Path, Path, spotipy.Spotify):        
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        username = os.environ.get("SPOTIFY_USERNAME")
        redirect_url = os.environ.get("SPOTIFY_REDIRECT_URL")
        scope = "user-library-read user-read-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private"

        manager = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_url)
        sp = spotipy.Spotify(auth=manager)

        wavdir = Path("wavdir")
        imgdir = Path("imgdir")
        wavdir.mkdir(exist_ok=True)
        imgdir.mkdir(exist_ok=True)

        return wavdir, imgdir, sp

    def _statistics(self) -> Dict[str, float]:
        """calculate statistics of data in DB.
           They are used for normalization with respect ot loudness and tempo.

        Returns:
            Dict[str, float]:
            keys
              - loud_max: maximum of loudness
              - loud_min: minimum of loudness
              - tempo_max: maximum of tempo
              - tempo_min: minimum of tempo
        """

        loud_list = []
        tempo_list = []
        rows = self.db.select()

        for row in rows:
            loud_list.append(row[13])
            tempo_list.append(row[18])

        stat_dict = {}
        stat_dict["loud_max"] = max(loud_list)
        stat_dict["loud_min"] = min(loud_list)
        stat_dict["tempo_max"] = max(tempo_list)
        stat_dict["tempo_min"] = min(tempo_list)

        return stat_dict

    def _getVector(self, stat_dict: Dict[str, float]):
        """calculate vector for each song in DB

        Args:
            stat_dict (Dict[str, float]): gotten in self._statistics()

        Returns:
            Dict[str, (List[float], str, str, str)]
            key
              - The name of each song
            value
              - Feature vector
              - Album name including each song
              - External URL for each song
              - ID for each song
        """

        rows = self.db.select()
        src_dict = {}

        for row in rows:
            vector = []
            vector.append(row[8])
            vector.append(row[9])
            vector.append(row[10])
            vector.append(row[11])
            vector.append(row[12])
            vector.append(row[14])
            vector.append(row[15])
            vector.append(norm(row[13], stat_dict["loud_max"], stat_dict["loud_min"]))
            vector.append(norm(row[18], stat_dict["tempo_max"], stat_dict["tempo_min"]))

            src_dict[row[4]] = [vector, row[2], row[1], row[0]]

        return src_dict

    def _getTrack(self, id: str, search=False):
        try:
            meta = self.sp.track(id)
            features = self.sp.audio_features(id)[0]
        except Exception:
            return None, "00001"

        if features is None or meta is None:
            return None, "00002"

        def mp3save(meta: dict, wavdir) -> dict:
            preview_url = meta["preview_url"]

            if preview_url is not None:
                songname = meta["name"].replace(" ", "_")
                response = requests.get(preview_url)
                with open(str(self.wavdir / Path(f"{songname}.mp3")), "wb") as f:
                    f.write(response.content)

        songdict = {}
        songdict["id"] = meta["id"]
        songdict["url"] = meta["external_urls"]["spotify"]
        songdict["albumname"] = meta["album"]["name"]
        songdict["album_artist"] = meta["album"]["artists"][0]["name"]
        songdict["songname"] = meta["name"]
        songdict["artist"] = meta["artists"][0]["name"]
        songdict["duration_ms"] = meta["duration_ms"]
        songdict["popularity"] = meta["popularity"]
        songdict["acousticness"] = features["acousticness"]
        songdict["danceability"] = features["danceability"]
        songdict["energy"] = features["energy"]
        songdict["instrumentalness"] = features["instrumentalness"]
        songdict["liveness"] = features["liveness"]
        songdict["loudness"] = features["loudness"]
        songdict["valence"] = features["valence"]
        songdict["speechiness"] = features["speechiness"]
        songdict["key"] = features["key"]
        songdict["mode"] = features["mode"]
        songdict["tempo"] = features["tempo"]
        songdict["time_signature"] = features["time_signature"]
        #mp3save(meta, self.wavdir)

        if not search:
            self.db.insert(songdict)

        return songdict, None

    def extractSongsByArtists(self, artists: List[str]):
        for artist in artists:
            pprint.pprint(artist)
            offset = 0
            while True:
                albums = self.sp.artist_albums(artist,
                                               album_type="album",
                                               limit=50,
                                               offset=offset)

                for album in albums["items"]:
                    if "JP" not in album["available_markets"]:
                        continue
                    off = 0
                    while True:
                        time.sleep(2)
                        suminfos = self.sp.album_tracks(album["id"], limit=50, offset=off)
                        pprint.pprint(suminfos)
                        for info in suminfos["items"]:
                            judge = self._getTrack(info["id"])

                            if judge is None:
                                continue

                        off += 50

                        if suminfos["next"] is None:
                            break

                offset += 50
                if albums["next"] is None:
                    break

    def extractSongsByAlbums(self, album_ids: List[str]):
        for album in album_ids:
            offset = 0
            while True:
                time.sleep(2)
                suminfos = self.sp.album_tracks(album, limit=50, offset=offset)
                pprint.pprint(suminfos)
                for info in suminfos["items"]:
                    judge = self._getTrack(info["id"])

                    if judge is None:
                        continue

                offset += 50

                if suminfos["next"] is None:
                    break

    def makePlaylist(self, sorted_dict, playlist_name: str):
        def createTrackidList(sorted_dict):
            idlist = []
            for k, v in sorted_dict:
                idlist.append(v[3])
            return idlist
        user_id = self.sp.current_user()['id']

        results = self.sp.user_playlist_create(user_id,
                                               playlist_name,
                                               public=True)
        track_id_list = createTrackidList(sorted_dict)
        self.sp.user_playlist_add_tracks(user_id,
                                         results['id'],
                                         track_id_list)
        
        return results["external_urls"]["spotify"]

    def randomChoose(self, num: int) -> (Optional[str], Optional[str]):
        judge, c = num_check(num)

        if judge is None:
            return None, c

        random_dict = random.sample(list(self.src_dict.items()), num)
        pprint.pprint(random_dict)
        playlist_name = "RandomlyChosenSongs"

        playlist_url = self.makePlaylist(random_dict, playlist_name)

        return playlist_url, None
        
    def searchNearest(self, track_id: str, num: int) -> (Optional[str], Optional[str]):
        judge, c = num_check(num)

        if judge is None:
            return None, c

        target_dict, c = self._getTrack(track_id, True)

        if target_dict is None:
            return None, c

        target_vector = []
        target_vector.append(target_dict["acousticness"])
        target_vector.append(target_dict["danceability"])
        target_vector.append(target_dict["energy"])
        target_vector.append(target_dict["instrumentalness"])
        target_vector.append(target_dict["liveness"])
        target_vector.append(target_dict["valence"])
        target_vector.append(target_dict["speechiness"])
        target_vector.append(norm(target_dict["loudness"], self.stat_dict["loud_max"], self.stat_dict["loud_min"]))
        target_vector.append(norm(target_dict["tempo"], self.stat_dict["tempo_max"], self.stat_dict["tempo_min"]))

        dist_dict = {}

        for k, v in self.src_dict.items():
            sim = cosine_sim(v[0], target_vector)
            dist_dict[k] = [sim, v[1], v[2], v[3]]

        sorted_dict = sorted(dist_dict.items(), key=lambda x:x[1][0])
        results = sorted_dict[::-1][:num]

        pprint.pprint(results)

        songname = target_dict["songname"]
        playlist_name = f"{songname}RelatedSongs"
        playlist_url = self.makePlaylist(results, playlist_name)

        return playlist_url, c
