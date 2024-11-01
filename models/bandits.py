from models.base import BanditAlgorithm, EvolutionaryAlgorithm
import random
import numpy as np
import math


class EpsilonGreedy(BanditAlgorithm):
    def __init__(self, players, iterations, epsilon=0.1, num_teams=2):
        super().__init__(players, iterations)
        self.epsilon = epsilon
        self.num_teams = num_teams
        self.teams = [{} for _ in range(num_teams)]

    def initialize_teams(self):
        # Initialize players randomly across teams without duplication
        players = list(self.players.items())
        random.shuffle(players)
        for i, player in enumerate(players):
            self.teams[i % self.num_teams][player[0]] = player[1]

    def select_players_to_swap(self):
        if random.random() < self.epsilon:
            # Explore: select random players to swap
            team1, team2 = random.sample(range(self.num_teams), 2)
            player1 = random.choice(list(self.teams[team1].keys()))
            player2 = random.choice(list(self.teams[team2].keys()))
        else:
            # Exploit: select the best swap based on balance score
            valid_swaps = self.get_valid_swaps()
            if valid_swaps:
                team1, team2, player1, player2, _ = min(valid_swaps, key=lambda x: x[4])
            else:
                team1, team2 = random.sample(range(self.num_teams), 2)
                player1 = random.choice(list(self.teams[team1].keys()))
                player2 = random.choice(list(self.teams[team2].keys()))

        return team1, team2, player1, player2

    def get_valid_swaps(self):
        valid_swaps = []
        for i, team1 in enumerate(self.teams):
            for j, team2 in enumerate(self.teams):
                if i >= j:
                    continue
                team1_keys = list(team1.keys())  # Convert to list to avoid modifying during iteration
                team2_keys = list(team2.keys())  # Convert to list to avoid modifying during iteration
                for player1 in team1_keys:
                    for player2 in team2_keys:
                        new_balance = self.evaluate_swap(i, j, player1, player2)
                        if new_balance is not None:
                            valid_swaps.append((i, j, player1, player2, new_balance))
        return valid_swaps

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = [dict(team) for team in self.teams]

        for _ in range(self.iterations):
            team1_idx, team2_idx, player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_teams = [dict(team) for team in self.teams]

            self.swap_players(team1_idx, team2_idx, player1, player2)

            if any(self.has_two_max_rated_players(team) for team in self.teams):
                # Revert the swap if it violates the constraint
                self.teams = current_teams
                continue

            new_balance = sum(self.calculate_balance_score(team) for team in self.teams)

            if new_balance < best_balance:
                best_balance = new_balance
                self.best_teams = [dict(team) for team in self.teams]
            else:
                # Revert the swap if it doesn't improve the balance
                self.teams = current_teams

        return self.best_teams

    def swap_players(self, team1_idx, team2_idx, player1, player2):
        self.teams[team1_idx][player1], self.teams[team2_idx][player2] = (
            self.teams[team2_idx].pop(player2),
            self.teams[team1_idx].pop(player1),
        )


class UCB(BanditAlgorithm):
    def __init__(self, players, iterations, exploration_factor=1.0, num_teams=2):
        super().__init__(players, iterations)
        self.exploration_factor = exploration_factor
        self.num_teams = num_teams
        self.teams = [{} for _ in range(num_teams)]
        self.swap_counts = {}
        self.swap_rewards = {}

    def initialize_teams(self):
        # Initialize players randomly across teams without duplication
        players = list(self.players.items())
        random.shuffle(players)
        for i, player in enumerate(players):
            self.teams[i % self.num_teams][player[0]] = player[1]

    def select_players_to_swap(self):
        team1_players = list(self.teams)
        total_count = sum(self.swap_counts.values())

        # Calculate UCB scores for each swap
        ucb_scores = {}

        for i in range(self.num_teams):
            for j in range(i + 1, self.num_teams):
                for player1 in self.teams[i].keys():
                    for player2 in self.teams[j].keys():
                        swap = (i, j, player1, player2)
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
            team1, team2, player1, player2 = best_swap
        else:
            team1, team2 = random.sample(range(self.num_teams), 2)
            player1 = random.choice(list(self.teams[team1].keys()))
            player2 = random.choice(list(self.teams[team2].keys()))

        return team1, team2, player1, player2

    def update_swap_stats(self, team1_idx, team2_idx, player1, player2, reward):
        swap = (team1_idx, team2_idx, player1, player2)
        self.swap_counts[swap] += 1
        self.swap_rewards[swap] += reward

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = [dict(team) for team in self.teams]

        for _ in range(self.iterations):
            team1_idx, team2_idx, player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_teams = [dict(team) for team in self.teams]

            self.swap_players(team1_idx, team2_idx, player1, player2)

            if any(self.has_two_max_rated_players(team) for team in self.teams):
                # Revert the swap if it violates the constraint
                self.teams = current_teams
                reward = 0
            else:
                new_balance = sum(self.calculate_balance_score(team) for team in self.teams)
                reward = -new_balance  # Negative reward to minimize balance score

                if new_balance < best_balance:
                    best_balance = new_balance
                    self.best_teams = [dict(team) for team in self.teams]
                else:
                    # Revert the swap if it doesn't improve the balance
                    self.teams = current_teams

            self.update_swap_stats(team1_idx, team2_idx, player1, player2, reward)

        return self.best_teams

    def swap_players(self, team1_idx, team2_idx, player1, player2):
        self.teams[team1_idx][player1], self.teams[team2_idx][player2] = (
            self.teams[team2_idx].pop(player2),
            self.teams[team1_idx].pop(player1),
        )


class ThompsonSampling(BanditAlgorithm):
    def __init__(self, players, iterations, alpha=1, beta=1, num_teams=2):
        super().__init__(players, iterations)
        self.alpha = alpha
        self.beta = beta
        self.num_teams = num_teams
        self.teams = [{} for _ in range(num_teams)]
        self.swap_successes = {}
        self.swap_failures = {}

    def initialize_teams(self):
        # Initialize players randomly across teams without duplication
        players = list(self.players.items())
        random.shuffle(players)
        for i, player in enumerate(players):
            self.teams[i % self.num_teams][player[0]] = player[1]

    def select_players_to_swap(self):
        thompson_scores = {}

        for i in range(self.num_teams):
            for j in range(i + 1, self.num_teams):
                for player1 in self.teams[i].keys():
                    for player2 in self.teams[j].keys():
                        swap = (i, j, player1, player2)
                        if swap not in self.swap_successes:
                            self.swap_successes[swap] = 0
                            self.swap_failures[swap] = 0

                        successes = self.swap_successes[swap]
                        failures = self.swap_failures[swap]
                        thompson_score = np.random.beta(self.alpha + successes, self.beta + failures)
                        thompson_scores[swap] = thompson_score

        # Select the swap with the highest Thompson Sampling score
        if thompson_scores:
            best_swap = max(thompson_scores, key=thompson_scores.get)
            team1, team2, player1, player2 = best_swap
        else:
            team1, team2 = random.sample(range(self.num_teams), 2)
            player1 = random.choice(list(self.teams[team1].keys()))
            player2 = random.choice(list(self.teams[team2].keys()))

        return team1, team2, player1, player2

    def update_swap_stats(self, team1_idx, team2_idx, player1, player2, success):
        swap = (team1_idx, team2_idx, player1, player2)
        if success:
            self.swap_successes[swap] += 1
        else:
            self.swap_failures[swap] += 1

    def run(self):
        self.initialize_teams()
        best_balance = float("inf")
        self.best_teams = [dict(team) for team in self.teams]

        for _ in range(self.iterations):
            team1_idx, team2_idx, player1, player2 = self.select_players_to_swap()

            # Store the current teams before swapping
            current_teams = [dict(team) for team in self.teams]

            self.swap_players(team1_idx, team2_idx, player1, player2)

            if any(self.has_two_max_rated_players(team) for team in self.teams):
                # Revert the swap if it violates the constraint
                self.teams = current_teams
                success = False
            else:
                new_balance = sum(self.calculate_balance_score(team) for team in self.teams)
                success = new_balance < best_balance

                if success:
                    best_balance = new_balance
                    self.best_teams = [dict(team) for team in self.teams]
                else:
                    # Revert the swap if it doesn't improve the balance
                    self.teams = current_teams

            self.update_swap_stats(team1_idx, team2_idx, player1, player2, success)

        return self.best_teams

    def swap_players(self, team1_idx, team2_idx, player1, player2):
        self.teams[team1_idx][player1], self.teams[team2_idx][player2] = (
            self.teams[team2_idx].pop(player2),
            self.teams[team1_idx].pop(player1),
        )

