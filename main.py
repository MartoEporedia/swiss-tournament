import sqlite3
import pandas as pd
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from create_db import create_database

class TournamentGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Tournament Manager')
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()

        self.result_area = QTextEdit(self)
        self.result_area.setReadOnly(True)
        self.layout.addWidget(self.result_area)

        self.create_pairings_button = QPushButton('Create Pairings', self)
        self.create_pairings_button.clicked.connect(self.create_pairings)
        self.layout.addWidget(self.create_pairings_button)

        self.simulate_match_button = QPushButton('Simulate Match', self)
        self.simulate_match_button.clicked.connect(self.simulate_match)
        self.layout.addWidget(self.simulate_match_button)

        self.show_standings_button = QPushButton('Show Standings', self)
        self.show_standings_button.clicked.connect(self.show_standings)
        self.layout.addWidget(self.show_standings_button)

        self.show_all_pairings_button = QPushButton('Show All Pairings', self)
        self.show_all_pairings_button.clicked.connect(self.show_all_pairings)
        self.layout.addWidget(self.show_all_pairings_button)

        self.reset_database_button = QPushButton('Reset DB', self)
        self.reset_database_button.clicked.connect(create_database)
        self.layout.addWidget(self.reset_database_button)

        self.setLayout(self.layout)

    def create_pairings(self):
        conn = sqlite3.connect(os.environ['TOURNAMENT_DB'] if 'TOURNAMENT_DB' in os.environ else 'tournament.db')
        cursor = conn.cursor()
        
        # Fetch teams with their points
        cursor.execute('SELECT name, points FROM standings ORDER BY points DESC')
        teams = [{"Team": row[0], "Points": row[1]} for row in cursor.fetchall()]
        
        cursor.execute('SELECT round FROM pairings ORDER BY round DESC LIMIT 1')
        last_round = cursor.fetchone()
        last_round = last_round[0] if last_round else None
        next_round = 1 if not last_round else last_round + 1
        
        cursor.execute('SELECT team1, team2 FROM pairings WHERE goals1 IS NULL AND goals2 IS NULL')
        no_calculates_pairings = [(row[0], row[1]) for row in cursor.fetchall()]
        if no_calculates_pairings:
            pairings_text = "\n".join([f"{team1} vs {team2}" for team1, team2 in no_calculates_pairings])
            self.result_area.setText(f"Round {last_round} was not simulated:\n{pairings_text}")
            return
        
        if last_round == 8:
            self.result_area.setText("All rounds have been created")
            return
        
        cursor.execute('SELECT team1, team2 FROM pairings')
        past_pairings = [(row[0], row[1]) for row in cursor.fetchall()]

        pairings = []
        paired = set()

        for team1 in teams:
            if team1["Team"] in paired:
                continue
            for team2 in teams:
                if team2["Team"] in paired or team1["Team"] == team2["Team"]:
                    continue
                if (team1["Team"], team2["Team"]) not in past_pairings and team1["Points"] == team2["Points"]:
                    cursor.execute('INSERT INTO pairings (round, team1, team2) VALUES (?, ?, ?)', (next_round, team1["Team"], team2["Team"]))
                    paired.add(team1["Team"])
                    paired.add(team2["Team"])
                    pairings.append((team1["Team"], team2["Team"]))
                    break

        conn.commit()
        conn.close()

        self.result_area.setText("\n".join([f"{team1} vs {team2}" for team1, team2 in pairings]))
    

    def _calculate_probabilities(self, ranking_team1, ranking_team2):
        # Calculate the difference in ranking between the teams
        difference = ranking_team1 - ranking_team2

        if difference > 50:
            win_probability_team1 = 85  # Higher ranked team has high win probability
            draw_probability = 10  # Lower chance of draw with large difference
            win_probability_team2 = 5
        elif difference < -50:
            win_probability_team1 = 5
            draw_probability = 10
            win_probability_team2 = 85
        else:
            # Base probabilities for win, draw, and loss
            win_probability_team1 = 50 + difference * 0.2  # Higher ranked team has higher win probability
            draw_probability = max(5, 40 - abs(difference) * 0.1)  # Lower chance of draw with greater difference
            win_probability_team2 = 100 - (win_probability_team1 + draw_probability)

        return win_probability_team1, draw_probability, win_probability_team2

    def _generate_goals(self, ranking):
        # Goal average influenced by team ranking
        # Higher ranking -> higher expected average goals
        goal_average = max(0.5, ranking / 100)  # e.g., ranking 150 -> avg 1.5 goals, ranking 50 -> avg 0.5 goals
        deviation = 1  # Standard deviation for randomness in goals

        # Generate a random number of goals based on the average
        return max(0, int(random.gauss(goal_average, deviation)))

    def simulate_match(self):
        conn = sqlite3.connect(os.environ['TOURNAMENT_DB'] if 'TOURNAMENT_DB' in os.environ else 'tournament.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT 
            p.id AS pairing_id,
            p.round,
            t1.name AS team1_name,
            t1.ranking AS team1_ranking,
            t2.name AS team2_name,
            t2.ranking AS team2_ranking
        FROM 
            pairings p
        JOIN 
            teams t1 ON p.team1 = t1.name
        JOIN 
            teams t2 ON p.team2 = t2.name
        WHERE p.goals1 IS NULL AND p.goals2 IS NULL
        ORDER BY 
            p.round, t1.name, t2.name
        ''')
        pairings = cursor.fetchall()
        if pairings == []:
            self.result_area.setText("No pairings to simulate")
            return

        results = []
        for pairing in pairings:
            team1 = pairing[2]
            ranking_team1 = int(pairing[3])  # Convert to int
            team2 = pairing[4]
            ranking_team2 = int(pairing[5])  # Convert to int
            # Calculate win/draw/loss probabilities based on rankings
            win_prob_team1, draw_prob, win_prob_team2 = self._calculate_probabilities(ranking_team1, ranking_team2)
            # Generate a random number to determine the outcome
            outcome = random.uniform(0, 100)
            
            # Generate initial goals for each team
            goals_team1 = self._generate_goals(ranking_team1)
            goals_team2 = self._generate_goals(ranking_team2)

            # Adjust goals to ensure outcome matches the calculated probabilities
            if outcome <= win_prob_team1:
                # Ensure team 1 wins by adjusting goals if necessary
                while goals_team1 <= goals_team2:
                    goals_team1 += 1
            elif outcome <= win_prob_team1 + draw_prob:
                # Ensure a draw by adjusting goals
                while goals_team1 != goals_team2:
                    goals_team1 = self._generate_goals(ranking_team1)
                    goals_team2 = self._generate_goals(ranking_team2)
            else:
                # Ensure team 2 wins by adjusting goals if necessary
                while goals_team2 <= goals_team1:
                    goals_team2 += 1
            # Determina i punti assegnati a ciascuna squadra in base ai gol segnati
            if goals_team1 > goals_team2:
                points1 = 3
                points2 = 0
            elif goals_team1 < goals_team2:
                points1 = 0
                points2 = 3
            else:
                points1 = 1
                points2 = 1

            result = f"{team1} {goals_team1} - {team2} {goals_team2}"
            results.append(result)
            cursor.execute('UPDATE pairings SET goals1 = ?, goals2 = ? WHERE id = ?', (goals_team1, goals_team2, pairing[0]))

            # Update standings
            cursor.execute('UPDATE standings SET points = points + ? WHERE name = ?', 
                        (points1, team1))
            cursor.execute('UPDATE standings SET points = points + ? WHERE name = ?',
                        (points2, team2))

        conn.commit()
        conn.close()

        self.result_area.setText("\n".join(results))

    def show_standings(self):
        conn = sqlite3.connect(os.environ['TOURNAMENT_DB'] if 'TOURNAMENT_DB' in os.environ else 'tournament.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, points FROM standings ORDER BY points DESC')
        standings = cursor.fetchall()

        # Convert standings to DataFrame
        df_standings = pd.DataFrame(standings, columns=['name', 'points'])

        # Split standings into Champions League, Europa League, Conference League, and Relegation
        df_cl = df_standings.iloc[:24]
        df_el = df_standings.iloc[24:48]
        df_conf = df_standings.iloc[48:80]
        df_out = df_standings.iloc[80:]

        # Generate text for each section
        cl_text = "\n".join([f"{row['name']}: {row['points']} points" for _, row in df_cl.iterrows()])
        el_text = "\n".join([f"{row['name']}: {row['points']} points" for _, row in df_el.iterrows()])
        conf_text = "\n".join([f"{row['name']}: {row['points']} points" for _, row in df_conf.iterrows()])
        out_text = "\n".join([f"{row['name']}: {row['points']} points" for _, row in df_out.iterrows()])

        self.result_area.setText(f"Champions League:\n{cl_text}\n\nEuropa League:\n{el_text}\n\nConference League:\n{conf_text}\n\nRelegation:\n{out_text}")

    def show_all_pairings(self):
        conn = sqlite3.connect(os.environ['TOURNAMENT_DB'] if 'TOURNAMENT_DB' in os.environ else 'tournament.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT 
            p.round,
            t1.name AS team1,
            p.goals1,
            t2.name AS team2,
            p.goals2
        FROM 
            pairings p
        JOIN 
            teams t1 ON p.team1 = t1.name
        JOIN 
            teams t2 ON p.team2 = t2.name
        ORDER BY 
            p.round, t1.name, t2.name
        ''')
        pairings = cursor.fetchall()

        pairings_text = "\n".join([f"Round {row[0]}: {row[1]} {row[2]} - {row[3]} {row[4]}" for row in pairings])
        self.result_area.setText(pairings_text)

if __name__ == '__main__':
    app = QApplication([])
    window = TournamentGUI()
    window.show()
    app.exec_()