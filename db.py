import os
import sqlite3
from typing import Tuple, List

DB_FILE = "tennis.db"

CREATE_SCRIPT = """
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    country TEXT NOT NULL,
    birthdate DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    surface TEXT NOT NULL CHECK (surface IN ('Hard', 'Clay', 'Grass')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Grand Slam', 'Masters 1000', 'ATP 500', 'ATP 250'))
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    round TEXT NOT NULL CHECK (round IN ('R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F')),
    match_date DATE NOT NULL,
    winner_id INTEGER NOT NULL,
    score TEXT NOT NULL,
    FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id),
    FOREIGN KEY (player1_id) REFERENCES players (player_id),
    FOREIGN KEY (player2_id) REFERENCES players (player_id),
    FOREIGN KEY (winner_id) REFERENCES players (player_id)
);

CREATE TABLE IF NOT EXISTS match_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    aces INTEGER NOT NULL DEFAULT 0,
    double_faults INTEGER NOT NULL DEFAULT 0,
    first_serves_in INTEGER NOT NULL DEFAULT 0,
    first_serves_total INTEGER NOT NULL DEFAULT 0,
    break_points_converted INTEGER NOT NULL DEFAULT 0,
    break_points_total INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches (match_id),
    FOREIGN KEY (player_id) REFERENCES players (player_id)
);
"""

PLAYERS_SEED = [
    ("Rafael", "Nadal", "Spain", "1986-06-03"),
    ("Novak", "Djokovic", "Serbia", "1987-05-22"),
    ("Roger", "Federer", "Switzerland", "1981-08-08"),
    ("Carlos", "Alcaraz", "Spain", "2003-05-05"),
    ("Daniil", "Medvedev", "Russia", "1996-02-11"),
    ("Stefanos", "Tsitsipas", "Greece", "1998-08-12"),
    ("Alexander", "Zverev", "Germany", "1997-04-20"),
    ("Andrey", "Rublev", "Russia", "1997-10-20"),
    ("Jannik", "Sinner", "Italy", "2001-08-16"),
    ("Taylor", "Fritz", "USA", "1997-10-28"),
    ("Casper", "Ruud", "Norway", "1998-12-22"),
    ("Hubert", "Hurkacz", "Poland", "1997-02-11"),
    ("Felix", "Auger-Aliassime", "Canada", "2000-08-08"),
    ("Cameron", "Norrie", "UK", "1995-08-23"),
    ("Pablo", "Carreno Busta", "Spain", "1991-07-12"),
    ("Denis", "Shapovalov", "Canada", "1999-04-15"),
    ("Grigor", "Dimitrov", "Bulgaria", "1991-05-16"),
    ("Karen", "Khachanov", "Russia", "1996-05-21"),
    ("Nick", "Kyrgios", "Australia", "1995-04-27"),
    ("Matteo", "Berrettini", "Italy", "1996-04-12")
]

TOURNAMENTS_SEED = [
    ("Wimbledon", "London, UK", "Grass", "2025-07-01", "2025-07-14", "Grand Slam"),
    ("US Open", "New York, USA", "Hard", "2025-08-25", "2025-09-08", "Grand Slam"),
    ("Madrid Open", "Madrid, Spain", "Clay", "2025-05-01", "2025-05-12", "Masters 1000"),
    ("Australian Open", "Melbourne, Australia", "Hard", "2025-01-20", "2025-02-02", "Grand Slam"),
    ("French Open", "Paris, France", "Clay", "2025-05-25", "2025-06-08", "Grand Slam"),
    ("Indian Wells", "Indian Wells, USA", "Hard", "2025-03-06", "2025-03-19", "Masters 1000"),
    ("Miami Open", "Miami, USA", "Hard", "2025-03-24", "2025-04-06", "Masters 1000"),
    ("Monte Carlo", "Monte Carlo, Monaco", "Clay", "2025-04-07", "2025-04-20", "Masters 1000"),
    ("Rome Masters", "Rome, Italy", "Clay", "2025-05-08", "2025-05-21", "Masters 1000"),
    ("Cincinnati Masters", "Cincinnati, USA", "Hard", "2025-08-10", "2025-08-23", "Masters 1000"),
    ("Paris Masters", "Paris, France", "Hard", "2025-10-28", "2025-11-03", "Masters 1000"),
    ("Rotterdam Open", "Rotterdam, Netherlands", "Hard", "2025-02-10", "2025-02-16", "ATP 500"),
    ("Dubai Tennis", "Dubai, UAE", "Hard", "2025-02-24", "2025-03-02", "ATP 500"),
    ("Barcelona Open", "Barcelona, Spain", "Clay", "2025-04-15", "2025-04-21", "ATP 500"),
    ("Queen's Club", "London, UK", "Grass", "2025-06-17", "2025-06-23", "ATP 500")
]

MATCHES_SEED = [
    # tournament_id, player1_id, player2_id, round, date, winner_id, score
    # Wimbledon matches
    (1, 1, 2, "F", "2025-07-14", 2, "7-6,6-4,7-6"),
    (1, 1, 4, "SF", "2025-07-12", 1, "6-4,7-5,6-4"),
    (1, 2, 5, "SF", "2025-07-12", 2, "6-3,7-6,6-4"),
    (1, 4, 7, "QF", "2025-07-10", 4, "7-6,6-4,6-4"),
    (1, 1, 9, "QF", "2025-07-10", 1, "6-4,6-2,7-5"),
    
    # US Open matches
    (2, 2, 5, "QF", "2025-09-03", 2, "6-3,7-6,7-5"),
    (2, 4, 3, "F", "2025-09-08", 4, "6-4,6-4,7-6"),
    (2, 4, 8, "SF", "2025-09-06", 4, "7-6,6-4,6-4"),
    (2, 3, 6, "SF", "2025-09-06", 3, "6-3,6-4,6-4"),
    
    # Australian Open matches
    (4, 2, 4, "F", "2025-02-02", 4, "7-6,6-4,6-4"),
    (4, 2, 7, "SF", "2025-01-31", 2, "6-3,7-6,6-4"),
    (4, 4, 5, "SF", "2025-01-31", 4, "7-5,6-4,6-4"),
    
    # French Open matches
    (5, 1, 4, "F", "2025-06-08", 1, "6-4,6-4,6-4"),
    (5, 1, 8, "SF", "2025-06-06", 1, "7-5,6-3,6-4"),
    (5, 4, 6, "SF", "2025-06-06", 4, "6-4,7-6,6-4"),
    
    # Madrid Open matches
    (3, 1, 6, "F", "2025-05-12", 1, "6-3,6-4"),
    (3, 1, 9, "SF", "2025-05-10", 1, "7-6,6-4"),
    (3, 6, 4, "SF", "2025-05-10", 6, "6-4,7-5"),
    
    # Indian Wells matches
    (6, 2, 5, "F", "2025-03-19", 2, "7-6,6-4"),
    (6, 2, 8, "SF", "2025-03-17", 2, "6-4,6-4"),
    (6, 5, 7, "SF", "2025-03-17", 5, "7-6,6-3"),
    
    # Other tournament matches
    (7, 4, 7, "F", "2025-04-06", 4, "6-4,7-5"),
    (8, 1, 8, "F", "2025-04-20", 1, "6-3,6-4"),
    (9, 2, 6, "F", "2025-05-21", 2, "7-6,6-4"),
    (10, 4, 5, "F", "2025-08-23", 4, "6-4,7-6")
]

MATCH_STATS_SEED = [
    # match_id, player_id, aces, double_faults, first_serves_in, first_serves_total, break_points_converted, break_points_total
    # Wimbledon Final stats
    (1, 1, 5, 2, 45, 60, 2, 5),
    (1, 2, 12, 1, 50, 65, 3, 6),
    
    # Wimbledon SF stats
    (2, 1, 8, 1, 48, 62, 2, 4),
    (2, 4, 10, 2, 45, 58, 1, 6),
    (3, 2, 15, 2, 52, 68, 2, 4),
    (3, 5, 7, 3, 46, 60, 1, 5),
    
    # US Open stats
    (6, 2, 18, 1, 55, 70, 2, 4),
    (6, 5, 10, 2, 48, 65, 1, 6),
    (7, 4, 12, 2, 50, 65, 2, 5),
    (7, 3, 8, 3, 45, 62, 1, 4),
    
    # Australian Open stats
    (10, 2, 14, 2, 52, 68, 2, 5),
    (10, 4, 16, 1, 54, 70, 3, 6),
    (11, 2, 12, 1, 48, 62, 2, 4),
    (11, 7, 9, 2, 45, 60, 1, 5),
    
    # French Open stats
    (13, 1, 6, 1, 50, 65, 3, 6),
    (13, 4, 8, 2, 48, 62, 1, 5),
    (14, 1, 7, 1, 52, 68, 2, 4),
    (14, 8, 5, 3, 45, 60, 1, 6),
    
    # Madrid Open stats
    (16, 1, 8, 1, 48, 62, 2, 4),
    (16, 6, 6, 2, 45, 58, 1, 5),
    (17, 1, 10, 1, 50, 65, 2, 5),
    (17, 9, 7, 2, 46, 60, 1, 4),
    
    # Indian Wells stats
    (19, 2, 15, 1, 54, 70, 2, 5),
    (19, 5, 12, 2, 50, 65, 1, 6),
    (20, 2, 14, 1, 52, 68, 2, 4),
    (20, 8, 8, 2, 48, 62, 1, 5)
]


def _table_empty(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(1) FROM {table_name};")
        count = cur.fetchone()[0]
    finally:
        cur.close()
    return count == 0


def init_db(db_file: str = DB_FILE) -> Tuple[sqlite3.Connection, bool]:
    """Create schema and seed tables only when empty to avoid duplicates.

    Returns (conn, created) where 'created' indicates whether the DB file was
    created by this call.
    """
    created = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(CREATE_SCRIPT)

    # seed each table only if it's empty
    if _table_empty(conn, 'players'):
        cur = conn.cursor()
        try:
            cur.executemany(
                "INSERT INTO players (first_name, last_name, country, birthdate) VALUES (?, ?, ?, ?)",
                PLAYERS_SEED
            )
        finally:
            cur.close()

    if _table_empty(conn, 'tournaments'):
        cur = conn.cursor()
        try:
            cur.executemany(
                "INSERT INTO tournaments (name, location, surface, start_date, end_date, category) VALUES (?, ?, ?, ?, ?, ?)",
                TOURNAMENTS_SEED
            )
        finally:
            cur.close()

    if _table_empty(conn, 'matches'):
        cur = conn.cursor()
        try:
            cur.executemany(
                "INSERT INTO matches (tournament_id, player1_id, player2_id, round, match_date, winner_id, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                MATCHES_SEED
            )
        finally:
            cur.close()

    if _table_empty(conn, 'match_stats'):
        cur = conn.cursor()
        try:
            cur.executemany(
                "INSERT INTO match_stats (match_id, player_id, aces, double_faults, first_serves_in, first_serves_total, break_points_converted, break_points_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                MATCH_STATS_SEED
            )
        finally:
            cur.close()

    conn.commit()
    return conn, created


def get_connection(db_file: str = DB_FILE) -> sqlite3.Connection:
    return sqlite3.connect(db_file)
