import random
import math
from abc import ABC, abstractmethod


class TeamFormulator:
    def __init__(self, players):
        self.players = players

    def determine_positions(self, team):
        positions = {}
        for player, ratings in team.items():
            max_rating = max(ratings.values())
            position = [pos for pos, rating in ratings.items() if rating == max_rating][0]
            positions[player] = position
        return positions

    def formulate_teams(self, algorithm):
        best_teams = algorithm.run()
        results = {}
        for i, team in enumerate(best_teams):
            positions = self.determine_positions(team)
            balance_score = self.calculate_balance_score(team)
            results[f"Team {i + 1}"] = {
                "team": team,
                "positions": positions,
                "balance_score": balance_score,
            }
        return results

    def calculate_balance_score(self, team):
        scores = {"forward": 0, "midfielder": 0, "defender": 0}
        for ratings in team.values():
            for position in scores:
                scores[position] += ratings[position]
        balance_score = max(scores.values()) - min(scores.values())
        return balance_score


class BanditAlgorithm(ABC):
    def __init__(self, players, iterations):
        self.players = players
        self.iterations = iterations
        self.teams = []

    @abstractmethod
    def select_players_to_swap(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def swap_players(self, team1_idx, team2_idx, player1, player2):
        self.teams[team1_idx][player1], self.teams[team2_idx][player2] = (
            self.teams[team2_idx][player2],
            self.teams[team1_idx][player1],
        )

    def calculate_balance_score(self, team):
        scores = {"forward": 0, "midfielder": 0, "defender": 0}
        for ratings in team.values():
            for position in scores:
                scores[position] += ratings[position]
        balance_score = max(scores.values()) - min(scores.values())
        return balance_score

    def has_two_max_rated_players(self, team):
        max_rated_positions = set()
        for ratings in team.values():
            for position, rating in ratings.items():
                if rating == 10:
                    if position in max_rated_positions:
                        return True
                    max_rated_positions.add(position)
        return False

    def initialize_teams(self, num_teams):
        self.teams = [{} for _ in range(num_teams)]
        player_list = list(self.players.items())
        random.shuffle(player_list)

        for i, (player, skills) in enumerate(player_list):
            self.teams[i % num_teams][player] = skills

    def evaluate_swap(self, team1_idx, team2_idx, player1, player2):
        current_teams = [dict(team) for team in self.teams]

        self.swap_players(team1_idx, team2_idx, player1, player2)

        if any(self.has_two_max_rated_players(team) for team in self.teams):
            # Revert the swap if it violates the constraint
            self.teams = current_teams
            return None

        new_balance = sum(self.calculate_balance_score(team) for team in self.teams)
        self.teams = current_teams

        return new_balance


class EvolutionaryAlgorithm(ABC):
    def __init__(self, players, iterations):
        self.players = players
        self.iterations = iterations

    @abstractmethod
    def initialize_population(self):
        pass

    @abstractmethod
    def fitness(self, individual):
        pass

    @abstractmethod
    def select_parents(self):
        pass

    @abstractmethod
    def reproduce(self, parent1, parent2):
        pass

    @abstractmethod
    def mutate(self, individual):
        pass

    @abstractmethod
    def run(self):
        pass
