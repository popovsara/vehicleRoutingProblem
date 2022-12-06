import matplotlib.pyplot as plt


def plot_fitness_values(best_solutions, title):
    fitness_values = [solution[1][1] for solution in best_solutions]
    num_generations = [solution[0] for solution in best_solutions]
    plt.plot(num_generations, fitness_values)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(title)
    plt.savefig('../plots/' + title + '.png')
    plt.clf()


def plot_routes(vehicles, title):
    i = 0
    for vehicle in vehicles:
        if len(vehicle.routes) > 0:
            longitude = [route.location[0] for route in vehicle.routes]
            latitude = [route.location[1] for route in vehicle.routes]
            plt.scatter(x=longitude, y=latitude)
            plt.plot(longitude, latitude, label='vehicle: ' + str(vehicle.vehicle_number))
            i += 1
    plt.title(title)
    plt.legend()
    plt.savefig('../plots/' + title + '.png')
    plt.clf()


# def load_data():
  #  return pickle.load(open("initialPopulation15.p", "rb"))


# def save_data(data):
  #  pickle.dump(data, open("initialPopulation15.p", "wb"))


# number_of_generations = 500
# same_results_threshold = 60
# -1 because DEPOT point is also considered as one location
# size_of_init_population = (len(locations.all_routes) - 1) * 10
# size_of_init_population = 15 * 10
# initial_population = vrp.create_init_population(size_of_init_population, locations.all_routes, vehicles.all_vehicles)
# save_data(initial_population)
# initial_population = load_data()

