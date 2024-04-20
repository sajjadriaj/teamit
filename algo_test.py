from models.bandits import EpsilonGreedy, UCB, ThompsonSampling
from models.evolution import GeneticAlgorithm
from models.base import TeamFormulator

players = {
    "El Riajo": {"forward": 5, "midfielder": 7, "defender": 3},
    "Nazmul Hoque Shayento": {"forward": 0, "midfielder": 6, "defender": 5},
    "Jubaer Hossain": {"forward": 3, "midfielder": 5, "defender": 6},
    "Syed Saqueb": {"forward": 4, "midfielder": 0, "defender": 6},
    "Nazmul Khan Shahan": {"forward": 0, "midfielder": 6, "defender": 8},
    "Ishmam Zabir": {"forward": 8, "midfielder": 6, "defender": 0},
    "Aurko Khandakar": {"forward": 7, "midfielder": 0, "defender": 3},
    "Mahmudul Hasan Razib": {"forward": 7, "midfielder": 6, "defender": 0},
    "Ahsan Z Khan": {"forward": 6, "midfielder": 7, "defender": 4},
    "Syed Shakib Sarwar": {"forward": 6, "midfielder": 0, "defender": 4},
    "Rayhan Hossain": {"forward": 3, "midfielder": 0, "defender": 5},
    "Shazzad Khan": {"forward": 0, "midfielder": 8, "defender": 0},
    "Kazi Abdul Muktadir": {"forward": 5, "midfielder": 5, "defender": 5},
    "SM Sohan": {"forward": 3, "midfielder": 6, "defender": 4},
    "Rupu Zaman": {"forward": 2, "midfielder": 0, "defender": 5},
    "Mashfiqui Rabbi Shuva": {"forward": 0, "midfielder": 0, "defender": 10},
    "Shajid Islam Amit": {"forward": 10, "midfielder": 0, "defender": 0},
    "Rownak Islam": {"forward": 2, "midfielder": 8, "defender": 3},
    "Enamul Haque": {"forward": 10, "midfielder": 7, "defender": 7},
    "Madhusudan Banik": {"forward": 3, "midfielder": 6, "defender": 4},
    "Syed Hafiz R": {"forward": 6, "midfielder": 7, "defender": 10},
    "Uzzal Sutradhar": {"forward": 3, "midfielder": 0, "defender": 3},
}

# Create an instance of TeamFormulator
formulator = TeamFormulator(players)

# Create an instance of EpsilonGreedy
# epsilon_greedy = EpsilonGreedy(players, iterations=1000, epsilon=0.1)

# # Formulate teams using the epsilon-greedy algorithm
# formulator.formulate_teams(epsilon_greedy)

# ucb = UCB(players, iterations=1000, exploration_factor=1.0)

# # Formulate teams using the UCB algorithm
# formulator.formulate_teams(ucb)


# Create an instance of ThompsonSampling
# thompson_sampling = ThompsonSampling(players, iterations=1000, alpha=1, beta=1)

# Formulate teams using the Thompson Sampling algorithm
# formulator.formulate_teams(thompson_sampling)

genetic_algorithm = GeneticAlgorithm(
    players, iterations=1000, population_size=30, mutation_rate=0.05
)

formulator.formulate_teams(genetic_algorithm)
