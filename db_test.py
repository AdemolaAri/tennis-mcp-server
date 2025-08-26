import sqlite3
import os
from typing import List, Tuple

from db import init_db

DB_FILE = "test.db"

def execute_query(conn: sqlite3.Connection, query: str) -> dict:
    cur = conn.cursor()
    try:
        cur.execute(query)
        return {"success": True, "data": cur.fetchall()}
    except sqlite3.Error as e:
        return {"success": False, "error": str(e)}
    finally:
        cur.close()

def get_player_id(conn: sqlite3.Connection, full_name: str) -> int:
    """Helper function to get player ID from full name."""
    names = full_name.split()
    if len(names) < 2:
        return None
    
    first_name = names[0]
    last_name = ' '.join(names[1:])
    
    result = execute_query(conn, f"""
        SELECT player_id FROM players 
        WHERE first_name = '{first_name}' AND last_name = '{last_name}'
    """)
    
    if not result["success"] or not result["data"]:
        return None
        
    return result["data"][0][0]

def _print_sample_rows(conn: sqlite3.Connection) -> None:
    print('\nPlayers:')
    result = execute_query(conn, 'SELECT player_id, first_name, last_name, country, birthdate FROM players')
    if result["success"]:
        for row in result["data"]:
            print(row)
    else:
        print(f"Error: {result['error']}")

    print('\nTournaments:')
    result = execute_query(conn, 'SELECT tournament_id, name, location, surface, category FROM tournaments')
    if result["success"]:
        for row in result["data"]:
            print(row)
    else:
        print(f"Error: {result['error']}")

    print('\nMatches:')
    result = execute_query(conn, """
        SELECT m.match_id, t.name, 
               p1.first_name || ' ' || p1.last_name,
               p2.first_name || ' ' || p2.last_name,
               m.round, m.score
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        JOIN players p1 ON m.player1_id = p1.player_id
        JOIN players p2 ON m.player2_id = p2.player_id
        ORDER BY m.match_date DESC
    """)
    if result["success"]:
        for row in result["data"]:
            print(row)
    else:
        print(f"Error: {result['error']}")

    print('\nMatch Stats (sample):')
    result = execute_query(conn, """
        SELECT m.match_id, 
               p.first_name || ' ' || p.last_name as player,
               s.aces, s.first_serves_in || '/' || s.first_serves_total as serves,
               s.break_points_converted || '/' || s.break_points_total as breaks
        FROM match_stats s
        JOIN matches m ON s.match_id = m.match_id
        JOIN players p ON s.player_id = p.player_id
        LIMIT 4
    """)
    if result["success"]:
        for row in result["data"]:
            print(row)
    else:
        print(f"Error: {result['error']}")
        
    # Test the player name-based queries
    print('\nTesting player stats by name:')
    player_name = "Rafael Nadal"
    player_id = get_player_id(conn, player_name)
    if player_id:
        matches_result = execute_query(conn, f"""
            SELECT 
                (SELECT COUNT(*) FROM matches WHERE player1_id = {player_id} OR player2_id = {player_id}) as total_matches,
                (SELECT COUNT(*) FROM matches WHERE winner_id = {player_id}) as matches_won,
                ROUND(CAST((SELECT COUNT(*) FROM matches WHERE winner_id = {player_id}) AS FLOAT) / 
                      CAST((SELECT COUNT(*) FROM matches WHERE player1_id = {player_id} OR player2_id = {player_id}) AS FLOAT) * 100, 1) as win_pct
            FROM players 
            WHERE player_id = {player_id}
        """)
        if matches_result["success"]:
            print(f"{player_name}'s stats:", matches_result["data"][0])
        else:
            print(f"Error getting stats for {player_name}: {matches_result['error']}")
    else:
        print(f"Player {player_name} not found")

def main() -> None:
    conn, created = init_db(DB_FILE)
    print(f"Initialized '{DB_FILE}'. Created new file: {created}")
    _print_sample_rows(conn)
    conn.close()
    os.remove(DB_FILE)


if __name__ == '__main__':
    main()