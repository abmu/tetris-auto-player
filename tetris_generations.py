from adversary import RandomAdversary
from board import Board
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, BLOCK_LIMIT
from exceptions import BlockLimitException
from player import SelectedPlayer

from copy import deepcopy
from math import exp
import random
import time
from multiprocessing import Pool

def get_median_score(score_arr):
    arr_len = len(score_arr)
    index = (arr_len - 1) // 2

    if arr_len % 2 == 0:
        return (score_arr[index] + score_arr[index + 1]) / 2
    return score_arr[index]

def get_mean_score(score_arr):
    return sum(score_arr) / len(score_arr)

def get_random_decimal():
    # generate deciaml between -1 and 1
    #return round(-1 + (random.random() * 2), 4)

    # generate decimal between 0 and 1
    return round(random.random(), 4)

def initialise_population(pop_arr, pop_size, start_id=1):
    #a= 0.0063, b= 0.2904, c=-0.9878, d=-0.1713, e= 0.0000, f= 0.0000, g=-0.2441, h= 0.0000, i= 0.1301, j= 1.0000
    weight_total_height = [0.0000, 0.0063]
    weight_lines = [0.2904]
    weight_holes = [-0.9878, -1.0000]
    weight_bumpiness = [-0.1713, -0.1475]
    weight_not_tetris = [-0.2441]
    weight_bump4 = [0.1301]
    weight_tetris = [1.0000]

    individual_id = start_id
    for _ in range(pop_size):
        individual = {
            'id': individual_id,
            'scores': [],
            'median_score': 0,
            'mean_score': 0,
            'weight_total_height': 0,
            'weight_lines': 0,
            'weight_holes': -get_random_decimal(),
            'weight_bumpiness': -get_random_decimal(),
            'weight_max_height': 0,
            'weight_delta_height': 0,
            'weight_not_tetris': -get_random_decimal(),
            'weight_empty_last_col': 0,
            'weight_bump4': get_random_decimal(),
            'weight_tetris': get_random_decimal() #random.choice(weight_tetris)
        }
        pop_arr.append(individual)
        individual_id += 1

def ga_new_gen(pop_arr, pop_size, next_id):
    """
    Use genetic algorithm method to generate a new generation
    """
    parent_ratio = 0.5 # only top half will create children
    best_of_pop = pop_arr[:round(parent_ratio*pop_size)] # pop_arr is already sorted

    children = []
    keep_ratio = 0.2
    for i in range(round(keep_ratio*pop_size)):
        pop_arr[i]['scores'] = []
        pop_arr[i]['median_score'] = 0
        pop_arr[i]['mean_score'] = 0
        children.append(pop_arr[i])

    mutation_rate = 0.25
    mutation_step = 0.10
    for _ in range(round(keep_ratio*pop_size), pop_size):
        parent_1 = random.choice(best_of_pop)
        parent_2 = random.choice(best_of_pop)
        child_individual = {
            'id': next_id,
            'scores': [],
            'median_score': 0,
            'mean_score': 0,
            'weight_total_height': 0,
            'weight_lines': 0,
            'weight_holes': 0,
            'weight_bumpiness': 0,
            'weight_max_height': 0,
            'weight_delta_height': 0,
            'weight_not_tetris': 0,
            'weight_empty_last_col': 0,
            'weight_bump4': 0,
            'weight_tetris': 0
        }
        next_id += 1

        for key in child_individual:
            if key in ['id', 'scores', 'median_score', 'mean_score', 'weight_total_height', 'weight_delta_height', 'weight_empty_last_col']:
                continue
            possible_values = [parent_1[key], parent_2[key]]
            child_individual[key] = random.choice(possible_values)

            if random.random() < mutation_rate:
                child_individual[key] = round(child_individual[key] + random.random() * mutation_step * 2 - mutation_step, 4)

        children.append(child_individual)
    return children

def find(lst, key, value):
    for i, individual in enumerate(lst):
        if individual[key] == value:
            return i
    return None

def sa_new_gen(base_pop, curr_pop, pop_size, fitness_attr, temperature, mutation_rate, mutation_step):
    """
    Use simulated annealing method to generate a new generation
    """
    new_base_pop = []
    new_curr_pop = []

    keep_ratio = 0.2
    keep_limit = round(keep_ratio*pop_size)

    for i in range(pop_size):
        curr_id = curr_pop[i]['id']
        curr_individual = curr_pop[i]
        prev_id_index = find(base_pop, 'id', curr_id)
        prev_individual = base_pop[prev_id_index]

        new_base_individual = deepcopy(prev_individual)
        if curr_individual[fitness_attr] > prev_individual[fitness_attr]:
            new_base_individual = deepcopy(curr_individual)
        else:
            # ChatGPT was used to get code for probability
            probability = exp(-(prev_individual[fitness_attr] - curr_individual[fitness_attr]) / temperature)
            if random.random() < probability and i >= keep_limit:
                new_base_individual = deepcopy(curr_individual)
        new_base_pop.append(new_base_individual)
        
        new_curr_individual = deepcopy(new_base_individual)
        for key in new_curr_individual:
            if key in ['id', 'scores', 'median_score', 'mean_score', 'weight_total_height', 'weight_delta_height', 'weight_empty_last_col']:
                continue
            
            if random.random() < mutation_rate:
                mutation_amt = random.random() * mutation_step * 2 - mutation_step
                
                # while round(new_curr_individual[key] + mutation_amt, 4) > 1 or round(new_curr_individual[key] + mutation_amt, 4) < -1:
                #     mutation_amt = random.random() * mutation_step * 2 - mutation_step

                if round(new_curr_individual[key] + mutation_amt, 4) > 1:
                    new_curr_individual[key] = 1
                elif round(new_curr_individual[key] + mutation_amt, 4) < -1:
                    new_curr_individual[key] = -1
                else:
                    new_curr_individual[key] = round(new_curr_individual[key] + mutation_amt, 4)

        new_curr_pop.append(new_curr_individual)

    return new_base_pop, new_curr_pop

def run_game(game_num, total_games, individual, seed):
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(seed + game_num, BLOCK_LIMIT)

    player = SelectedPlayer(
        individual['weight_total_height'],
        individual['weight_lines'],
        individual['weight_holes'],
        individual['weight_bumpiness'],
        individual['weight_max_height'],
        individual['weight_delta_height'],
        individual['weight_not_tetris'],
        individual['weight_empty_last_col'],
        individual['weight_bump4'],
        individual['weight_tetris']
    )

    try:
        for move in board.run(player, adversary):
            pass
        print("Game lost")
    except BlockLimitException:
        print(f"Out of blocks ({BLOCK_LIMIT})")
    except KeyboardInterrupt:
        pass
    
    print(f"Game: {game_num+1}/{total_games}\nScore: {board.score}\n")
    
    return board.score

# run 'ulimit -n 999999' first, and clear generations.txt file
# for better performance, exectue the script with 'pypy3 tetris_generations.py'
if __name__ == '__main__':
    method = 'ga' # simulated annealing (sa) or genetic algorithm (ga)
    generations = 50
    population = []
    population_size = 100
    games_per_individual = 5
    fitness_attribute = 'mean_score'
    start_id = 1
    initialise_population(population, population_size, start_id)
    next_id = start_id + population_size

    # simulated annealing
    base_population = deepcopy(population)
    temperature = 1800
    mutation_rate = 0.95
    mutation_step = 0.40
    cooling_rate = 0.95

    cpu_cores = 5
    with Pool(cpu_cores) as pool:
        for i in range(generations):
            seed = DEFAULT_SEED + i*games_per_individual
            
            for j in range(population_size):
                start_time = time.time()
                
                individual = population[j]
                scores = sorted(pool.starmap(run_game, [(game_num, games_per_individual, individual, seed) for game_num in range(games_per_individual)]))

                population[j]['scores'] = scores
                population[j]['mean_score'] = get_mean_score(scores)
                population[j]['median_score'] = get_median_score(scores)

                print(f"========STATS========\nGeneration: {i+1}/{generations}\nIndividual: {j+1}/{population_size}\nGames: {games_per_individual}\nTime taken: {round(time.time() - start_time, 3)}sec\n")
                for key in population[j]:
                    print(f"{key}: {population[j][key]}")
                print("=====================\n\n\n")

            population = sorted(population, key=lambda d: d[fitness_attribute], reverse=True)
            with open(f"./generations/generation_{i+1}.txt","a+") as f:
                for individual in population:
                    f.write(f"{individual}\n")

            # population must be sorted first
            if method == 'ga': # genetic algorithm
                population = ga_new_gen(population, population_size, next_id)
                next_id += population_size
            else: # simulated annealing
                base_population, population = sa_new_gen(base_population, population, population_size, fitness_attribute, temperature, mutation_rate, mutation_step)
                temperature *= cooling_rate
                mutation_rate *= cooling_rate
                mutation_step *= cooling_rate