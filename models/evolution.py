import random
from models.base import EvolutionaryAlgorithm


class GeneticAlgorithm(EvolutionaryAlgorithm):
    def __init__(self, players, iterations, population_size=50, mutation_rate=0.1):
        super().__init__(players, iterations)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []

    def initialize_population(self):
        self.population = []
        player_list = list(self.players.items())
        for _ in range(self.population_size):
            random.shuffle(player_list)
            mid_point = len(player_list) // 2
            team1 = dict(player_list[:mid_point])
            team2 = dict(player_list[mid_point:])
            self.population.append((team1, team2))

    def fitness(self, individual):
        team1, team2 = individual
        return self.calculate_balance_score(team1) + self.calculate_balance_score(team2)

    def select_parents(self):
        return random.sample(self.population, 2)

    def reproduce(self, parent1, parent2):
        total_players = len(parent1[0]) + len(parent1[1])
        break_point = total_players // 2
        shuffled_players = list(parent1[0].items()) + list(parent2[1].items())
        random.shuffle(shuffled_players)
        child1_team1 = dict(shuffled_players[:break_point])
        child1_team2 = dict(shuffled_players[break_point:])
        self.validate_teams(child1_team1, child1_team2)
        return (child1_team1, child1_team2)

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            team1, team2 = individual
            if not team1 or not team2:
                return
            player1 = random.choice(list(team1.keys()))
            player2 = random.choice(list(team2.keys()))
            if player1 in team2 and player2 in team1:
                team1[player2], team2[player1] = team2.pop(player1), team1.pop(player2)
            self.validate_teams(team1, team2)

    def run(self):
        self.initialize_population()
        for _ in range(self.iterations):
            new_population = []
            for _ in range(len(self.population)):
                parent1, parent2 = self.select_parents()
                child1 = self.reproduce(parent1, parent2)
                self.mutate(child1)
                new_population.append(child1)
            self.population = new_population
        best_solution = min(self.population, key=self.fitness)
        return best_solution

    def validate_teams(self, team1, team2):
        if len(team1) > len(team2) + 1:
            # Move player from team1 to team2
            keys = list(team1.keys())
            for key in keys:
                team2[key] = team1.pop(key)
                if len(team1) <= len(team2) + 1:
                    break
        elif len(team2) > len(team1) + 1:
            # Move player from team2 to team1
            keys = list(team2.keys())
            for key in keys:
                team1[key] = team2.pop(key)
                if len(team2) <= len(team1) + 1:
                    break

    def calculate_balance_score(self, team):
        scores = {"forward": 0, "midfielder": 0, "defense": 0}
        for ratings in team.values():
            for position in scores:
                scores[position] += ratings[position]
        return max(scores.values()) - min(scores.values())
