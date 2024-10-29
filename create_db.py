import sqlite3
import os

def create_database():


    # Check if the TOURNAMENT_DB environment variable is set
    if 'TOURNAMENT_DB' not in os.environ:
        os.environ['TOURNAMENT_DB'] = 'tournament.db'
        
    # List of teams to be inserted into the database
    teams = [
        {"Rank": 1, "Team": "Manchester City", "Ranking": 148},
        {"Rank": 2, "Team": "Bayern Monaco", "Ranking": 144},
        {"Rank": 3, "Team": "Real Madrid", "Ranking": 136},
        {"Rank": 4, "Team": "Paris Saint-Germain", "Ranking": 116},
        {"Rank": 5, "Team": "Liverpool", "Ranking": 114},
        {"Rank": 6, "Team": "Roma", "Ranking": 101},
        {"Rank": 7, "Team": "Inter", "Ranking": 101},
        {"Rank": 8, "Team": "Borussia Dortmund", "Ranking": 97},
        {"Rank": 9, "Team": "RB Leipzig", "Ranking": 97},
        {"Rank": 10, "Team": "Chelsea", "Ranking": 96},
        {"Rank": 11, "Team": "Manchester United", "Ranking": 92},
        {"Rank": 12, "Team": "Barcelona", "Ranking": 91},
        {"Rank": 13, "Team": "Bayer Leverkusen", "Ranking": 90},
        {"Rank": 14, "Team": "Atletico Madrid", "Ranking": 89},
        {"Rank": 15, "Team": "Sevilla", "Ranking": 84},
        {"Rank": 16, "Team": "Villarreal", "Ranking": 82},
        {"Rank": 17, "Team": "Atalanta", "Ranking": 81},
        {"Rank": 18, "Team": "Napoli", "Ranking": 80},
        {"Rank": 19, "Team": "Juventus", "Ranking": 80},
        {"Rank": 20, "Team": "Benfica", "Ranking": 79},
        {"Rank": 21, "Team": "Porto", "Ranking": 77},
        {"Rank": 22, "Team": "Arsenal", "Ranking": 72},
        {"Rank": 23, "Team": "West Ham Utd", "Ranking": 69},
        {"Rank": 24, "Team": "Ajax", "Ranking": 67},
        {"Rank": 25, "Team": "Club Brugge", "Ranking": 64},
        {"Rank": 26, "Team": "Rangers", "Ranking": 63},
        {"Rank": 27, "Team": "Shakhtar Donetsk", "Ranking": 63},
        {"Rank": 28, "Team": "Eintracht Frankfurt", "Ranking": 60},
        {"Rank": 29, "Team": "Milan", "Ranking": 59},
        {"Rank": 30, "Team": "Feyenoord", "Ranking": 57},
        {"Rank": 31, "Team": "Sporting Lisbon", "Ranking": 54},
        {"Rank": 32, "Team": "Lazio", "Ranking": 54},
        {"Rank": 33, "Team": "PSV", "Ranking": 54},
        {"Rank": 34, "Team": "Tottenham", "Ranking": 54},
        {"Rank": 35, "Team": "Slavia Prague", "Ranking": 53},
        {"Rank": 36, "Team": "Basel", "Ranking": 52},
        {"Rank": 37, "Team": "Copenhagen", "Ranking": 51},
        {"Rank": 38, "Team": "Real Sociedad", "Ranking": 51},
        {"Rank": 39, "Team": "Dinamo Zagreb", "Ranking": 50},
        {"Rank": 40, "Team": "Salzburg", "Ranking": 50},
        {"Rank": 41, "Team": "AZ Alkmaar", "Ranking": 50},
        {"Rank": 42, "Team": "Braga", "Ranking": 49},
        {"Rank": 43, "Team": "Marseille", "Ranking": 47},
        {"Rank": 44, "Team": "Lille", "Ranking": 47},
        {"Rank": 45, "Team": "Gent", "Ranking": 45},
        {"Rank": 46, "Team": "Lyon", "Ranking": 44},
        {"Rank": 47, "Team": "Rennes", "Ranking": 43},
        {"Rank": 48, "Team": "Olympiacos", "Ranking": 41},
        {"Rank": 49, "Team": "Red Star Belgrade", "Ranking": 40},
        {"Rank": 50, "Team": "Fiorentina", "Ranking": 38},
        {"Rank": 51, "Team": "PAOK", "Ranking": 37},
        {"Rank": 52, "Team": "LASK", "Ranking": 37},
        {"Rank": 53, "Team": "Fenerbahce", "Ranking": 36},
        {"Rank": 54, "Team": "Maccabi Tel Aviv", "Ranking": 35},
        {"Rank": 55, "Team": "Ferencvaros", "Ranking": 35},
        {"Rank": 56, "Team": "Young Boys", "Ranking": 34},
        {"Rank": 57, "Team": "Qarabag", "Ranking": 33},
        {"Rank": 58, "Team": "Betis", "Ranking": 33},
        {"Rank": 59, "Team": "Celtic", "Ranking": 32},
        {"Rank": 60, "Team": "Galatasaray", "Ranking": 31},
        {"Rank": 61, "Team": "Slovan Bratislava", "Ranking": 30},
        {"Rank": 62, "Team": "Istanbul Basaksehir", "Ranking": 29},
        {"Rank": 63, "Team": "Molde", "Ranking": 28},
        {"Rank": 64, "Team": "Viktoria Plzen", "Ranking": 28},
        {"Rank": 65, "Team": "Freiburg", "Ranking": 28},
        {"Rank": 66, "Team": "Bodo/Glimt", "Ranking": 28},
        {"Rank": 67, "Team": "Union Saint-Gilloise", "Ranking": 27},
        {"Rank": 68, "Team": "Dynamo Kyiv", "Ranking": 26},
        {"Rank": 69, "Team": "CFR Cluj", "Ranking": 26},
        {"Rank": 70, "Team": "Ludogorets", "Ranking": 26},
        {"Rank": 71, "Team": "Midtjylland", "Ranking": 25},
        {"Rank": 72, "Team": "Partizan", "Ranking": 25},
        {"Rank": 73, "Team": "Monaco", "Ranking": 24},
        {"Rank": 74, "Team": "Union Berlin", "Ranking": 23},
        {"Rank": 75, "Team": "Antwerp", "Ranking": 22},
        {"Rank": 76, "Team": "Leicester City", "Ranking": 23},
        {"Rank": 77, "Team": "Sparta Praga", "Ranking": 22},
        {"Rank": 78, "Team": "Wolfsburg", "Ranking": 22},
        {"Rank": 79, "Team": "Zenit San Pietroburgo", "Ranking": 22},
        {"Rank": 80, "Team": "Borussia M'gladbach", "Ranking": 21},
        {"Rank": 81, "Team": "Aston Villa", "Ranking": 17},
        {"Rank": 82, "Team": "Brighton", "Ranking": 16},
        {"Rank": 83, "Team": "Newcastle Utd", "Ranking": 8},
        {"Rank": 84, "Team": "Wolverhampton", "Ranking": 16},
        {"Rank": 85, "Team": "Sheriff Tiraspol", "Ranking": 20},
        {"Rank": 86, "Team": "Lech Poznań", "Ranking": 19},
        {"Rank": 87, "Team": "Zorja", "Ranking": 18},
        {"Rank": 88, "Team": "Malmö FF", "Ranking": 18},
        {"Rank": 89, "Team": "Legia Varsavia", "Ranking": 18},
        {"Rank": 90, "Team": "Maccabi Haifa", "Ranking": 18},
        {"Rank": 91, "Team": "Osasuna", "Ranking": 2},
        {"Rank": 92, "Team": "Granada", "Ranking": 13},
        {"Rank": 93, "Team": "Valencia", "Ranking": 17},
        {"Rank": 94, "Team": "Celta Vigo", "Ranking": 8},
        {"Rank": 95, "Team": "Alavés", "Ranking": 8},
        {"Rank": 96, "Team": "Getafe", "Ranking": 9},
    ]
    conn = sqlite3.connect(os.environ['TOURNAMENT_DB'])
    cursor = conn.cursor()
    
    # Drop tables if they exist to recreate with new schema
    cursor.execute('DROP TABLE IF EXISTS teams')
    cursor.execute('DROP TABLE IF EXISTS pairings')
    cursor.execute('DROP TABLE IF EXISTS standings')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        rank INTEGER,
        name TEXT,
        ranking INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pairings (
        id INTEGER PRIMARY KEY,
        round INTEGER,
        team1 TEXT,
        team2 TEXT,
        goals1 INTEGER DEFAULT NULL,
        goals2 INTEGER DEFAULT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS standings (
        id INTEGER PRIMARY KEY,
        rank INTEGER,
        name TEXT,
        points INTEGER DEFAULT 0
    )
    ''')

    for team in teams:
        cursor.execute('''
        INSERT INTO teams (rank, name, ranking) VALUES (?, ?, ?)
        ''', (team['Rank'], team['Team'], team['Ranking']))

        cursor.execute('''
        INSERT INTO standings (rank, name, points) VALUES (?, ?, ?)
        ''', (team['Rank'], team['Team'], 0))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()