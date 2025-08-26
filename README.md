# Tennis Database MCP Server Example

As the 2025 US Open unfolds with its thrilling matches and incredible stats, I've been thinking about how AI could enhance our tennis experience. What if we could build AI systems that understand tennis as deeply as the commentators do? That's what inspired this project—a perfect way to demonstrate the power of the Model Context Protocol (MCP) in the world of tennis.

## 🎾 The Story Behind This Project

Imagine you're building an AI tennis commentator or a sports analytics system that needs to access historical tennis data on the fly. Your large language model (LLM) assistant needs to answer questions like:

- "What's the head-to-head record between Nadal and Djokovic at Wimbledon?"
- "How does Federer perform on different surfaces?"
- "Which players have the best serve statistics in Grand Slams?"

Traditionally, you'd have to pre-write specific SQL queries for each possible question. But what if your LLM could generate and execute database queries dynamically based on natural language questions?

This is where our Tennis Database MCP Server comes in. It's a practical example of how to create a Model Context Protocol (MCP) server that exposes a SQLite tennis database as a set of tools that any LLM can use. The server provides a clean interface for querying player statistics, match histories, tournament results, and detailed match statistics.

## 🎯 What This Example Demonstrates

- How to create a simple MCP server in Python
- How to expose a SQLite database as a set of tools for LLMs
- How to structure tennis tournament data and statistics
- How to provide flexible querying capabilities through well-defined tool interfaces

## 📚 Database Schema

The database includes four main tables:

- `players`: Tennis player profiles (name, country, birthdate)
- `tournaments`: Tournament details (name, location, surface type, category)
- `matches`: Match records (players, round, score, winner)
- `match_stats`: Detailed statistics per player per match

## 🛠️ Available Tools

The server exposes several tools that an LLM can use:

1. `get_player_stats`: Retrieve a player's total matches, wins, and win percentage
2. `get_head_to_head`: Get complete match history between two players
3. `get_tournament_draw`: Get full tournament bracket and results
4. `get_player_surface_stats`: Analyze a player's performance by court surface
5. `list_tables`: List all tables in the database
6. `describe_table`: Describe the schema of a table
7. `Execute a SQL query and return the results`: Execute a SQL query and return the results. Useful for when we do not have a predefined query set


## 🚀 Running the Sample

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (recommended but not required)

### Step-by-Step Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```bash
     .venv\\Scripts\\activate
     ```

3. Install dependencies:
   ```bash
   pip install "mcp[cli]"
   ```

4. Run the server:
   ```bash
   mcp run server.py
   ```

5. Test the server:
   
   In a new terminal, start the visual interface:
   ```bash
   mcp dev server.py
   ```

   Or test directly from CLI:
   ```bash
   # List available tools
   npx @modelcontextprotocol/inspector --cli mcp run server.py --method tools/list

   # Example: Get player stats for Nadal (player_id=1)
   npx @modelcontextprotocol/inspector --cli mcp run server.py --method tools/call --tool-name get_player_stats --tool-arg player_id=1

   # Example: Get Nadal vs Djokovic head-to-head
   npx @modelcontextprotocol/inspector --cli mcp run server.py --method tools/call --tool-name get_head_to_head --tool-arg player1_id=1 --tool-arg player2_id=2
   ```

## 🌟 Example Use Cases

1. **AI Tennis Commentator**
   ```python
   # LLM can dynamically query player stats during match commentary
   stats = get_player_stats(conn, player_id=1)
   surface_stats = get_player_surface_stats(conn, player_id=1)
   ```

2. **Tournament Analysis**
   ```python
   # Generate tournament bracket analysis
   draw = get_tournament_draw(conn, tournament_id=1)
   ```

3. **Player Matchup Analysis**
   ```python
   # Analyze head-to-head history
   h2h = get_head_to_head(conn, player1_id=1, player2_id=2)
   ```

## 📝 License

MIT

---

This example is part of the Model Context Protocol (MCP) samples, demonstrating how to create practical tool interfaces for LLMs. The tennis database schema and sample data are fictional and used for demonstration purposes only.
