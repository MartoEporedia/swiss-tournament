"""
Database management for Swiss Tournament Simulator
Handles database schema, initialization, and queries
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional


class Database:
    """Database manager for tournament data"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or os.environ.get('TOURNAMENT_DB', 'tournament.db')

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with improved schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Drop existing tables
        cursor.execute('DROP TABLE IF EXISTS pairings')
        cursor.execute('DROP TABLE IF EXISTS standings')
        cursor.execute('DROP TABLE IF EXISTS teams')
        cursor.execute('DROP TABLE IF EXISTS playoffs')

        # Create teams table
        cursor.execute('''
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY,
            rank INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE,
            ranking INTEGER NOT NULL,
            country TEXT
        )
        ''')

        # Create standings table with full statistics
        cursor.execute('''
        CREATE TABLE standings (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            rank INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            played INTEGER DEFAULT 0,
            won INTEGER DEFAULT 0,
            drawn INTEGER DEFAULT 0,
            lost INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            goal_difference INTEGER DEFAULT 0,
            home_games INTEGER DEFAULT 0,
            away_games INTEGER DEFAULT 0,
            FOREIGN KEY (name) REFERENCES teams(name)
        )
        ''')

        # Create pairings table
        cursor.execute('''
        CREATE TABLE pairings (
            id INTEGER PRIMARY KEY,
            round INTEGER NOT NULL,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            goals1 INTEGER DEFAULT NULL,
            goals2 INTEGER DEFAULT NULL,
            simulated BOOLEAN DEFAULT 0,
            team1_home BOOLEAN DEFAULT 1,
            FOREIGN KEY (team1) REFERENCES teams(name),
            FOREIGN KEY (team2) REFERENCES teams(name)
        )
        ''')

        # Create playoffs table for knockout pairings
        cursor.execute('''
        CREATE TABLE playoffs (
            id INTEGER PRIMARY KEY,
            competition TEXT NOT NULL,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            position1 INTEGER NOT NULL,
            position2 INTEGER NOT NULL,
            FOREIGN KEY (team1) REFERENCES teams(name),
            FOREIGN KEY (team2) REFERENCES teams(name)
        )
        ''')

        conn.commit()
        conn.close()

    def load_teams(self, teams_data: List[Dict[str, Any]]):
        """Load teams into database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for team in teams_data:
            cursor.execute('''
            INSERT INTO teams (rank, name, ranking, country)
            VALUES (?, ?, ?, ?)
            ''', (team['rank'], team['name'], team['ranking'], team.get('country', '')))

            cursor.execute('''
            INSERT INTO standings (name, rank, points, played, won, drawn, lost,
                                 goals_for, goals_against, goal_difference,
                                 home_games, away_games)
            VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (team['name'], team['rank']))

        conn.commit()
        conn.close()

    def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teams ORDER BY rank')
        teams = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return teams

    def get_standings(self) -> List[Dict[str, Any]]:
        """Get standings ordered by points, goal difference, goals for"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM standings
        ORDER BY points DESC, goal_difference DESC, goals_for DESC, name ASC
        ''')
        standings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return standings

    def get_team_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get team by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teams WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_pairings(self, round_num: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get pairings, optionally filtered by round"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if round_num:
            cursor.execute('SELECT * FROM pairings WHERE round = ? ORDER BY id', (round_num,))
        else:
            cursor.execute('SELECT * FROM pairings ORDER BY round, id')

        pairings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pairings

    def get_unsimulated_pairings(self) -> List[Dict[str, Any]]:
        """Get pairings that haven't been simulated yet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM pairings
        WHERE simulated = 0
        ORDER BY round, id
        ''')
        pairings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pairings

    def add_pairing(self, round_num: int, team1: str, team2: str, team1_home: bool = True):
        """Add a new pairing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO pairings (round, team1, team2, simulated, team1_home)
        VALUES (?, ?, ?, 0, ?)
        ''', (round_num, team1, team2, 1 if team1_home else 0))
        conn.commit()
        conn.close()

    def update_pairing_result(self, pairing_id: int, goals1: int, goals2: int):
        """Update pairing with match result"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get pairing info
        cursor.execute('SELECT team1, team2, team1_home FROM pairings WHERE id = ?', (pairing_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        team1, team2, team1_home = row['team1'], row['team2'], row['team1_home']

        # Update pairing
        cursor.execute('''
        UPDATE pairings
        SET goals1 = ?, goals2 = ?, simulated = 1
        WHERE id = ?
        ''', (goals1, goals2, pairing_id))

        # Calculate points
        if goals1 > goals2:
            points1, points2 = 3, 0
            won1, won2 = 1, 0
            drawn1, drawn2 = 0, 0
            lost1, lost2 = 0, 1
        elif goals1 < goals2:
            points1, points2 = 0, 3
            won1, won2 = 0, 1
            drawn1, drawn2 = 0, 0
            lost1, lost2 = 1, 0
        else:
            points1, points2 = 1, 1
            won1, won2 = 0, 0
            drawn1, drawn2 = 1, 1
            lost1, lost2 = 0, 0

        # Update team1 standings
        cursor.execute('''
        UPDATE standings
        SET points = points + ?,
            played = played + 1,
            won = won + ?,
            drawn = drawn + ?,
            lost = lost + ?,
            goals_for = goals_for + ?,
            goals_against = goals_against + ?,
            goal_difference = goal_difference + (? - ?),
            home_games = home_games + ?,
            away_games = away_games + ?
        WHERE name = ?
        ''', (points1, won1, drawn1, lost1, goals1, goals2, goals1, goals2,
              1 if team1_home else 0, 0 if team1_home else 1, team1))

        # Update team2 standings
        cursor.execute('''
        UPDATE standings
        SET points = points + ?,
            played = played + 1,
            won = won + ?,
            drawn = drawn + ?,
            lost = lost + ?,
            goals_for = goals_for + ?,
            goals_against = goals_against + ?,
            goal_difference = goal_difference + (? - ?),
            home_games = home_games + ?,
            away_games = away_games + ?
        WHERE name = ?
        ''', (points2, won2, drawn2, lost2, goals2, goals1, goals2, goals1,
              0 if team1_home else 1, 1 if team1_home else 0, team2))

        conn.commit()
        conn.close()

    def get_past_pairings(self, team1: str, team2: str) -> bool:
        """Check if two teams have already played against each other"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) as count FROM pairings
        WHERE (team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)
        ''', (team1, team2, team2, team1))
        count = cursor.fetchone()['count']
        conn.close()
        return count > 0

    def get_current_round(self) -> int:
        """Get the current round number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(round) as max_round FROM pairings')
        result = cursor.fetchone()
        conn.close()
        max_round = result['max_round'] if result['max_round'] else 0
        return max_round

    def clear_playoffs(self):
        """Clear playoff pairings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM playoffs')
        conn.commit()
        conn.close()

    def add_playoff_pairing(self, competition: str, team1: str, team2: str,
                           position1: int, position2: int):
        """Add a playoff pairing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO playoffs (competition, team1, team2, position1, position2)
        VALUES (?, ?, ?, ?, ?)
        ''', (competition, team1, team2, position1, position2))
        conn.commit()
        conn.close()

    def get_playoffs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get playoff pairings grouped by competition"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM playoffs ORDER BY competition, position1')
        rows = cursor.fetchall()
        conn.close()

        playoffs = {
            'Champions League': [],
            'Europa League': [],
            'Conference League': []
        }

        for row in rows:
            playoffs[row['competition']].append(dict(row))

        return playoffs
