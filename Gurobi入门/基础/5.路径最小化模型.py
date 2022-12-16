import numpy as np
import matplotlib.pyplot as plt
from gurobipy import *
# 来自CSDN博客的例子 https://blog.csdn.net/weixin_47001012/article/details/125845966

rnd = np.random
rnd.seed(1) # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

n = 10 # 一共几个客户点/城市/需求点
xc = rnd.rand(n+1)*200 # 随机生成每个城市的横坐标，范围[0,200]
yc = rnd.rand(n+1)*100 # 随机生成每个城市的纵坐标，范围[0,100]

# 可以画图看一眼生成的城市什么样子
plt.plot(xc[0], yc[0], c='r',marker='s' ) # 索引为0的点，即depot/仓库/出发点
plt.scatter(xc, yc, c='b') # 客户点
plt.show()

N = list(range(1,n+1)) # 客户点集合 N [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
V = list(range(0,n+1)) # 所有点集合（仓库+客户点）V [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
A = [(i,j) for i in V for j in V if i !=j] # 城市之间有哪些连线/路段/弧段 110个值
D = {(i,j): np.hypot(xc[i]-xc[j], yc[i]-yc[j]) for i,j in A} # np.hypot：二范数=求平方和；计算弧段的长度  距离矩阵
Q = 20 # 车最大载重
# 生成的q是字典 {1: 7, 2: 2, 3: 1, 4: 2, 5: 9, 6: 9, 7: 4, 8: 9, 9: 8, 10: 4}
q = {i:rnd.randint(1,10) for i in N} # 随机生成客户点的需求量，范围[1,10] N是客户点集合[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

mdl = Model('CVRP') # 起名字

x = mdl.addVars(A, vtype=GRB.BINARY) # 增加变量xij，表示是否链接ij,注意这里生成的变量名实际上是C0-C109
u = mdl.addVars(N, vtype=GRB.CONTINUOUS) # 增加变量ui，表示车在该点处累计载货量,注意这里生成的变量名实际上是C110-C119

# 更新变量环境
mdl.update()

# 打印所有的变量名
for var in mdl.getVars():
   print(var.varName)

mdl.modelSense = GRB.MINIMIZE # 目标为最小化
mdl.setObjective(quicksum(x[i,j]*D[i,j] for i,j in A )) # 目标函数为总距离

# 添加所有约束
mdl.addConstrs(quicksum(x[i,j] for j in V if i != j)==1 for i in N)# 约束1：每个点都被离开一次；
mdl.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in N)# 约束2：每个点都被到达一次。
mdl.addConstrs((x[i,j]==1) >>   # 这个是一个Gurobi高阶操作，指示约束
               (u[i] + q[j] == u[j]) for i,j in A if i!=0 and j!=0)# 约束3:如果两点可达，则前一个点的累计载货量加上目的地的需求量等于目的地的累计载货量
mdl.addConstrs(u[i] >= q[i] for i in N)# 约束4：每个点累计载货量大于需求量。
mdl.addConstrs(u[i] <= Q for i in N)# 约束5：每个点累计载货量小于车最大载重。

mdl.optimize() # 优化

# 优化完成，下面输出结果
active_arts = [a for a in A if x[a].x > 0.9] # 输出最优解的所有连线，即xij中是1的(i,j)
# 由于存在误差，xij可能为0.999999999，因此不要用==1
print(active_arts)

# 画图
for index, (i,j) in enumerate(active_arts):
    plt.plot([xc[i],xc[j]],[yc[i],yc[j]],c='r')
plt.plot(xc[0], yc[0], c='g',marker='s' )
plt.scatter(xc, yc, c='b')
plt.show()