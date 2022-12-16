# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def get_attr_dict_func(row,col,item,attr_dict):
    version=getattr(row, '版本')
    attr_value_0=getattr(row, col)
    if type(attr_value_0)==str:
        attr_value=attr_value_0.strip()
    else:
        attr_value=attr_value_0
    if version not in attr_dict:
        attr_dict[version]={col:{attr_value:[item]}}
    else:
        attr_dict_0=attr_dict[version]
        if col not in attr_dict_0:
            attr_dict_0[col]={attr_value:[item]}
        else:
            attr_dict_1=attr_dict_0[col]
            if attr_value not in attr_dict_1:
                attr_dict_1[attr_value]=[item]
            else:
                attr_dict_1[attr_value].append(item)
def get_attr_dict(item_df):
    #value:[item]
    attr_dict={}
    attr_cols=set(item_df.columns)-set(['SKU编码','版本'])
    item_set=set()
    for row in item_df.itertuples():
        item=getattr(row, 'SKU编码')
        item_set.add(item)
        for col in attr_cols:
            get_attr_dict_func(row,col,item,attr_dict)
    return attr_dict,attr_cols,item_set
def get_version_qty_dict(version_qty_df):
    version_qty_dict={}#version/year:qty
    version_qty_df_0=version_qty_df.copy()
    version_qty_df_0.set_index(['版本'],inplace=True)
    years=list(set(version_qty_df_0.columns)-set(['版本']))
    for year in years:
        for version,qty in version_qty_df_0[year].items():
            if qty>0:
                if version not in version_qty_dict:
                    version_qty_dict[version]={year:qty}
                else:
                    version_qty_dict_0=version_qty_dict[version]
                    version_qty_dict_0[year]=qty
    return version_qty_dict
def get_attr_ratio_dict(file_name,attr_cols):
    attr_ratio_dict={}#version/attr_col/attr_value:qty
    attr_cols_1=attr_cols-set(['版本'])
    for col in attr_cols_1:
        df=pd.read_excel("%s.xlsx"%(file_name),sheet_name='选配项比例-%s'%(col))
        for row in df.itertuples():
            attr_value_0=getattr(row, col)
            if type(attr_value_0)==str:
                attr_value=attr_value_0.strip()
            else:
                attr_value=attr_value_0
            versions=list(set(df.columns)-set([col]))
            if attr_value!='合计':
                for version in versions:
                    qty=getattr(row, version)
                    if qty>0:
                        if version not in attr_ratio_dict:
                            attr_ratio_dict[version]={col:{attr_value:qty}}
                        else:
                            attr_ratio_dict_0=attr_ratio_dict[version]
                            if col not in attr_ratio_dict_0:
                                attr_ratio_dict_0[col]={attr_value:qty}
                            else:
                                attr_ratio_dict_1=attr_ratio_dict_0[col]
                                attr_ratio_dict_1[attr_value]=qty
    return attr_ratio_dict
def get_item_ratio_dict(item_ratio_df):
    item_ratio_dict={}
    for row in item_ratio_df.itertuples():
        item=getattr(row, 'SKU编码')
        ratio=getattr(row, '比例')
        item_ratio_dict[item]=ratio
    return item_ratio_dict
def get_last_qty_dict(last_qty_df):
    last_qty_df_0=last_qty_df.copy()
    last_qty_df_0.set_index(['SKU编码'],inplace=True)
    last_qty_dict={}#year/item:qty
    years=list(set(last_qty_df.columns)-set(['SKU编码']))
    for year in years:
        for item,qty in last_qty_df_0[year].items():
            if year not in last_qty_dict:
                last_qty_dict[year]={item:qty}
            else:
                last_qty_dict_0=last_qty_dict[year]
                last_qty_dict_0[item]=qty
    return last_qty_dict
import gurobipy as grb
from collections import defaultdict
def create_model(item_set,version_qty_dict,attr_dict,attr_ratio_dict,item_ratio_dict,last_qty_dict,item_df):
    result_all_df=item_df.copy()
    for version,version_qty_dict_0 in version_qty_dict.items():
        attr_dict_0=attr_dict[version]
        attr_ratio_dict_0=attr_ratio_dict[version]
        sorted_year=sorted(list(version_qty_dict_0.keys()))
        for year in sorted_year:
            print(year)
            qty_sum=version_qty_dict_0[year]
            last_qty_dict_0=last_qty_dict[year]
            #每个item占有的数量作为decision_var
            mdl = grb.Model("sop_split_%s"%(year))
            items_var=mdl.addVars(item_set,vtype=grb.GRB.CONTINUOUS, lb=0, name='items')
            #总和等于qty_sum的约束
            mdl.addConstr(grb.quicksum(items_var[i] for i in item_set)==qty_sum,name='qty_sum')
            cc_lin_expr = defaultdict(grb.LinExpr)
            unit_list=[]
            for attr_col,attr_ratio_dict_1 in attr_ratio_dict_0.items():
                for attr_value,ratio in attr_ratio_dict_1.items():
                    item_list_selected=attr_dict_0[attr_col][attr_value]
                    #第一个目标，各个属性的比例差距最小,l1-norm minimization的表达式
                    unit=(attr_col,attr_value)
                    cc_lin_expr[unit]=grb.quicksum(items_var[i] for i in item_list_selected)-qty_sum*ratio
                    unit_list.append(unit)
            #辅助变量y,>=-y,<=y
            y_var=mdl.addVars(unit_list,vtype=grb.GRB.CONTINUOUS, name='y')
            for unit in unit_list:
                mdl.addConstr(cc_lin_expr[unit]<=y_var[unit],name='ub_%s_%s'%(unit))
                mdl.addConstr(cc_lin_expr[unit]>=-y_var[unit],name='lb_%s_%s'%(unit))
            #求解三个目标的多目标优化问题，可以按照前一个目标达成的最优结果作为约束，进入下一个目标
            #设置第一个目标
            mdl.setObjectiveN(grb.quicksum(y_var[unit] for unit in unit_list),index=1,priority=3)
            #第二个目标净大比例
            y_item_var=mdl.addVars(item_set,vtype=grb.GRB.CONTINUOUS, name='y_item')
            for item in item_set:
                qty_sum_item=item_ratio_dict[item]*qty_sum
                mdl.addConstr(items_var[item]-qty_sum_item<=y_item_var[item],name='ub_%s'%(item))
                mdl.addConstr(items_var[item]-qty_sum_item>=-y_item_var[item],name='lb_%s'%(item))
            mdl.setObjectiveN(grb.quicksum(y_item_var[item] for item in item_set),index=2,priority=2)
            #第三个目标，上版SKU数量
            y_last_item_var=mdl.addVars(item_set,vtype=grb.GRB.CONTINUOUS, name='y_last_item')
            for item in item_set:
                qty=last_qty_dict_0[item]
                mdl.addConstr(items_var[item]-qty<=y_last_item_var[item],name='ub_last_%s'%(item))
                mdl.addConstr(items_var[item]-qty>=-y_last_item_var[item],name='lb_last_%s'%(item))
            mdl.setObjectiveN(grb.quicksum(y_item_var[item] for item in item_set),index=3,priority=1)
            #求解
            mdl.ModelSense = grb.GRB.MINIMIZE
            mdl.optimize()
            #获得结果
            result_tuple_list=[]
            for item in item_set:
                alloc_qty = items_var[item].x
                result_tuple_list.append((item,alloc_qty))
            result_df=pd.DataFrame(result_tuple_list,columns=['SKU编码',year])
            result_all_df=result_all_df.merge(result_df,how='left',on=['SKU编码'])
    return result_all_df
def read_df(file_name):
    #读取数据
    item_df=pd.read_excel("%s.xlsx"%(file_name),sheet_name='基表',dtype={'SKU编码':str})
    attr_dict,attr_cols,item_set=get_attr_dict(item_df)
    version_qty_df=pd.read_excel("%s.xlsx"%(file_name),sheet_name='本期版本数量')
    version_qty_dict=get_version_qty_dict(version_qty_df)
    attr_ratio_dict=get_attr_ratio_dict(file_name,attr_cols)
    item_ratio_df=pd.read_excel("%s.xlsx"%(file_name),sheet_name='SKU净大订比例',dtype={'SKU编码':str})
    item_ratio_dict=get_item_ratio_dict(item_ratio_df)
    last_qty_df=pd.read_excel("%s.xlsx"%(file_name),sheet_name='上版SKU数量',dtype={'SKU编码':str})
    last_qty_dict=get_last_qty_dict(last_qty_df)
    #创建模型并求解
    result_all_df=create_model(item_set,version_qty_dict,attr_dict,attr_ratio_dict,item_ratio_dict,last_qty_dict,item_df)
    result_all_df.to_excel("result_all_df.xlsx",index=False)
if __name__ == "__main__": #this is necessary for parallel processing with pool
     file_name='数据模板02'
     read_df(file_name)
