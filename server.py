from typing import Tuple
import sqlite3
from mcp.server.fastmcp import FastMCP
from db import init_db

mcp = FastMCP('DB Calls')

conn, _ = init_db()

@mcp.tool()
def list_tables():
    """List all tables in the database."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in cur.fetchall()]
    finally:
        cur.close()

@mcp.tool()
def describe_table(table_name: str):
    """Describe the schema of a table."""
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        return [(col[1], col[2]) for col in cur.fetchall()]
    finally:
        cur.close()


@mcp.tool()
def execute_query(query: str):
    """Execute a SQL query and return the results."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        return {"success": True, "data": cur.fetchall()}
    except sqlite3.Error as e:
        return {"success": False, "error": str(e)}
    finally:
        cur.close()

def get_player_id(full_name):
    """Helper function to get player ID from full name."""
    names = full_name.split()
    if len(names) < 2:
        return None
    
    first_name = names[0]
    last_name = ' '.join(names[1:])
    
    result = execute_query(f"""
        SELECT player_id FROM players 
        WHERE first_name = '{first_name}' AND last_name = '{last_name}'
    """)
    
    if not result["success"] or not result["data"]:
        return None
        
    return result["data"][0][0]

@mcp.tool()
def get_player_stats(player_name: str):
    """Get a player's total matches, wins, and win percentage."""
    player_id = get_player_id(player_name)
    if not player_id:
        return {"success": False, "error": f"Player '{player_name}' not found"}
        
    result = execute_query(f"""
        SELECT 
            (SELECT COUNT(*) FROM matches WHERE player1_id = {player_id} OR player2_id = {player_id}) as total_matches,
            (SELECT COUNT(*) FROM matches WHERE winner_id = {player_id}) as matches_won,
            ROUND(CAST((SELECT COUNT(*) FROM matches WHERE winner_id = {player_id}) AS FLOAT) / 
                  CAST((SELECT COUNT(*) FROM matches WHERE player1_id = {player_id} OR player2_id = {player_id}) AS FLOAT) * 100, 1) as win_pct
        FROM players 
        WHERE player_id = {player_id}
    """)
    
    if not result["success"]:
        return result
        
    if not result["data"]:
        return {"success": False, "error": "No matches found for this player"}
        
    total_matches, matches_won, win_pct = result["data"][0]
    return {
        "success": True,
        "data": {
            "total_matches": total_matches,
            "matches_won": matches_won,
            "win_percentage": win_pct or 0
        }
    }

@mcp.tool()
def get_head_to_head(player1_name: str, player2_name: str):
    """Get head-to-head match history between two players."""
    player1_id = get_player_id(player1_name)
    player2_id = get_player_id(player2_name)
    
    if not player1_id:
        return {"success": False, "error": f"Player '{player1_name}' not found"}
    if not player2_id:
        return {"success": False, "error": f"Player '{player2_name}' not found"}
        
    result = execute_query(f"""
        SELECT t.name, m.round, m.match_date, m.score,
               CASE WHEN m.winner_id = {player1_id} THEN 
                    (SELECT first_name || ' ' || last_name FROM players WHERE player_id = {player1_id})
               ELSE 
                    (SELECT first_name || ' ' || last_name FROM players WHERE player_id = {player2_id})
               END as winner
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        WHERE (m.player1_id = {player1_id} AND m.player2_id = {player2_id})
           OR (m.player1_id = {player2_id} AND m.player2_id = {player1_id})
        ORDER BY m.match_date DESC
    """)
    
    if not result["success"]:
        return result
        
    return {
        "success": True,
        "data": [
            {
                "tournament": row[0],
                "round": row[1],
                "date": row[2],
                "score": row[3],
                "winner": row[4]
            }
            for row in result["data"]
        ]
    }

@mcp.tool()
def get_tournament_draw(tournament_id: int):
    """Get the tournament draw with match results by round."""
    return execute_query(f"""
        SELECT m.round,
               p1.first_name || ' ' || p1.last_name as player1,
               p2.first_name || ' ' || p2.last_name as player2,
               m.score,
               CASE WHEN m.winner_id = p1.player_id THEN p1.first_name || ' ' || p1.last_name
                    ELSE p2.first_name || ' ' || p2.last_name
               END as winner
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.player_id
        JOIN players p2 ON m.player2_id = p2.player_id
        WHERE m.tournament_id = {tournament_id}
        ORDER BY 
            CASE m.round 
                WHEN 'F' THEN 1 
                WHEN 'SF' THEN 2
                WHEN 'QF' THEN 3
                WHEN 'R16' THEN 4
                WHEN 'R32' THEN 5
                WHEN 'R64' THEN 6
                WHEN 'R128' THEN 7
            END,
            m.match_id
    """)

@mcp.tool()
def get_player_surface_stats(player_id: int) :
    """Get a player's win-loss record by surface type."""
    return execute_query(f"""
        SELECT t.surface,
               COUNT(*) as total_matches,
               SUM(CASE WHEN m.winner_id = {player_id} THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN m.winner_id != {player_id} THEN 1 ELSE 0 END) as losses,
               ROUND(SUM(CASE WHEN m.winner_id = {player_id} THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as win_pct
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        WHERE m.player1_id = {player_id} OR m.player2_id = {player_id}
        GROUP BY t.surface
        ORDER BY wins DESC
    """)

if __name__ == '__main__':
    mcp.run()

    

