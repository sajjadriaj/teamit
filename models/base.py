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
            position = [pos for pos, rating in ratings.items() if rating == max_rating][
                0
            ]
            positions[player] = position
        return positions

    # def print_teams(self, team_name, team, positions):
    #     print(f"{team_name}:")
    #     position_players = {"forward": [], "midfielder": [], "defender": []}
    #     position_scores = {"forward": 0, "midfielder": 0, "defender": 0}

    #     for player, position in positions.items():
    #         position_players[position].append(player)
    #         position_scores[position] += team[player][position]

    #     for position in ["forward", "midfielder", "defender"]:
    #         print(f"  {position.capitalize()}:")
    #         for player in position_players[position]:
    #             print(f"    - {player}")
    #         print(
    #             f"    Overall {position.capitalize()} Score: {position_scores[position]}"
    #         )

    #     print("Balance Score:", self.calculate_balance_score(team))
    #     print()

    def formulate_teams(self, algorithm):
        best_team1, best_team2 = algorithm.run()
        positions_team1 = self.determine_positions(best_team1)
        positions_team2 = self.determine_positions(best_team2)

        # Get balance scores for each team
        balance_score1 = self.calculate_balance_score(best_team1)
        balance_score2 = self.calculate_balance_score(best_team2)

        return {
            "Team 1": {
                "team": best_team1,
                "positions": positions_team1,
                "balance_score": balance_score1,
            },
            "Team 2": {
                "team": best_team2,
                "positions": positions_team2,
                "balance_score": balance_score2,
            },
        }

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
        self.team1 = {}
        self.team2 = {}
        self.best_teams = None

    @abstractmethod
    def select_players_to_swap(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def swap_players(self, player1, player2):
        team1_player = self.team1.pop(player1)
        team2_player = self.team2.pop(player2)
        self.team1[player2] = team2_player
        self.team2[player1] = team1_player

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

    def initialize_teams(self):
        self.team1 = {}
        self.team2 = {}
        player_list = list(self.players.items())
        random.shuffle(player_list)

        for i, (player, skills) in enumerate(player_list):
            if i % 2 == 0:
                self.team1[player] = skills
            else:
                self.team2[player] = skills

    def evaluate_swap(self, player1, player2):
        current_team1 = dict(self.team1)
        current_team2 = dict(self.team2)

        self.swap_players(player1, player2)

        if self.has_two_max_rated_players(self.team1) or self.has_two_max_rated_players(
            self.team2
        ):
            # Revert the swap if it violates the constraint
            self.team1 = current_team1
            self.team2 = current_team2
            return None

        new_balance = self.calculate_balance_score(
            self.team1
        ) + self.calculate_balance_score(self.team2)
        self.team1 = current_team1
        self.team2 = current_team2

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
