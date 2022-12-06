import itertools

import numpy as np
import random
import copy
import defineProblem, vehicles
from collections import namedtuple


class Chromosome:
    def __int__(self, vehicles):
        self.vehicles = vehicles


distances = defineProblem.distances
all_routes = defineProblem.all_routes


def create_init_population(size_of_population, routes, vehicles):
    population = []
    number_of_vehicles = len(vehicles)
    if number_of_vehicles > len(routes):
        number_of_vehicles = len(routes)

    if number_of_vehicles <= 0:
        return Exception('It is necessary to have at least one vehicle to solve this problem')

    if sum(vehicle.capacity for vehicle in vehicles) < sum(route.requirement for route in routes):
        return Exception('Chosen vehicles do not have capacity to serve the routes')

    if max(vehicle.capacity for vehicle in vehicles) < max(route.requirement for route in routes):
        return Exception('Chosen vehicles do not have capacity to serve the routes')

    routes.sort(key=lambda x: x.requirement, reverse=True)
    for i in range(size_of_population):
        # chromosome is a list of vehicles that will be used for the delivery and routes assigned to those vehicles
        chromosome = []
        vehicles_copy = copy.deepcopy(vehicles)

        # gene is one route (name and requirement)
        # go throw the sorted routes (desc); assign the route to the random vehicle (that is capable to serve the route)
        for route in routes:
            if route.city == 'DEPOT':
                depot = route
                continue
            appropriate_vehicles = list(filter(lambda x: x.capacity >= route.requirement, vehicles_copy))

            if len(appropriate_vehicles) == 0:
                return Exception('Chosen vehicles do not have capacity to serve the routes')

            chosen_vehicle = random.choice(appropriate_vehicles)
            chosen_vehicle.routes.append(route)
            chosen_vehicle.capacity -= route.requirement


        # go throw all the vehicles that has at least one assigned route, shuffle routes and add genes to chromosome
        vehicles_with_routes = list(filter(lambda x: len(x.routes) > 0, vehicles_copy))
        for genes in vehicles_with_routes:
            genes.capacity = [x.capacity for x in vehicles if x.vehicle_number == genes.vehicle_number][0]
            random.shuffle(genes.routes)
            # every vehicle needs to start from the depot point and to end there
            genes.routes.insert(0, depot)
            genes.routes.insert(len(genes.routes), depot)
            chromosome.append(genes)

        population.append(chromosome)

    return population


# the goal is to minimize the total distance travelled
# the fitness value is computed as a simple sum of lengths of individual routes
# every vehicle starts from the depot point and ends there
# criterion is the minimization
def fitness(population):
    fitness_values = []
    for chromosome in population:
        fitness_value = 0
        for vehicle in chromosome:
            for i in range(0, len(vehicle.routes)):
                if i == len(vehicle.routes) - 1:
                    break
                fitness_value += distances[vehicle.routes[i].city][vehicle.routes[i + 1].city]

        fitness_values.append(fitness_value)
    population_with_fitness = list(zip(population, fitness_values))
    sorted_population = sorted(population_with_fitness, key=lambda fitness_values: fitness_values[1])
    return sorted_population


def elitism(chromosomes, elitism_number):
    next_population = list(chromosomes[0:elitism_number])
    chromosomes = list(chromosomes[elitism_number:])
    return next_population, chromosomes


# roulette wheel selection
def selection(population, len_of_next_generation, elitism_num):
    population_for_selection = [chromosome for chromosome in population if chromosome is not None]
    previous_population = fitness(population_for_selection)
    chromosomes, values = zip(*previous_population)

    chosen_parents_by_elitism, chromosomes = elitism(previous_population, elitism_num)

    values = values[elitism_num:]
    population_fitness = sum([fitness for fitness in values])
    relative_fitness_values = [1 - (x / population_fitness) for x in values]
    # Computes for each chromosome the probability
    chromosome_probabilities = np.cumsum(relative_fitness_values)
    chromosome_probabilities /= chromosome_probabilities.sum()
    chromosome_probabilities = list(chromosome_probabilities)

    chromosomes = [chr[0] for chr in chromosomes]
    chosen_parents = []
    for i in range(len_of_next_generation):
        tmp = population[np.random.choice(len(chromosomes), p=chromosome_probabilities)]
        chosen_parents.append(tmp)

    chosen_parents_by_elitism = [chosen_parent[0] for chosen_parent in chosen_parents_by_elitism]
    return chosen_parents, chosen_parents_by_elitism


def determine_cross_points(converted_female):
    if len(converted_female) - 2 < 1:
        cross_point1 = 0
    else:
        cross_point1 = random.randint(1, (len(converted_female) - 2))

    if cross_point1 == 0:
        cross_point2 = random.randint(0, (len(converted_female) - 1))
    else:
        cross_point2 = random.randint(cross_point1 + 1, (len(converted_female) - 1))
    return cross_point1, cross_point2


def order_crossover_implementation(male, female, cross_point1, cross_point2):
    # convert chromosome into list
    # one chromosome will have list of all cities in order for every vehicle
    # later on we will match routes with vehicles
    converted_male = convert_into_chromosome(male, False)
    converted_female = convert_into_chromosome(female, False)

    if cross_point1 is None or cross_point2 is None:
        cross_point1, cross_point2 = determine_cross_points(converted_female)

    child = [None] * len(converted_female)

    # copy the routes between cross points from the female
    # in this part we know that constraints are going to be fulfilled
    for j in range(cross_point1, cross_point2 + 1):
        child[j] = converted_female[j]

    male_gene_index = cross_point2 + 1
    child_index = cross_point2 + 1
    while True:
        if all(elem is not None for elem in child):
            break
        if male_gene_index == len(converted_male):
            male_gene_index = 0
            continue
        if child_index == len(child):
            child_index = 0
        if converted_male[male_gene_index] not in child:
            child[child_index] = converted_male[male_gene_index]
            child_index += 1
        male_gene_index += 1

    vehicle_child = define_child_vehicles_in_crossover(child)

    restart_capacity(vehicle_child)

    return vehicle_child, cross_point1, cross_point2


def partially_mapped_crossover_implementation(male, female, cross_point1, cross_point2):
    # convert chromosome into list
    # one chromosome will have list of all cities in order for every vehicle
    # later on we will match routes with vehicles
    converted_male = convert_into_chromosome(male, False)
    converted_female = convert_into_chromosome(female, False)

    # define cross points
    if cross_point1 is None or cross_point2 is None:
        cross_point1, cross_point2 = determine_cross_points(converted_female)

    child1 = [None] * len(converted_female)
    child2 = [None] * len(converted_female)

    # define a matching section between two cross points of the two offspring
    matching_section = []
    Match = namedtuple('Match', ['female_gene', 'male_gene'])
    for j in range(cross_point1, cross_point2 + 1):
        child1[j] = converted_female[j]
        child2[j] = converted_male[j]
        match_to_add = Match(converted_female[j], converted_male[j])
        matching_section.append(match_to_add)

    for j in itertools.chain(range(0, cross_point1), range(cross_point2 + 1, len(converted_female))):
        if converted_male[j] not in child1:
            child1[j] = converted_male[j]
            child1[j]

        if converted_female[j] not in child2:
            child2[j] = converted_female[j]
            child2[j]

    if any(elem is None for elem in child1) or any(elem is None for elem in child2):

        def find_match(parent1, parent2, child, gene, observe_female_gene):
            if observe_female_gene:
                match = [el for el in matching_section if el.female_gene == gene][0]
                if match.male_gene not in child:
                    return match
                else:
                    return find_match(parent1, parent2, child, match.male_gene, True)
            else:
                match = [el for el in matching_section if el.male_gene == gene][0]
                if match.female_gene not in child:
                    return match
                else:
                    return find_match(parent1, parent2, child, match.female_gene, False)

        for j in range(0, len(child1)):
            if child1[j] is None:
                match = find_match(female, male, child1, converted_male[j], True)
                child1[j] = match.male_gene

            if child2[j] is None:
                match = find_match(male, female, child2, converted_female[j], False)
                child2[j] = match.female_gene

    vehicle_child1 = define_child_vehicles_in_crossover(child1)
    vehicle_child2 = define_child_vehicles_in_crossover(child2)

    restart_capacity(vehicle_child1)
    restart_capacity(vehicle_child2)

    return cross_point1, cross_point2, vehicle_child1, vehicle_child2


def define_child_vehicles_in_crossover(child):
    vehicle_child = copy.deepcopy(vehicles.all_vehicles)
    while len(child) > 0:
        for vehicle in vehicle_child:
            if len(child) == 0:
                break
            if len(child) - 1 > 0:
                number_of_routes = random.randint(0, len(child)-1)
            else:
                number_of_routes = 0
            child_copy = copy.deepcopy(child)
            for index in range(number_of_routes+1):
                route = [route for route in all_routes if route.city == child_copy[index]][0]
                if route.requirement <= vehicle.capacity:
                    vehicle.routes.append(route)
                    vehicle.capacity -= route.requirement
                    child.remove(route.city)
                elif vehicle_child[-1] == vehicle:
                    appropriate_vehicles = [veh for veh in vehicle_child if veh.capacity >= route.requirement]
                    if len(appropriate_vehicles) == 1:
                        appropriate_vehicles[0].routes.append(route)
                        appropriate_vehicles[0].capacity -= route.requirement
                        child.remove(route.city)
                    elif len(appropriate_vehicles) > 1:
                        appropriate_vehicle = random.choice(appropriate_vehicles)
                        appropriate_vehicle.routes.append(route)
                        appropriate_vehicle.capacity -= route.requirement
                        child.remove(route.city)
                    else:
                        # adjust the distribution of routes by vehicles in order to met the condition
                        # find all potential vehicles
                        potential_vehicles_number = [veh.vehicle_number for veh in vehicles.all_vehicles
                                                     if veh.capacity >= route.requirement]
                        potential_vehicles_current_capacity = [veh for veh in vehicle_child
                                                               if veh.vehicle_number in potential_vehicles_number]
                        potential_vehicles_current_capacity.sort(key=lambda x: x.capacity, reverse=True)
                        for potential_vehicle in potential_vehicles_current_capacity:
                            needed_free_space = route.requirement - potential_vehicle.capacity
                            while needed_free_space > 0:
                                routes = copy.deepcopy(potential_vehicle.routes)
                                for veh_route in routes:
                                    if veh_route.city not in [r.city for r in routes]:
                                        continue
                                    other_vehicles = [veh for veh in vehicle_child
                                                      if veh.capacity >= veh_route.requirement]
                                    if len(other_vehicles) > 0:
                                        other_vehicle = random.choice(other_vehicles)
                                        other_vehicle.routes.append([r for r in potential_vehicle.routes
                                                                         if r.city == veh_route.city][0])
                                        other_vehicle.capacity -= veh_route.requirement
                                        needed_free_space -= veh_route.requirement
                                        potential_vehicle.capacity += veh_route.requirement
                                        potential_vehicle.routes.remove([r for r in potential_vehicle.routes
                                                                         if r.city == veh_route.city][0])
                                    if needed_free_space <= 0:
                                        potential_vehicle.routes.append(route)
                                        potential_vehicle.capacity -= route.requirement
                                        child.remove(route.city)
                                        break
                                    if veh_route == routes[-1]:
                                        break
                                break

                            if potential_vehicle == potential_vehicles_current_capacity[-1] and needed_free_space != 0:
                                print('problem')

                            break
    return vehicle_child


def restart_capacity(child):
    for vehicle in child:
        vehicle.capacity = [veh.capacity for veh in vehicles.all_vehicles
                            if veh.vehicle_number == vehicle.vehicle_number][0]
        if len(vehicle.routes) > 0:
            vehicle.routes.insert(0, [depot for depot in all_routes if depot.city == 'DEPOT'][0])
            vehicle.routes.insert(len(vehicle.routes),
                                    [depot for depot in all_routes if depot.city == 'DEPOT'][0])


def order_crossover(population_for_crossover):
    new_population = []
    number_of_iterations = copy.deepcopy(len(population_for_crossover)) // 2
    population_for_crossover_copy = copy.deepcopy(population_for_crossover)
    for i in range(number_of_iterations):
        male = random.choice(population_for_crossover_copy)
        female = copy.deepcopy(random.choice(population_for_crossover_copy))
        male = copy.deepcopy(male)
        child1, cross_point1, cross_point2 = order_crossover_implementation(male, female, None, None)
        child2, cross_point1, cross_point2 = order_crossover_implementation(female, male, cross_point1, cross_point2)
        new_population.append(child1)
        new_population.append(child2)
    return new_population


def partially_mapped_crossover(population_for_crossover):
    new_population = []
    number_of_iterations = copy.deepcopy(len(population_for_crossover)) // 2
    population_for_crossover_copy = copy.deepcopy(population_for_crossover)
    for i in range(number_of_iterations):
        male = random.choice(population_for_crossover_copy)
        population_for_crossover_copy.remove(male)
        female = random.choice(population_for_crossover_copy)
        population_for_crossover_copy.append(male)
        cross_point1, cross_point2, child1, child2 = partially_mapped_crossover_implementation(male, female, None, None)
        new_population.extend([child1, child2])
    return new_population


def mutation(population, mutation_probability):
    population_after_mutation = []
    for chromosome in population:
        if random.random() < mutation_probability:
            # find one random route and then find routes that are capable for the swap mutation (where condition is met)
            random_vehicle = random.choice([veh for veh in chromosome if len(veh.routes) > 0])
            random_route = random.choice([route for route in random_vehicle.routes if route.city != 'DEPOT'])
            capable_routes_for_swap = []
            random_vehicle_capacity = random_vehicle.capacity - \
                                      sum([route.requirement for route in random_vehicle.routes]) \
                                      + random_route.requirement
            for vehicle in chromosome:
                vehicle_capacity = vehicle.capacity - sum([route.requirement for route in vehicle.routes])
                capable_routes_for_swap.extend([route for route in vehicle.routes
                                                if random_vehicle_capacity >= route.requirement
                                                and vehicle_capacity >= random_route.requirement
                                                and route.city != 'DEPOT'])

            if len(capable_routes_for_swap) > 0:
                random_route2 = random.choice(capable_routes_for_swap)
                if random_route2 in random_vehicle.routes:
                    index1 = random_vehicle.routes.index(random_route)
                    index2 = random_vehicle.routes.index(random_route2)
                    random_vehicle.routes[index1], random_vehicle.routes[index2] = \
                        random_vehicle.routes[index2], random_vehicle.routes[index1]
                else:
                    index1 = random_vehicle.routes.index(random_route)
                    random_vehicle.routes.pop(index1)
                    random_vehicle.routes.insert(index1, random_route2)
                    random_vehicle2 = [veh for veh in chromosome if random_route2 in veh.routes][0]
                    index2 = random_vehicle2.routes.index(random_route2)
                    random_vehicle2.routes.pop(index2)
                    random_vehicle2.routes.insert(index2, random_route)
        population_after_mutation.append(chromosome)
    return population_after_mutation


# initial chromosome is list of vehicles with assigned routes
# this function coverts initial representation of the chromosome into the list of lists where the index of the list
# is the number of vehicle and elements in the list are assigned routes for that vehicle
def convert_into_chromosome(chromosome, with_vehicles):
    converted = []
    if not with_vehicles:
        for vehicle in chromosome:
            for route in vehicle.routes:
                if route.city == 'DEPOT':
                    continue
                converted.append(route.city)
    else:
        for vehicle in chromosome:
            for route in vehicle.routes:
                if route.city == 'DEPOT':
                    continue
                converted.append(route.city)
            converted.append(vehicle.vehicle_number)
    return converted


def genetic_alg(population, selection_method):
    chosen_parents, elitists = selection(population, len(population), 2)
    if selection_method == 'pmx':
        new_population = partially_mapped_crossover(chosen_parents)
    else:
        new_population = order_crossover(chosen_parents)
    new_population_after_mutation = mutation(new_population, 0.2)
    new_population_after_mutation.extend(elitists)
    return new_population_after_mutation


def evolution(number_of_generations, same_results_threshold, selection_method, population):
    best_solution_per_generation = []
    stopping_criteria_is_met = False
    num_generation = 0
    while not stopping_criteria_is_met:
        if num_generation == number_of_generations:
            stopping_criteria_is_met = True

        generation = genetic_alg(population, selection_method)

        if len(generation) == 0:
            break

        fit = fitness(generation)
        fit_best_sol = fit[0]

        population = generation
        best_solution_per_generation.append((num_generation, fit_best_sol))

        if len(best_solution_per_generation) > same_results_threshold:
            j = num_generation
            for i in range(j - same_results_threshold + 1, j):
                if best_solution_per_generation[i][1] != fit_best_sol:
                    break
                elif i == j - 1:
                    stopping_criteria_is_met = True

        num_generation += 1
    return best_solution_per_generation
