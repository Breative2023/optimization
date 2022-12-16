import gurobipy as gp
from gurobipy import GRB
# 参考知乎专栏的例子 https://zhuanlan.zhihu.com/p/52371462

# multidict的用法
names, lower, upper = gp.multidict({
	'x': [0, 1],
	'y': [1, 2],
	'z': [0, 3]})
print(names) # names对象是tuplelist
print(lower) # lower对象是tupledict
print(upper) # upper对象是tupledict

# tuplelist的用法
list = [(1, 2), (1, 3), (2, 3), (2, 4)]
A = gp.tuplelist(list)
print(A.select(1, '*'))# 选出所有第一个元素为 "1" 的组
# print([(x,y) for x,y in A if x == 1]) # 跟上面结果等价的
print(A.select('*', [2, 4]))  # 选出所有第二个元素为"2"或者"4"的组
print(A.select('*', '*')) # 所有的组

# tupledict的用法
model = gp.Model('gurobi_demo_4') # 起名字
d = model.addVars(list, name="d") # 模型的变量一般都是tupledict类型，有sum,select,prod函数
model.update()
print(d.select(1, '*'))
print(sum(d.select(1, '*')))
print((d.sum(1, '*'))) # 等价于上面sum(d.select(1, '*'))

# 添加约束条件 Model.addConstr() 和 Model.addConstrs()
model2 = gp.Model('gurobi_demo_4') # 起名字
x = model2.addVars(20, 8, vtype=gp.GRB.BINARY) # 160个变量
# 写法 1
for i in range(20):
    model2.addConstr(x.sum(i, "*") <= 1)
# 写法 2
model2.addConstrs(x.sum(i, "*") <= 1 for i in range(20))

# prod()的用法 用于变量和系数相乘后累加
# 创建模型
c = [8, 10, 7, 6, 11, 9]
p = [[12, 9, 25, 20, 17, 13],
	[35, 42, 18, 31, 56, 49],
	[37, 53, 28, 24, 29, 20]]
r = [60, 150, 125]
model3 = gp.Model("Example")
# 创建变量
x = model3.addVars(6, lb=0, ub=1, name='x')
# 更新变量环境
model3.update()
# 创建目标函数
model3.setObjective(x.prod(c), gp.GRB.MINIMIZE)
# 创建约束条件
model3.addConstrs(x.prod(p[i]) >= r[i] for i in range(3))
# 执行线性规划模型
model3.optimize()
print("Obj:", model3.objVal)
for v in model3.getVars():
	print(f"{v.varName}：{round(v.x,3)}")