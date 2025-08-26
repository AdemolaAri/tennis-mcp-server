from typing import Tuple
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
def describe_table(table_name):
    """Describe the schema of a table."""
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        return [(col[1], col[2]) for col in cur.fetchall()]
    finally:
        cur.close()


@mcp.tool()
def execute_query(query):
    """Execute a SQL query and return the results."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        return cur.fetchall()
    finally:
        cur.close()

@mcp.tool()
def get_player_stats(player_id: int):
    """Get a player's total matches, wins, and win percentage."""
    matches_won = execute_query(f"""
        SELECT COUNT(*) FROM matches 
        WHERE winner_id = {player_id}
    """)[0][0]
    
    total_matches = execute_query(f"""
        SELECT COUNT(*) FROM matches 
        WHERE player1_id = {player_id} OR player2_id = {player_id}
    """)[0][0]

    win_pct = (matches_won / total_matches * 100) if total_matches > 0 else 0
    return total_matches, matches_won, round(win_pct, 1)

@mcp.tool()
def get_head_to_head(player1_id: int, player2_id: int):
    """Get head-to-head match history between two players."""
    return execute_query(f"""
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

    

