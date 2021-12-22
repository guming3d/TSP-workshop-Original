# dependance
import numpy as np
import pandas as pd
import networkx as nx
from braket.ocean_plugin import BraketDWaveSampler
from dwave.system.composites import EmbeddingComposite
from os.path import abspath, dirname, join, pardir

seed = 1024

import sys
sys.dont_write_bytecode = True
path_app = dirname(abspath(__file__))
path_parent = abspath(join(path_app, pardir))
if path_app not in sys.path:
    sys.path.append(path_app)

from scripts.plots import plot_cities
from utils_tsp import get_distance, traveling_salesperson


class qcANN():

    def __init__(self, s3_folder, tsp):
        self.cities = tsp.cities
        self.distances = tsp.distances
        print(self.cities)
        print(self.distances)
        # for cityA in self.cities:
        #     for cityB in self.cities:
        #         print(f"{cityA} v.s {cityB} distance: {self.distances[cityA][cityB]}")

        self.answer = None
        print(f"Try to solve tsp of {len(self.cities)}")
        self.sampler = EmbeddingComposite(BraketDWaveSampler(
            s3_folder, 'arn:aws:braket:::device/qpu/d-wave/Advantage_system4'))

        self.city_map = {}
        self.num_shots = 1000
        self.total_dist = None
        self.distance_with_return = None
        self.optimize_routes = []

        self.solve_tsp()

    def solve_tsp(self):
        # TODO: generate data from raw data -> distance matrix -> graph model based on nx
        distance_matrix = self.get_distance_matrix_v2()
        # data = pd.DataFrame(distance_matrix)
        # data = distance_matrix
        data = None

        # distance matrix -> graph model based on nx
        # G = nx.from_pandas_adjacency(data)
        # G = data
        G = None

        # TODO: prepare paramters
        lagrange = None
        weight = 'weight'

        start_city = 0
        # Hints: find how the lagrange is generated in your notebook

        # run the traveling sales man api to get the answer
        route_list = traveling_salesperson(G, self.sampler, lagrange=lagrange,
                                      start=start_city, num_reads=self.num_shots, answer_mode="histogram")

        # TODO: find the optimized one and prepare to saving as the local file
        # Hint: route_list -> self.optimize_routes
        # min_distance = 999999999
        # min_route = []
        # for route in route_list:
        #     self.total_dist, self.distance_with_return = get_distance(route, data)#
        
        # random generate results for testing
        # print distance
        min_distance = 999999999
        min_route = []
        city_num = len(self.cities)
        route_num = 0
        for num in range(route_num):
            route_answer = {}
            route_answer['route'] = range(1, city_num+1)
            route_answer['total_distance'] = 12345
            route_answer['total_distance_with_return'] = 12345
            if route_answer['total_distance_with_return'] < min_distance:
                min_distance = route_answer['total_distance_with_return']
                min_route = route_answer['route']
                
            self.optimize_routes.append(route_answer)

        print(f"min route {min_route} with distance {min_distance}")

    # helper function
    def create_cities(self, N):
        """
        Creates an array of random points of size N.
        """
        cities = []
        np.random.seed(seed)
        for i in range(N):
            cities.append(np.round((np.random.rand(2) * 100), 2))
        return np.array(cities)

    def get_distance_matrix_v2(self):
        number_of_cities = len(self.cities)
        matrix = np.zeros((number_of_cities, number_of_cities))
        # build city map
        for city in self.cities:
            if city not in self.city_map:
                self.city_map[len(self.city_map)] = city

        for i in range(number_of_cities):
            for j in range(i, number_of_cities):
                matrix[i][j] = self.distances[self.city_map[i]][self.city_map[j]]
                matrix[j][i] = matrix[i][j]
        return matrix

    def tsp_solver(self):
        # generate data: cities/distance -> distance matrix -> generate graph data based on distance matrix

        # raw data(cities/distance) -> distance matrix
        distance_matrix = self.get_distance_matrix_v2()
        data = pd.DataFrame(distance_matrix)

        # distance matrix -> graph model based on nx
        G = nx.from_pandas_adjacency(data)

        # prepare parameters
        lagrange = None
        weight = 'weight'

        start_city = 0

        if lagrange is None:
            # If no lagrange parameter provided, set to 'average' tour length.
            # Usually a good estimate for a lagrange parameter is between 75-150%
            # of the objective function value, so we come up with an estimate for
            # tour length and use that.
            if G.number_of_edges() > 0:
                lagrange = G.size(weight=weight) * G.number_of_nodes() / G.number_of_edges()
            else:
                lagrange = 2

        # run traveling sales man api to get the optimized result
        route_list = traveling_salesperson(G, self.sampler, lagrange=lagrange,
                                      start=start_city, num_reads=self.num_shots, answer_mode="histogram")

        # find the optimized one, prepare the data for saving as the local file
        min_distance = 999999999
        min_route = []
        for route in route_list:
            self.total_dist, self.distance_with_return = get_distance(route, data)
            route_answer = {}
            route_answer['route'] = route
            route_answer['total_distance'] = self.total_dist
            route_answer['total_distance_with_return'] = self.distance_with_return
            if self.distance_with_return < min_distance:
                min_distance = self.distance_with_return
                min_route = route
            
            self.optimize_routes.append(route_answer)

        print(f"min route {min_route} with distance {min_distance}")