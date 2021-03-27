import mysql.connector as connector

from typing import Dict


class DB:
    def __init__(self):
        self.conn = connector.connect(
            host='mysql',
            port='3306',
            user='root',
            password='rikka',
            database='userinfo'
        )

        print(self.conn.is_connected())

        self.cur = self.conn.cursor()
        self._table_create()

    def _table_create(self):
        #self.cur.execute("DROP TABLE IF EXISTS songs;")
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
            `id` text,
            `url` text,
            `albumname` text,
            `album_artist` text,
            `songname` text,
            `artist` text,
            `duration_ms` int,
            `popularity` int,
            `acousticness` float,
            `danceability` float,
            `energy` float,
            `instrumentalness` float,
            `liveness` float,
            `loudness` float,
            `valence` float,
            `speechiness` float,
            `key` int,
            `mode` int,
            `tempo` float,
            `time_signature` int
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
            """)
        self.conn.commit()

    def insert(self, json: dict):
        self.cur.execute(
            "INSERT INTO songs VALUES ( \
                %(id)s, \
                %(url)s, \
                %(albumname)s, \
                %(album_artist)s, \
                %(songname)s, \
                %(artist)s, \
                %(duration_ms)s, \
                %(popularity)s, \
                %(acousticness)s, \
                %(danceability)s, \
                %(energy)s, \
                %(instrumentalness)s, \
                %(liveness)s, \
                %(loudness)s, \
                %(valence)s, \
                %(speechiness)s, \
                %(key)s, \
                %(mode)s, \
                %(tempo)s, \
                %(time_signature)s \
            )", {
                'id': json["id"],
                'url': json["url"],
                'albumname': json["albumname"],
                'album_artist': json["album_artist"],
                'songname': json["songname"],
                'artist': json["artist"],
                'duration_ms': json["duration_ms"],
                'popularity': json["popularity"],
                'acousticness': json["acousticness"],
                'danceability': json["danceability"],
                'energy': json["energy"],
                'instrumentalness': json["instrumentalness"],
                'liveness': json["liveness"],
                'loudness': json["loudness"],
                'valence': json["valence"],
                'speechiness': json["speechiness"],
                'key': json["key"],
                'mode': json["mode"],
                'tempo': json["tempo"],
                'time_signature': json["time_signature"]
            })
        self.conn.commit()

    def select(self):
        self.cur.execute("SELECT * FROM songs")
        rows = self.cur.fetchall()

        return rows


