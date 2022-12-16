# This example formulates and solves the following simple MIP model
# using the matrix API:
#  maximize
#        x +   y + 2 z
#  subject to
#        x + 2 y + 3 z <= 4
#        x +   y       >= 1
#        x, y, z binary

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
# 来自gurobi官网的例子 https://www.gurobi.com/documentation/10.0/quickstart_windows/cs_example_matrix1_py.html

try:

    # Create a new model
    m = gp.Model("matrix1")

    # Create variables
    x = m.addMVar(shape=3, vtype=GRB.BINARY, name="x")

    # Set objective
    obj = np.array([1.0, 1.0, 2.0])
    m.setObjective(obj @ x, GRB.MAXIMIZE)
    #m.setObjective(np.matmul(obj, x), GRB.MAXIMIZE)

    # Build (sparse) constraint matrix
    val = np.array([1.0, 2.0, 3.0, -1.0, -1.0])
    row = np.array([0, 0, 0, 1, 1])
    col = np.array([0, 1, 2, 0, 1])

    A = sp.csr_matrix((val, (row, col)), shape=(2, 3)) # 压缩稀疏行矩阵 初始化参数的格式 csr_matrix((data, (row_ind, col_ind)), [shape=(M, N)])

    # Build rhs vector
    rhs = np.array([4.0, -1.0])

    # Add constraints
    m.addConstr(A @ x <= rhs, name="c")

    # Optimize model
    m.optimize()

    print(x.X)
    print('Obj: %g' % m.ObjVal)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')