from itertools import product
from math import sqrt

import gurobipy as gp
from gurobipy import GRB


def compute_distance(loc1, loc2):
    # This function determines the Euclidean distance between a facility and a county centroid.

    dx = loc1[0] - loc2[0]
    dy = loc1[1] - loc2[1]
    return sqrt(dx * dx + dy * dy)


def solve_covid19_facility(c_coordinates, demand):
    #####################################################
    #                    Data
    #####################################################

    # Indices for the counties
    counties = [*range(1, 10)]

    # Indices for the facilities
    facilities = [*range(1, 24)]

    # Create a dictionary to capture the coordinates of an existing facility and capacity of treating COVID-19 patients

    existing, e_coordinates, e_capacity = gp.multidict({
        1: [(1, 2), 281],
        2: [(2.5, 1), 187],
        3: [(5, 1), 200],
        4: [(6.5, 3.5), 223],
        5: [(1, 5), 281],
        6: [(3, 4), 281],
        7: [(5, 4), 222],
        8: [(6.5, 5.5), 200],
        9: [(1, 8.5), 250],
        10: [(1.5, 9.5), 125],
        11: [(8.5, 6), 187],
        12: [(5, 8), 300],
        13: [(3, 9), 300],
        14: [(6, 9), 243]
    })

    # Create a dictionary to capture the coordinates of a temporary facility and capacity of treating COVID-19 patients

    temporary, t_coordinates, t_capacity = gp.multidict({
        15: [(1.5, 1), 100],
        16: [(3.5, 1.5), 100],
        17: [(5.5, 2.5), 100],
        18: [(1.5, 3.5), 100],
        19: [(3.5, 2.5), 100],
        20: [(4.5, 4.5), 100],
        21: [(1.5, 6.5), 100],
        22: [(3.5, 6.5), 100],
        23: [(5.5, 6.5), 100]
    })

    # Cost of driving 10 miles
    dcost = 5

    # Cost of building a temporary facility with capacity of 100 COVID-19
    tfcost = 500000

    # Compute key parameters of MIP model formulation
    f_coordinates = {}
    for e in existing:
        f_coordinates[e] = e_coordinates[e]

    for t in temporary:
        f_coordinates[t] = t_coordinates[t]

    # Cartesian product of counties and facilities
    cf = []

    for c in counties:
        for f in facilities:
            tp = c, f
            cf.append(tp)

    # Compute distances between counties centroids and facility locations
    distance = {(c, f): compute_distance(c_coordinates[c], f_coordinates[f]) for c, f in cf}

    #####################################################
    #                    MIP Model Formulation
    #####################################################

    m = gp.Model('covid19_temporary_facility_location')

    # Build temporary facility
    y = m.addVars(temporary, vtype=GRB.BINARY, name='temporary') # 9个变量：9个临时设备点是否启用

    # Assign COVID-19 patients of county to facility
    x = m.addVars(cf, vtype=GRB.CONTINUOUS, name='Assign') # 9*23个变量：9个城市，23个设备点，一个城市到一个设备点治疗的人数

    # Add capacity to temporary facilities
    z = m.addVars(temporary, vtype=GRB.CONTINUOUS, name='addCap') #  9个变量：9个临时设备点的增量容量

    # Objective function: Minimize total distance to drive to a COVID-19 facility

    # Big penalty for adding capacity at a temporary facility
    bigM = 1e9

    m.setObjective(gp.quicksum(dcost * distance[c, f] * x[c, f] for c, f in cf)
                   + tfcost * y.sum() # tfcost建一个临时设备点的费用
                   + bigM * z.sum(), GRB.MINIMIZE)

    # Counties demand constraints
    demandConstrs = m.addConstrs((gp.quicksum(x[c, f] for f in facilities) == demand[c] for c in counties),
                                 name='demandConstrs')

    # Existing facilities capacity constraints
    existingCapConstrs = m.addConstrs((gp.quicksum(x[c, e] for c in counties) <= e_capacity[e] for e in existing),
                                      name='existingCapConstrs')

    # temporary facilities capacity constraints
    temporaryCapConstrs = m.addConstrs((gp.quicksum(x[c, t] for c in counties) - z[t]
                                        <= t_capacity[t] * y[t] for t in temporary),
                                       name='temporaryCapConstrs')
    # Run optimization engine
    m.optimize()

    #####################################################
    #                    Output Reports
    #####################################################

    # Total cost of building temporary facility locations
    temporary_facility_cost = 0

    print(f"\n\n_____________Optimal costs______________________")
    for t in temporary:
        if (y[t].x > 0.5):
            temporary_facility_cost += tfcost * round(y[t].x)

    patient_allocation_cost = 0
    for c, f in cf:
        if x[c, f].x > 1e-6:
            patient_allocation_cost += dcost * round(distance[c, f] * x[c, f].x)

    print(f"The total cost of building COVID-19 temporary healhtcare facilities is ${temporary_facility_cost:,}")
    print(f"The total cost of allocating COVID-19 patients to healtcare facilities is ${patient_allocation_cost:,}")

    # Build temporary facility at location

    print(f"\n_____________Plan for temporary facilities______________________")
    for t in temporary:
        if (y[t].x > 0.5):
            print(f"Build a temporary facility at location {t}")

    # Extra capacity at temporary facilities
    print(f"\n_____________Plan to increase Capacity at temporary Facilities______________________")
    for t in temporary:
        if (z[t].x > 1e-6):
            print(f"Increase  temporary facility capacity at location {t} by {round(z[t].x)} beds")

    # Demand satisfied at each facility
    f_demand = {}

    print(f"\n_____________Allocation of county patients to COVID-19 healthcare facility______________________")
    for f in facilities:
        temp = 0
        for c in counties:
            allocation = round(x[c, f].x)
            if allocation > 0:
                print(f"{allocation} COVID-19 patients from county {c} are treated at facility {f} ")
            temp += allocation
        f_demand[f] = temp
        print(f"{temp} is the total number of COVID-19 patients that are treated at facility {f}. ")
        print(f"\n________________________________________________________________________________")

    # Test total demand = total demand satisfied by facilities
    total_demand = 0

    for c in counties:
        total_demand += demand[c]

    demand_satisfied = 0
    for f in facilities:
        demand_satisfied += f_demand[f]

    print(f"\n_____________Test demand = supply______________________")
    print(f"Total demand is: {total_demand:,} patients")
    print(f"Total demand satisfied is: {demand_satisfied:,} beds")


# 场景一 Base Scenario
# Create a dictionary to capture the coordinates of a county and the demand of COVID-19 treatment
counties, coordinates, forecast = gp.multidict({
    1: [(1, 1.5), 351],
    2: [(3, 1), 230],
    3: [(5.5, 1.5), 529],
    4: [(1, 4.5), 339],
    5: [(3, 3.5), 360],
    6: [(5.5, 4.5), 527],
    7: [(1, 8), 469],
    8: [(3, 6), 234],
    9: [(4.5, 8), 500]
})
# find the optimal solution of the base scenario
print('--------------场景一-----------------')
solve_covid19_facility(coordinates, forecast)


# 场景二 Scenario 1
# Increase in demand by 20%.
for c in counties:
    forecast[c] = round(1.2 * forecast[c])
# find the optimal for scenario 1
print('--------------场景二-----------------')
solve_covid19_facility(coordinates, forecast)
