# Tournament Simulator

A PyQt5-based application to simulate a Swiss-style tournament. The application allows users to generate team pairings based on similar scores, simulate match results, and view categorized standings. The tournament simulation includes probability-based match outcomes for added realism.

## Features

- **Swiss-Style Pairing**: Pairs teams with similar scores, ensuring they haven't faced each other previously.
- **Match Simulation**: Simulates matches with outcomes influenced by team rankings, incorporating win/loss probabilities.
- **Standings and Categories**: Displays standings by categories: Champions League, Europa League, Conference League, and Relegation.
- **Database Reset**: Allows for a fresh start by resetting the tournament database.
- **User-Friendly GUI**: Built with PyQt5, including controls for each step (e.g., creating pairings, simulating matches, viewing standings).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MartoEporedia/swiss-tournament.git
   cd swiss-tournament
   ```

2.	**Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.	**Set up the database**:
    Run the initial database setup script before launching the application:
    ```bash
    python create_db.py
    ```

4.	**Launch the application**:
    ```bash
    python main.py
    ```
## Usage

- **Create Pairings**: Generates the next round of pairings based on team scores and previous matches.
- **Simulate Match**: Simulates matches for all pairings, with probabilities based on team rankings.
- **Show Standings**: Displays the current standings in categories for an organized overview.
- **Show All Pairings**: Shows all pairings and their outcomes, providing a full history of the tournament.
- **Reset DB**: Resets the database for a fresh tournament start.

## Requirements

- Python 3.x
- PyQt5
- Pandas

All dependencies can be installed using the `requirements.txt` file.

## How It Works

1. **Pairing Algorithm**: Matches teams with similar scores, ensuring variety by checking past pairings and prioritizing teams that haven’t faced each other.
2. **Match Simulation**: Calculates the outcome of each match with probabilities based on the ranking difference between teams.
3. **Standings**: Divides teams into categories based on their points, providing a ranked list within Champions League, Europa League, Conference League, and Relegation.

## Example Workflow

1.	**Create Pairings** - Start a new round and pair teams based on their current standings.
2.	**Simulate Match** - Run simulations for each pairing and update standings.
3.	**Show Standings** - View current standings and categories.
4.	**Repeat** - Continue creating pairings and simulating rounds until the tournament ends.

## File Structure

	•	main.py: Contains the main application code with the PyQt5 GUI.
	•	create_db.py: Initializes the database and defines the required tables.
	•	requirements.txt: List of required dependencies.

## Database

The application uses SQLite to store team data, pairings, and results, allowing you to reset or continue simulations easily.

## License

This project is licensed under the MIT License.
