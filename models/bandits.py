from models.base import BanditAlgorithm, EvolutionaryAlgorithm
import random
import numpy as np
import math


class EpsilonGreedy(BanditAlgorithm):
    def __init__(self, players, iterations, epsilon=0.1):
        super().__init__(players, iterations)
        self.epsilon = epsilon

    def select_players_to_swap(self):
        if random.random() < self.epsilon:
            # Explore: select random players to swap
            player1 = random.choice(list(self.team1.keys()))
            player2 = random.choice(list(self.team2.keys()))
        else:
            # Exploit: select the best swap based on balance score
            valid_swaps = self.get_valid_swaps()
            if valid_swaps:
                player1, player2, _ = min(valid_swaps, key=lambda x: x[2])
            else:
                player1 = random.choice(list(self.team1.keys()))
                player2 = random.choice(list(self.team2.keys()))

        return player1, player2

    def get_valid_swaps(self):
        valid_swaps = []
        team1_players = list(self.team1.keys())
        team2_players = list(self.team2.keys())

        for player1 in team1_players:
            for player2 in team2_players:
                new_balance = self.evaluate_swap(player1, player2)
                if new_balance is not None:
                    valid_swaps.append((player1, player2, new_balance))
        return valid_swaps

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = (dict(self.team1), dict(self.team2))

        for _ in range(self.iterations):
            player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_team1 = dict(self.team1)
            current_team2 = dict(self.team2)

            self.swap_players(player1, player2)

            if self.has_two_max_rated_players(
                self.team1
            ) or self.has_two_max_rated_players(self.team2):
                # Revert the swap if it violates the constraint
                self.team1 = current_team1
                self.team2 = current_team2
                continue

            new_balance = self.calculate_balance_score(
                self.team1
            ) + self.calculate_balance_score(self.team2)

            if new_balance < best_balance:
                best_balance = new_balance
                self.best_teams = (dict(self.team1), dict(self.team2))
            else:
                # Revert the swap if it doesn't improve the balance
                self.team1 = current_team1
                self.team2 = current_team2

        return self.best_teams


class UCB(BanditAlgorithm):
    def __init__(self, players, iterations, exploration_factor=1.0):
        super().__init__(players, iterations)
        self.exploration_factor = exploration_factor
        self.swap_counts = {}
        self.swap_rewards = {}

    def select_players_to_swap(self):
        team1_players = list(self.team1.keys())
        team2_players = list(self.team2.keys())

        # Calculate UCB scores for each swap
        ucb_scores = {}
        total_count = sum(self.swap_counts.values())

        for player1 in team1_players:
            for player2 in team2_players:
                swap = (player1, player2)
                if swap not in self.swap_counts:
                    self.swap_counts[swap] = 0
                    self.swap_rewards[swap] = 0

                count = self.swap_counts[swap]
                reward = self.swap_rewards[swap]
                if count == 0:
                    ucb_score = float("inf")
                else:
                    ucb_score = reward / count + self.exploration_factor * math.sqrt(
                        math.log(total_count) / count
                    )
                ucb_scores[swap] = ucb_score

        # Select the swap with the highest UCB score
        if ucb_scores:
            best_swap = max(ucb_scores, key=ucb_scores.get)
            player1, player2 = best_swap
        else:
            player1 = random.choice(team1_players)
            player2 = random.choice(team2_players)

        return player1, player2

    def update_swap_stats(self, player1, player2, reward):
        swap = (player1, player2)
        self.swap_counts[swap] += 1
        self.swap_rewards[swap] += reward

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = (dict(self.team1), dict(self.team2))

        for _ in range(self.iterations):
            player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_team1 = dict(self.team1)
            current_team2 = dict(self.team2)

            self.swap_players(player1, player2)

            if self.has_two_max_rated_players(
                self.team1
            ) or self.has_two_max_rated_players(self.team2):
                # Revert the swap if it violates the constraint
                self.team1 = current_team1
                self.team2 = current_team2
                reward = 0
            else:
                new_balance = self.calculate_balance_score(
                    self.team1
                ) + self.calculate_balance_score(self.team2)
                reward = -new_balance  # Negative reward to minimize balance score

                if new_balance < best_balance:
                    best_balance = new_balance
                    self.best_teams = (dict(self.team1), dict(self.team2))
                else:
                    # Revert the swap if it doesn't improve the balance
                    self.team1 = current_team1
                    self.team2 = current_team2

            self.update_swap_stats(player1, player2, reward)

        return self.best_teams


class ThompsonSampling(BanditAlgorithm):
    def __init__(self, players, iterations, alpha=1, beta=1):
        super().__init__(players, iterations)
        self.alpha = alpha
        self.beta = beta
        self.swap_successes = {}
        self.swap_failures = {}

    def select_players_to_swap(self):
        team1_players = list(self.team1.keys())
        team2_players = list(self.team2.keys())

        # Calculate Thompson Sampling scores for each swap
        thompson_scores = {}

        for player1 in team1_players:
            for player2 in team2_players:
                swap = (player1, player2)
                if swap not in self.swap_successes:
                    self.swap_successes[swap] = 0
                    self.swap_failures[swap] = 0

                successes = self.swap_successes[swap]
                failures = self.swap_failures[swap]
                thompson_score = np.random.beta(
                    self.alpha + successes, self.beta + failures
                )
                thompson_scores[swap] = thompson_score

        # Select the swap with the highest Thompson Sampling score
        if thompson_scores:
            best_swap = max(thompson_scores, key=thompson_scores.get)
            player1, player2 = best_swap
        else:
            player1 = random.choice(team1_players)
            player2 = random.choice(team2_players)

        return player1, player2

    def update_swap_stats(self, player1, player2, success):
        swap = (player1, player2)
        if success:
            self.swap_successes[swap] = self.swap_successes.get(swap, 0) + 1
        else:
            self.swap_failures[swap] = self.swap_failures.get(swap, 0) + 1

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = (dict(self.team1), dict(self.team2))

        for _ in range(self.iterations):
            player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_team1 = dict(self.team1)
            current_team2 = dict(self.team2)

            self.swap_players(player1, player2)

            if self.has_two_max_rated_players(
                self.team1
            ) or self.has_two_max_rated_players(self.team2):
                # Revert the swap if it violates the constraint
                self.team1 = current_team1
                self.team2 = current_team2
                success = False
            else:
                new_balance = self.calculate_balance_score(
                    self.team1
                ) + self.calculate_balance_score(self.team2)
                success = new_balance < best_balance

                if success:
                    best_balance = new_balance
                    self.best_teams = (dict(self.team1), dict(self.team2))
                else:
                    # Revert the swap if it doesn't improve the balance
                    self.team1 = current_team1
                    self.team2 = current_team2

            self.update_swap_stats(player1, player2, success)

        return self.best_teams
