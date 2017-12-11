from itertools import product
import pickle

from nav.utility.classes import Location, Obstacle
from nav import solve

from benchmarks.point_to_point import problem
from benchmarks.point_to_point import environments
from benchmarks.point_to_point import benchmark

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

ENVIRONMENT_ID = 12345
ENVIRONMENT_COUNT = 25

params_values = {"granularity": [5.0, 10.0],
                "quantization_distance": [0.5, 1.0],
                "optim_max_iter": [1000],
                "optim_init_step_size": [1e-4, 1e-3, 1e-2],
                "optim_min_step": [1e-3, 1e-2, 1e-1],
                "optim_reset_step_size": [1e-8, 1e-7, 1e-6],
                "optim_cooling_schedule": [1.01, 1.001, 1.0001, 1.00001],
                "optim_fast_cooling_schedule": [1.1, 1.3, 1.6, 2.0],
                "optim_init_constraint_hardness": [1, 2, 3, 4],
                "optim_init_spring_hardness": [.1, .2, .4, .8, .16, .32, .64, 1.28],
                "optim_max_time_increase": [5, 10, 20, 50], # what does this do?
                "optim_init_momentum":  [.5, .8, .95, .99, .995],
                "optim_momentum_change": [.05, .1, .2, .3],
                "optim_scale": [1.0]}

results_grid = []
score_grid = []
params_grid = [dict(zip(params_values, v)) for v in product(*params_values.values())]

# Set problem variables
((x_min, y_min), (x_max, y_max)) = problem.area
boundary = [Location(x_min, y_min), Location(x_min, y_max),
            Location(x_max, y_min), Location(x_max, y_max)]

((wx_min, wy_min), (wx_max, wy_max)) = problem.waypoints
waypoints = [Location(wx_min, wy_min), Location(wx_max, wy_max)]

for params in params_grid:
    print("trying:")
    print(params)
    envs = environments.generate(ENVIRONMENT_COUNT, ENVIRONMENT_ID)
    flight_paths = []
    for i, env in enumerate(envs):
        stat_obstacles = []
        for obs in env:
            cx, cy, r = obs
            stat_obstacles.append(Obstacle(Location(cx, cy), r))
    
        try:
            flight_path = solve.point_to_point(boundary, waypoints,
                                               stat_obstacles, params)
        except Exception as e:
            print(e)
            flight_path = np.array([[wx_min, wx_max], [wy_min, wy_max]])
    
        flight_paths.append(flight_path)

    result = benchmark.run(envs, flight_paths)
    results_grid.append(result)
    score_grid.append(result["score"])

best_params = params_grid[score_grid.index(min(score_grid))]
pickle.dump(best_params, open("graph_params.pkl", "wb"))