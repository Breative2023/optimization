import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7.0 & Gurobi 9.1.0

# Sample data: values of independent variable x and dependent variable y

observations, x, y = gp.multidict({
    ('1'): [0,1],
    ('2'): [0.5,0.9],
    ('3'): [1,0.7],
    ('4'): [1.5,1.5],
    ('5'): [1.9,2],
    ('6'): [2.5,2.4],
    ('7'): [3,3.2],
    ('8'): [3.5,2],
    ('9'): [4,2.7],
    ('10'): [4.5,3.5],
    ('11'): [5,1],
    ('12'): [5.5,4],
    ('13'): [6,3.6],
    ('14'): [6.6,2.7],
    ('15'): [7,5.7],
    ('16'): [7.6,4.6],
    ('17'): [8.5,6],
    ('18'): [9,6.8],
    ('19'): [10,7.3]
})

model = gp.Model('CurveFitting')

# 添加变量
# Constant term of the function f(x). This is a free continuous variable that can take positive and negative values.
a = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="a")

# Coefficient of the linear term of the function f(x). This is a free continuous variable that can take positive
# and negative values.
b = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="b")

# Non-negative continuous variables that capture the positive deviations
u = model.addVars(observations, vtype=GRB.CONTINUOUS, name="u")

# Non-negative continuous variables that capture the negative deviations
v = model.addVars(observations, vtype=GRB.CONTINUOUS, name="v")

# Non-negative continuous variables that capture the value of the maximum deviation
z = model.addVar(vtype=GRB.CONTINUOUS, name="z")

# 添加约束条件
# Deviation constraints
deviations = model.addConstrs( (b*x[i] + a + u[i] - v[i] == y[i] for i in observations), name='deviations')

# 添加目标函数
# Objective function of problem 1
model.setObjective(u.sum('*') + v.sum('*'))

# Run optimization engine
# 执行目标优化
model.optimize()

print("\n\n_________________________________________________________________________________")
print(f"The best straight line that minimizes the absolute value of the deviations is:")
print("_________________________________________________________________________________")
print(f"y = {b.x:.4f}x + ({a.x:.4f})")
print("\n\n")

# Maximum deviation constraints
# 场景二 添加约束条件
maxPositive_deviation = model.addConstrs( (z >= u[i] for i in observations), name='maxPositive_deviation')
maxNegative_deviation = model.addConstrs( (z >= v[i] for i in observations), name='maxNegative_deviation')

# Objective function for Problem 2
model.setObjective(z)

# Run optimization engine
model.optimize()

print("\n\n_________________________________________________________________________________")
print(f"The best straight line that minimizes the maximum deviation is:")
print("_________________________________________________________________________________")
print(f"y = {b.x:.4f}x + ({a.x:.4f})")
