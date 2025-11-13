"""
UEFA Club Rankings Fetcher
Fetches updated club rankings from online sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict, Optional


class UEFARankingFetcher:
    """Fetches UEFA club rankings from online sources"""

    def __init__(self):
        """Initialize fetcher"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_from_kassiesa(self) -> Optional[List[Dict]]:
        """
        Fetch rankings from kassiesa.net (historical UEFA coefficient data)
        This is a backup/fallback source
        """
        try:
            url = "https://kassiesa.net/uefa/data/method5/crank2024.html"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            teams = []

            # Find the main table
            table = soup.find('table')
            if not table:
                return None

            rows = table.find_all('tr')[1:]  # Skip header

            for i, row in enumerate(rows[:96], 1):  # Get top 96 teams
                cols = row.find_all('td')
                if len(cols) >= 3:
                    team_name = cols[1].get_text(strip=True)
                    try:
                        # Coefficient is usually in the last column
                        ranking_text = cols[-1].get_text(strip=True)
                        ranking = float(re.sub(r'[^\d.]', '', ranking_text))
                    except:
                        ranking = 100 - i  # Fallback

                    teams.append({
                        'Rank': i,
                        'Team': team_name,
                        'Ranking': int(ranking)
                    })

            return teams if len(teams) >= 50 else None

        except Exception as e:
            print(f"Error fetching from kassiesa: {e}")
            return None

    def fetch_from_uefa_official(self) -> Optional[List[Dict]]:
        """
        Attempt to fetch from UEFA's official API (if accessible)
        Note: UEFA's API may require authentication or have CORS restrictions
        """
        try:
            # This is a placeholder - UEFA's actual API endpoint would go here
            # The endpoint may change or require authentication
            url = "https://www.uefa.com/api/v1/rankings/clubs"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                teams = []

                for i, club in enumerate(data.get('clubs', [])[:96], 1):
                    teams.append({
                        'Rank': i,
                        'Team': club.get('name', f'Team {i}'),
                        'Ranking': int(club.get('coefficient', 100 - i))
                    })

                return teams if len(teams) >= 50 else None

        except Exception as e:
            print(f"Error fetching from UEFA official: {e}")
            return None

    def fetch_from_transfermarkt(self) -> Optional[List[Dict]]:
        """
        Fetch top clubs from Transfermarkt (market value as proxy for strength)
        """
        try:
            url = "https://www.transfermarkt.com/statistik/wertvollstemannschaften"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            teams = []

            # Find team rows
            rows = soup.find_all('tr', class_=['odd', 'even'])

            for i, row in enumerate(rows[:96], 1):
                team_cell = row.find('td', class_='hauptlink')
                if team_cell:
                    team_name = team_cell.get_text(strip=True)

                    # Use inverse rank as ranking (top teams get higher scores)
                    ranking = 150 - i

                    teams.append({
                        'Rank': i,
                        'Team': team_name,
                        'Ranking': ranking
                    })

            return teams if len(teams) >= 50 else None

        except Exception as e:
            print(f"Error fetching from Transfermarkt: {e}")
            return None

    def get_fallback_rankings(self) -> List[Dict]:
        """
        Get fallback rankings if online sources fail
        Uses the current create_db.py data
        """
        from create_db import teams as fallback_teams
        return fallback_teams

    def fetch_rankings(self, use_fallback: bool = True) -> List[Dict]:
        """
        Fetch rankings from multiple sources with fallback

        Args:
            use_fallback: If True, use local data if online sources fail

        Returns:
            List of team dictionaries with Rank, Team, Ranking
        """
        print("🔍 Fetching UEFA rankings from online sources...")

        # Try multiple sources in order of preference
        sources = [
            ("UEFA Official", self.fetch_from_uefa_official),
            ("Kassiesa", self.fetch_from_kassiesa),
            ("Transfermarkt", self.fetch_from_transfermarkt),
        ]

        for source_name, fetch_func in sources:
            print(f"   Trying {source_name}...")
            try:
                teams = fetch_func()
                if teams and len(teams) >= 50:
                    print(f"   ✓ Successfully fetched {len(teams)} teams from {source_name}")
                    return teams
                else:
                    print(f"   ✗ {source_name} returned insufficient data")
            except Exception as e:
                print(f"   ✗ {source_name} failed: {e}")

        # Use fallback if requested
        if use_fallback:
            print("   ⚠ Using fallback rankings from local database")
            return self.get_fallback_rankings()
        else:
            raise Exception("Failed to fetch rankings from any source")

    def normalize_team_names(self, teams: List[Dict]) -> List[Dict]:
        """
        Normalize team names to match common formats

        Args:
            teams: List of teams with Team field

        Returns:
            Teams with normalized names
        """
        name_mappings = {
            'Man City': 'Manchester City',
            'Man United': 'Manchester United',
            'Man Utd': 'Manchester United',
            'Bayern Munich': 'Bayern Monaco',
            'Paris SG': 'Paris Saint-Germain',
            'PSG': 'Paris Saint-Germain',
            'Inter Milan': 'Inter',
            'AC Milan': 'Milan',
            'Atlético': 'Atletico Madrid',
            'Real Sociedad': 'Real Sociedad',
        }

        for team in teams:
            original_name = team['Team']
            team['Team'] = name_mappings.get(original_name, original_name)

        return teams


def fetch_latest_rankings() -> List[Dict]:
    """
    Convenience function to fetch latest rankings

    Returns:
        List of team dictionaries
    """
    fetcher = UEFARankingFetcher()
    teams = fetcher.fetch_rankings(use_fallback=True)
    teams = fetcher.normalize_team_names(teams)
    return teams


if __name__ == "__main__":
    # Test the fetcher
    print("\n" + "="*60)
    print("UEFA Rankings Fetcher - Test Mode")
    print("="*60 + "\n")

    try:
        teams = fetch_latest_rankings()

        print(f"\n✓ Fetched {len(teams)} teams\n")
        print("Top 10 teams:")
        print("-" * 60)

        for team in teams[:10]:
            print(f"{team['Rank']:2d}. {team['Team']:30s} | Ranking: {team['Ranking']}")

        print("-" * 60)
        print(f"\nBottom 5 teams:")

        for team in teams[-5:]:
            print(f"{team['Rank']:2d}. {team['Team']:30s} | Ranking: {team['Ranking']}")

        print("\n" + "="*60)

    except Exception as e:
        print(f"\n✗ Error: {e}\n")
