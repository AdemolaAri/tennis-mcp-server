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
    ("Stefanos", "Tsitsipas", "Greece", "1998-08-12")
]

TOURNAMENTS_SEED = [
    ("Wimbledon", "London, UK", "Grass", "2025-07-01", "2025-07-14", "Grand Slam"),
    ("US Open", "New York, USA", "Hard", "2025-08-25", "2025-09-08", "Grand Slam"),
    ("Madrid Open", "Madrid, Spain", "Clay", "2025-05-01", "2025-05-12", "Masters 1000")
]

MATCHES_SEED = [
    # tournament_id, player1_id, player2_id, round, date, winner_id, score
    (1, 1, 2, "F", "2025-07-14", 2, "7-6,6-4,7-6"),
    (1, 3, 4, "SF", "2025-07-12", 3, "6-4,6-4,6-4"),
    (2, 2, 5, "QF", "2025-09-03", 2, "6-3,7-6,7-5")
]

MATCH_STATS_SEED = [
    # match_id, player_id, aces, double_faults, first_serves_in, first_serves_total, break_points_converted, break_points_total
    (1, 1, 5, 2, 45, 60, 2, 5),
    (1, 2, 12, 1, 50, 65, 3, 6),
    (2, 3, 15, 0, 48, 62, 3, 4),
    (2, 4, 8, 3, 40, 58, 1, 5)
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


def list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def describe_table(conn: sqlite3.Connection, table_name: str) -> List[Tuple]:
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        return [(col[1], col[2]) for col in cur.fetchall()]
    finally:
        cur.close()


def execute_query(conn: sqlite3.Connection, query: str) -> List[Tuple]:
    cur = conn.cursor()
    try:
        cur.execute(query)
        return cur.fetchall()
    finally:
        cur.close()


def _print_sample_rows(conn: sqlite3.Connection) -> None:
    print('\nPlayers:')
    for row in execute_query(conn, 'SELECT player_id, first_name, last_name, country, birthdate FROM players'):
        print(row)

    print('\nTournaments:')
    for row in execute_query(conn, 'SELECT tournament_id, name, location, surface, category FROM tournaments'):
        print(row)

    print('\nMatches:')
    for row in execute_query(conn, """
        SELECT m.match_id, t.name, 
               p1.first_name || ' ' || p1.last_name,
               p2.first_name || ' ' || p2.last_name,
               m.round, m.score
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        JOIN players p1 ON m.player1_id = p1.player_id
        JOIN players p2 ON m.player2_id = p2.player_id
        ORDER BY m.match_date DESC
    """):
        print(row)

    print('\nMatch Stats (sample):')
    for row in execute_query(conn, """
        SELECT m.match_id, 
               p.first_name || ' ' || p.last_name as player,
               s.aces, s.first_serves_in || '/' || s.first_serves_total as serves,
               s.break_points_converted || '/' || s.break_points_total as breaks
        FROM match_stats s
        JOIN matches m ON s.match_id = m.match_id
        JOIN players p ON s.player_id = p.player_id
        LIMIT 4
    """):
        print(row)


def main() -> None:
    conn, created = init_db(DB_FILE)
    print(f"Initialized '{DB_FILE}'. Created new file: {created}")
    _print_sample_rows(conn)
    conn.close()


if __name__ == '__main__':
    main()
