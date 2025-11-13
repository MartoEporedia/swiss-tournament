"""
Flask web application for Swiss Tournament Simulator
Provides REST API and serves web interface
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
from database import Database
from simulator import MatchSimulator
from create_db import teams as initial_teams
from uefa_rankings import fetch_latest_rankings


app = Flask(__name__)
CORS(app)

# Initialize database path
DB_PATH = os.environ.get('TOURNAMENT_DB', 'tournament.db')
os.environ['TOURNAMENT_DB'] = DB_PATH

db = Database(DB_PATH)
simulator = MatchSimulator()


# ================== API ENDPOINTS ==================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_tournament():
    """Initialize tournament with fresh database"""
    try:
        db.init_db()

        # Try to fetch latest UEFA rankings online
        print("Fetching latest UEFA rankings...")
        try:
            online_teams = fetch_latest_rankings()
            teams_source = "online (UEFA)"
        except:
            print("Failed to fetch online rankings, using fallback data")
            online_teams = initial_teams
            teams_source = "local fallback"

        # Load teams
        teams_data = [
            {
                'rank': team['Rank'],
                'name': team['Team'],
                'ranking': team['Ranking'],
                'country': team.get('country', '')
            }
            for team in online_teams
        ]

        db.load_teams(teams_data)

        return jsonify({
            'success': True,
            'message': f'Tournament initialized with {len(teams_data)} teams from {teams_source}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all teams"""
    try:
        teams = db.get_all_teams()
        return jsonify({'success': True, 'teams': teams})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/standings', methods=['GET'])
def get_standings():
    """Get current standings with categorization"""
    try:
        standings = db.get_standings()

        # Add position to each team
        for i, team in enumerate(standings):
            team['position'] = i + 1

            # Categorize teams
            if team['position'] <= 24:
                team['category'] = 'Champions League'
                team['category_color'] = '#0066cc'
            elif team['position'] <= 48:
                team['category'] = 'Europa League'
                team['category_color'] = '#ff6600'
            elif team['position'] <= 80:
                team['category'] = 'Conference League'
                team['category_color'] = '#00cc66'
            else:
                team['category'] = 'Eliminated'
                team['category_color'] = '#cc0000'

        return jsonify({'success': True, 'standings': standings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pairings', methods=['GET'])
def get_pairings():
    """Get all pairings or by round"""
    try:
        round_num = request.args.get('round', type=int)
        pairings = db.get_pairings(round_num)

        # Enrich with team rankings
        for pairing in pairings:
            team1_data = db.get_team_by_name(pairing['team1'])
            team2_data = db.get_team_by_name(pairing['team2'])

            pairing['team1_ranking'] = team1_data['ranking'] if team1_data else 0
            pairing['team2_ranking'] = team2_data['ranking'] if team2_data else 0

        return jsonify({'success': True, 'pairings': pairings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pairings/create', methods=['POST'])
def create_pairings():
    """Create pairings for the next round using Swiss system with home/away balance"""
    try:
        # Check if there are unsimulated matches
        unsimulated = db.get_unsimulated_pairings()
        if unsimulated:
            return jsonify({
                'success': False,
                'error': f'There are {len(unsimulated)} unsimulated matches. Please simulate them first.'
            }), 400

        # Get current round and standings
        current_round = db.get_current_round()
        next_round = current_round + 1

        # Check if we've reached 8 rounds
        if next_round > 8:
            return jsonify({
                'success': False,
                'error': 'All 8 Swiss rounds have been completed. Generate playoffs instead.'
            }), 400

        standings = db.get_standings()
        pairings_created = 0

        # ROUND 1: Tennis-style seeding (1 vs 96, 2 vs 95, etc.)
        if next_round == 1:
            teams = db.get_all_teams()
            # Sort by initial rank
            teams.sort(key=lambda x: x['rank'])

            n = len(teams)
            for i in range(n // 2):
                team1 = teams[i]
                team2 = teams[n - 1 - i]

                # Higher ranked team (lower rank number) plays at home
                db.add_pairing(next_round, team1['name'], team2['name'], team1_home=True)
                pairings_created += 1

            return jsonify({
                'success': True,
                'round': next_round,
                'pairings_created': pairings_created,
                'pairing_method': 'Tennis-style seeding (1 vs 96, 2 vs 95, ...)'
            })

        # ROUNDS 2-8: Swiss system with home/away balance
        else:
            # Group teams by points
            points_groups = {}
            for team in standings:
                points = team['points']
                if points not in points_groups:
                    points_groups[points] = []
                points_groups[points].append(team)

            # Sort points in descending order
            sorted_points = sorted(points_groups.keys(), reverse=True)

            # Try to pair teams within same point group
            carry_over = []

            for points in sorted_points:
                teams_in_group = points_groups[points] + carry_over
                carry_over = []

                # Try to pair teams in this group
                while len(teams_in_group) >= 2:
                    team1 = teams_in_group[0]

                    # Find a suitable opponent that hasn't been faced before
                    opponent_found = False
                    for i in range(1, len(teams_in_group)):
                        team2 = teams_in_group[i]

                        # Check if teams have already played
                        if not db.get_past_pairings(team1['name'], team2['name']):
                            # Determine home/away based on balance (each team needs 4 home, 4 away)
                            team1_home_games = team1['home_games']
                            team1_away_games = team1['away_games']
                            team2_home_games = team2['home_games']
                            team2_away_games = team2['away_games']

                            # Decide who plays at home
                            if team1_home_games < 4 and team2_away_games < 4:
                                # team1 at home
                                team1_home = True
                            elif team1_away_games < 4 and team2_home_games < 4:
                                # team2 at home (team1 away)
                                team1_home = False
                            elif team1_home_games < team1_away_games:
                                # team1 needs more home games
                                team1_home = True
                            elif team2_home_games < team2_away_games:
                                # team2 needs more home games
                                team1_home = False
                            else:
                                # Default: alternate or random
                                import random
                                team1_home = random.choice([True, False])

                            # Pair these teams
                            db.add_pairing(next_round, team1['name'], team2['name'], team1_home=team1_home)
                            pairings_created += 1

                            # Remove from group
                            teams_in_group.pop(i)
                            teams_in_group.pop(0)

                            opponent_found = True
                            break

                    if not opponent_found:
                        # Can't pair this team in current group, carry over
                        carry_over.append(teams_in_group.pop(0))

                # Add remaining team to carry over
                if teams_in_group:
                    carry_over.extend(teams_in_group)

            # Handle remaining teams by pairing them even if they've played before
            while len(carry_over) >= 2:
                team1 = carry_over.pop(0)
                team2 = carry_over.pop(0)

                # Determine home/away
                team1_home = team1['home_games'] <= team1['away_games']

                db.add_pairing(next_round, team1['name'], team2['name'], team1_home=team1_home)
                pairings_created += 1

            # If odd number of teams, one gets a bye (forfeit win)
            if carry_over:
                team = carry_over[0]
                # Give the team a 3-0 win (bye)
                db.add_pairing(next_round, team['name'], 'BYE', team1_home=True)
                # Simulate automatic win
                pairings = db.get_pairings(next_round)
                bye_pairing = [p for p in pairings if p['team2'] == 'BYE'][0]
                db.update_pairing_result(bye_pairing['id'], 3, 0)
                pairings_created += 1

            return jsonify({
                'success': True,
                'round': next_round,
                'pairings_created': pairings_created,
                'pairing_method': 'Swiss system with home/away balance'
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/simulate', methods=['POST'])
def simulate_matches():
    """Simulate all unsimulated matches"""
    try:
        # Get unsimulated pairings
        unsimulated = db.get_unsimulated_pairings()

        if not unsimulated:
            return jsonify({
                'success': False,
                'error': 'No matches to simulate'
            }), 400

        results = []

        for pairing in unsimulated:
            # Skip bye matches
            if pairing['team2'] == 'BYE':
                continue

            # Get team data
            team1_data = db.get_team_by_name(pairing['team1'])
            team2_data = db.get_team_by_name(pairing['team2'])

            if not team1_data or not team2_data:
                continue

            # Simulate match
            goals1, goals2, stats = simulator.simulate_match(
                pairing['team1'], team1_data['ranking'],
                pairing['team2'], team2_data['ranking']
            )

            # Update database
            db.update_pairing_result(pairing['id'], goals1, goals2)

            # Add to results
            results.append({
                'round': pairing['round'],
                'team1': pairing['team1'],
                'team2': pairing['team2'],
                'goals1': goals1,
                'goals2': goals2,
                'stats': stats
            })

        return jsonify({
            'success': True,
            'matches_simulated': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playoffs/generate', methods=['POST'])
def generate_playoffs():
    """Generate playoff pairings after Swiss rounds complete"""
    try:
        # Check if all 8 rounds are complete
        current_round = db.get_current_round()
        if current_round < 8:
            return jsonify({
                'success': False,
                'error': f'Only {current_round} rounds completed. Need 8 rounds before playoffs.'
            }), 400

        # Check if there are unsimulated matches
        unsimulated = db.get_unsimulated_pairings()
        if unsimulated:
            return jsonify({
                'success': False,
                'error': f'There are {len(unsimulated)} unsimulated matches. Please simulate them first.'
            }), 400

        # Get final standings
        standings = db.get_standings()

        # Clear existing playoffs
        db.clear_playoffs()

        # Champions League playoffs: positions 1-24 (12 pairings)
        # Pairing format: 1 vs 24, 2 vs 23, ..., 12 vs 13
        cl_teams = standings[:24]
        for i in range(12):
            team1 = cl_teams[i]
            team2 = cl_teams[23 - i]
            db.add_playoff_pairing(
                'Champions League',
                team1['name'], team2['name'],
                i + 1, 24 - i
            )

        # Europa League playoffs: positions 25-48 (12 pairings)
        el_teams = standings[24:48]
        for i in range(12):
            team1 = el_teams[i]
            team2 = el_teams[23 - i]
            db.add_playoff_pairing(
                'Europa League',
                team1['name'], team2['name'],
                25 + i, 48 - i
            )

        # Conference League playoffs: positions 49-80 (16 pairings)
        conf_teams = standings[48:80]
        for i in range(16):
            team1 = conf_teams[i]
            team2 = conf_teams[31 - i]
            db.add_playoff_pairing(
                'Conference League',
                team1['name'], team2['name'],
                49 + i, 80 - i
            )

        return jsonify({
            'success': True,
            'message': 'Playoff pairings generated',
            'champions_league_matches': 12,
            'europa_league_matches': 12,
            'conference_league_matches': 16
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playoffs', methods=['GET'])
def get_playoffs():
    """Get playoff pairings"""
    try:
        playoffs = db.get_playoffs()

        # Enrich with team rankings
        for competition, matches in playoffs.items():
            for match in matches:
                team1_data = db.get_team_by_name(match['team1'])
                team2_data = db.get_team_by_name(match['team2'])

                match['team1_ranking'] = team1_data['ranking'] if team1_data else 0
                match['team2_ranking'] = team2_data['ranking'] if team2_data else 0

        return jsonify({'success': True, 'playoffs': playoffs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get tournament statistics"""
    try:
        current_round = db.get_current_round()
        total_pairings = len(db.get_pairings())
        simulated_pairings = len([p for p in db.get_pairings() if p['simulated']])
        unsimulated_pairings = total_pairings - simulated_pairings

        standings = db.get_standings()

        # Calculate some interesting stats
        total_goals = sum(team['goals_for'] for team in standings)
        total_matches = sum(team['played'] for team in standings) // 2

        avg_goals_per_match = round(total_goals / total_matches, 2) if total_matches > 0 else 0

        return jsonify({
            'success': True,
            'stats': {
                'current_round': current_round,
                'total_teams': len(standings),
                'total_matches': total_matches,
                'total_goals': total_goals,
                'avg_goals_per_match': avg_goals_per_match,
                'unsimulated_pairings': unsimulated_pairings
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Check if database exists, if not initialize it
    if not os.path.exists(DB_PATH):
        print("Database not found. Initializing...")
        db.init_db()
        teams_data = [
            {
                'rank': team['Rank'],
                'name': team['Team'],
                'ranking': team['Ranking'],
                'country': ''
            }
            for team in initial_teams
        ]
        db.load_teams(teams_data)
        print(f"Database initialized with {len(teams_data)} teams")

    print("\n" + "="*60)
    print("🏆 Swiss Tournament Simulator")
    print("="*60)
    print(f"\n✓ Server starting on http://localhost:5000")
    print(f"✓ Database: {DB_PATH}")
    print(f"✓ Teams loaded: {len(db.get_all_teams())}")
    print("\n" + "="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
