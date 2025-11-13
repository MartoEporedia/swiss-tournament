"""
Match simulation engine for Swiss Tournament
Uses improved algorithm with Poisson distribution for realistic football scores
"""

import random
import math
from typing import Tuple, Dict


class MatchSimulator:
    """Simulates football matches based on team rankings"""

    def __init__(self):
        """Initialize simulator with constants"""
        # Base expected goals for an average team
        self.BASE_GOALS = 1.3

        # Ranking scale factor (higher = more impact from ranking difference)
        self.RANKING_FACTOR = 0.015

        # Home advantage factor (in neutral venues like European competitions)
        self.HOME_ADVANTAGE = 0.05

    def calculate_expected_goals(self, ranking: int, opponent_ranking: int,
                                 is_home: bool = False) -> float:
        """
        Calculate expected goals using ranking difference

        Args:
            ranking: Team's UEFA ranking (higher = stronger)
            opponent_ranking: Opponent's UEFA ranking
            is_home: Whether team is playing at home

        Returns:
            Expected goals for the team
        """
        # Ranking difference (positive = team is stronger)
        rank_diff = ranking - opponent_ranking

        # Base expected goals adjusted by ranking
        # Stronger teams (higher ranking) score more
        expected_goals = self.BASE_GOALS + (rank_diff * self.RANKING_FACTOR)

        # Add small home advantage if applicable
        if is_home:
            expected_goals += self.HOME_ADVANTAGE

        # Ensure expected goals is reasonable (between 0.3 and 4.0)
        expected_goals = max(0.3, min(4.0, expected_goals))

        return expected_goals

    def poisson_probability(self, k: int, lambda_val: float) -> float:
        """
        Calculate Poisson probability P(X = k)

        Args:
            k: Number of goals
            lambda_val: Expected number of goals (lambda parameter)

        Returns:
            Probability of scoring exactly k goals
        """
        if lambda_val <= 0:
            return 1.0 if k == 0 else 0.0

        # P(X = k) = (λ^k * e^(-λ)) / k!
        try:
            probability = (math.pow(lambda_val, k) * math.exp(-lambda_val)) / math.factorial(k)
            return probability
        except (OverflowError, ValueError):
            # Handle edge cases
            return 0.0

    def generate_goals_poisson(self, expected_goals: float) -> int:
        """
        Generate number of goals using Poisson distribution

        Args:
            expected_goals: Expected number of goals (lambda)

        Returns:
            Number of goals scored
        """
        # Generate random value [0, 1)
        u = random.random()

        # Use inverse CDF method for Poisson distribution
        cumulative_prob = 0.0
        k = 0

        # Find k where cumulative probability exceeds u
        while cumulative_prob < u and k < 15:  # Cap at 15 goals for performance
            cumulative_prob += self.poisson_probability(k, expected_goals)
            if cumulative_prob < u:
                k += 1

        return k

    def calculate_match_probabilities(self, ranking1: int, ranking2: int) -> Tuple[float, float, float]:
        """
        Calculate win/draw/loss probabilities based on expected goals

        Args:
            ranking1: First team's ranking
            ranking2: Second team's ranking

        Returns:
            Tuple of (win_prob_team1, draw_prob, win_prob_team2) in percentage
        """
        # Calculate expected goals for both teams
        exp_goals1 = self.calculate_expected_goals(ranking1, ranking2)
        exp_goals2 = self.calculate_expected_goals(ranking2, ranking1)

        # Calculate probabilities for all score combinations up to 10 goals
        win_prob = 0.0
        draw_prob = 0.0
        lose_prob = 0.0

        for goals1 in range(11):
            prob1 = self.poisson_probability(goals1, exp_goals1)

            for goals2 in range(11):
                prob2 = self.poisson_probability(goals2, exp_goals2)
                joint_prob = prob1 * prob2

                if goals1 > goals2:
                    win_prob += joint_prob
                elif goals1 == goals2:
                    draw_prob += joint_prob
                else:
                    lose_prob += joint_prob

        # Convert to percentages
        total = win_prob + draw_prob + lose_prob
        if total > 0:
            win_prob = (win_prob / total) * 100
            draw_prob = (draw_prob / total) * 100
            lose_prob = (lose_prob / total) * 100
        else:
            # Fallback to equal probabilities
            win_prob = draw_prob = lose_prob = 33.33

        return win_prob, draw_prob, lose_prob

    def simulate_match(self, team1_name: str, team1_ranking: int,
                      team2_name: str, team2_ranking: int) -> Tuple[int, int, Dict]:
        """
        Simulate a match between two teams

        Args:
            team1_name: Name of first team
            team1_ranking: Ranking of first team
            team2_name: Name of second team
            team2_ranking: Ranking of second team

        Returns:
            Tuple of (goals_team1, goals_team2, stats_dict)
        """
        # Calculate expected goals for both teams
        exp_goals1 = self.calculate_expected_goals(team1_ranking, team2_ranking)
        exp_goals2 = self.calculate_expected_goals(team2_ranking, team1_ranking)

        # Generate goals using Poisson distribution
        goals1 = self.generate_goals_poisson(exp_goals1)
        goals2 = self.generate_goals_poisson(exp_goals2)

        # Calculate match probabilities for stats
        win_prob, draw_prob, lose_prob = self.calculate_match_probabilities(
            team1_ranking, team2_ranking
        )

        # Compile statistics
        stats = {
            'expected_goals_team1': round(exp_goals1, 2),
            'expected_goals_team2': round(exp_goals2, 2),
            'win_probability_team1': round(win_prob, 1),
            'draw_probability': round(draw_prob, 1),
            'win_probability_team2': round(lose_prob, 1),
            'ranking_difference': team1_ranking - team2_ranking
        }

        return goals1, goals2, stats

    def simulate_multiple_matches(self, matches: list) -> list:
        """
        Simulate multiple matches at once

        Args:
            matches: List of match tuples (team1_name, team1_ranking, team2_name, team2_ranking)

        Returns:
            List of results with goals and stats
        """
        results = []

        for match in matches:
            team1_name, team1_ranking, team2_name, team2_ranking = match
            goals1, goals2, stats = self.simulate_match(
                team1_name, team1_ranking, team2_name, team2_ranking
            )

            results.append({
                'team1': team1_name,
                'team2': team2_name,
                'goals1': goals1,
                'goals2': goals2,
                'stats': stats
            })

        return results

    def get_ranking_impact_info(self, ranking_diff: int) -> str:
        """
        Get human-readable description of ranking impact

        Args:
            ranking_diff: Difference in rankings (team1 - team2)

        Returns:
            Description string
        """
        abs_diff = abs(ranking_diff)

        if abs_diff < 10:
            return "Very evenly matched teams"
        elif abs_diff < 30:
            return "Slight advantage to higher-ranked team"
        elif abs_diff < 50:
            return "Moderate advantage to higher-ranked team"
        elif abs_diff < 80:
            return "Strong advantage to higher-ranked team"
        else:
            return "Very strong advantage to higher-ranked team"
