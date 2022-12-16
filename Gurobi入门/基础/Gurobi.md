### 1. Gurobi使用的一般流程
```
import gurobipy
# 创建模型
MODEL = gurobipy.Model()
# 创建变量
X = MODEL.addVar(vtype=gurobipy.GRB.INTEGER,name="X")
# 更新变量环境
MODEL.update()
# 创建目标函数
MODEL.setObjective('目标函数表达式', gurobipy.GRB.MINIMIZE)
# 创建约束条件
MODEL.addConstr('约束表达式，逻辑运算')
# 执行线性规划模型
MODEL.optimize()
# 输出模型结果
print("Obj:", MODEL.objVal)
for x in X:
    print(f"{x.varName}：{round(x.X,3)}")
```

### 2. 基本函数介绍
https://zhuanlan.zhihu.com/p/52371462
```
LinExpr.add(expr,mult=1.0)添加一个线性表达式到另外一个。
参数：
expr:添加一个线性表达式
mult(可选参数):表达式要乘以的系数
例子
e1=x+y
e1.add(z,3.0)

LinExpr.addTerms(coeffs,vars)在线性表达式中添加新的一项。
参数
coeffs:新的一项的系数，可以是是一个列表也可以是单独的一个。列表中元素的个数要和第二个参数相等。
vars:新的一项的变量，同样可以是一个列表也可以是单独的一个。
例子
expr=LinExpr()
expr.addTerms(1.0,x)
expr.addTerms([2.0,3,0],[y,z])

```


### 3. 输出日志解读
https://blog.csdn.net/weixin_47001012/article/details/125845966







