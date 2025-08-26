import sqlite3
import os
from typing import List, Tuple

from db import init_db

DB_FILE = "test.db"

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
    os.remove(DB_FILE)


if __name__ == '__main__':
    main()