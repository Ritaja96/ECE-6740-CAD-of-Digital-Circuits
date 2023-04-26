import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx
import numpy as np
import sympy
from array import *
import pandas as pd




ckt_file='mas8.txt'
#af_outputs=outputs
#rint("AF OUTPUTS",af_outputs)        


def get_inout(file,word):
   input_file=open(file,'r')
   lines = [line.rstrip(';\n').strip(' ') for line in input_file]
   found=0
   if(found==0):
    for l in lines:
      if word in l:
       port,var=l.split('=')
       var=var.strip()
       port=port.strip()
       s=var.split(' ')
       found=1 
       return s
   else:
        print("Not found")


inputs=get_inout(ckt_file,'INORDER')
outputs=get_inout(ckt_file,'OUTORDER')
af_outputs=outputs
print("AF OUTPUTS",af_outputs)  

print("inputs=", inputs)
print("outputs=", outputs) 


def get_eqn(line1):
 lines = [line1.rstrip(';\n').strip(' ')]
 st=lines[0]
 lhs,rhs=st.split('=')
 LHS=[]
 RHS=[]
 LHSRHS=[]
 LHS.append(lhs.strip())
 op_list=['(',')','!','*','^','+'] 
 rem_char=[op for op in op_list]
 res=rhs
 for i in range(0,len(rem_char)):
   res = res.replace(rem_char[i], " ")
   up_str=(res.split(' '))
   up_str = list(set(up_str)) 
   #print("list up",up_str)
   for st in up_str:
    if (st==''):
     up_str.remove(st)
     #print("list return",up_str)
 RHS=up_str
 LHSRHS=LHS+RHS
 #print("LHSRHS",LHSRHS)
 return LHSRHS   

input_file=open(ckt_file,'r')
lines = [line.rstrip(';\n').strip(' ') for line in input_file]
lines=lines[2:] 
Line_list=[]
for ln in lines:
 Ln=get_eqn(ln)
 Line_list.append(Ln) 

def find_ndlist(node):
 global inputs
 global Line_list
 lln=[]
 for ln in Line_list:
   if(ln[0]==node):
     #n=check_node(ln)
     for nd in ln:
      if((nd not in inputs) and (nd !='0') and (nd !='1')):
       lln.append(nd)#print(n)
    
     return lln[1:]
   
def find_afnets(node):
  parent_list=find_ndlist(node)
  lz=len(parent_list)
  itr=0
  while itr < lz:
    child_list=find_ndlist(parent_list[itr])
    itr=itr+1
    lchild=len(child_list)
    if(lchild!=0):
      parent_list=parent_list+child_list
      lz=len(parent_list)
    else:
      parent_list=parent_list  
  return parent_list    

def af_netlist(list1):
  global af_outputs
  af_netlist=[]
  for i in range(0,len(af_outputs)):
   af_net=find_afnets(af_outputs[i])
   if(len(af_net)!=0):
    af_netlist.append([af_outputs[i],af_net])
    #print(af_netlist)
   else:
    i=i+1  
  return af_netlist

buggy_nets=af_netlist(af_outputs)
#print("af",buggy_nets)  #['y_0_', ['t_14_0_', 't_13_0_', 'r_14_', 't_12_0_', 'r_13_', 'r_12_', 't_8_0_', 'r_0_', 'r_8_', 'T_12_', 'T_11_', 'T_10_']


def get_nets(list1):
 net_list=[]
 for elm in list1:
   for net in elm[1]:
    if net not in net_list:
     net_list.append(net)

 return net_list  

net_list=get_nets(buggy_nets)  
#print(net_list)  #internal nets

    

def get_afop(node):
  global buggy_nets
  edge_list=[]
  for elm in buggy_nets:
    for net in elm[1]:
      if(node==net):
       edge_list.append(elm[0])    
  return edge_list


#gives affected output list by each internal net
netwithop=[]
for net in net_list:
  op=get_afop(net)
  netwithop.append([net,op])

#print("Net with affected outputs",netwithop)  #['t_14_0_', ['y_0_']],

    
def get_grps(list1,op_grp):
  grp_net=[]
  for elm in list1:
    if(elm[1]==op_grp):
      grp_net.append(elm[0])
  return [op_grp,grp_net]

grps=[]
for item in netwithop:
  g=get_grps(netwithop,item[1])
  if g not in grps:
   grps.append(g)
  
print("GRP",grps)  #['y_0_', 'y_2_', 'y_3_', 'y_6_', 'y_7_'], ['r_12_']

op=[]
for gr in grps:
 if(gr[0] not in op):
   op.append(gr[0])
#print("GRP_OP",op)  #['y_0_'], ['y_0_', 'y_1_', 'y_4_']

  


row_size=len(af_outputs)
column_size=len(op)
#print(ar)

def create_rowmatrix(op,grpsofop):
 matrix = [] 
 for g in grpsofop:
   if op in g:
     matrix.append(1)
   else:
     matrix.append(0)  
 return matrix     

my_matrix=[]
for afop in af_outputs:
  o=create_rowmatrix(afop,op)
  my_matrix.append(o)
print("Matrix",my_matrix) 
#print(type(my_matrix)) 

my_df = pd.DataFrame(data = my_matrix, 
                  index = (i for i in range(0,row_size)), 
                  columns = (j for j in range(0,column_size)))

print("My dataframe",my_df)

#not needed
def create_dataframe(matrix):
  row_sz,column_sz=matrix.shape
  index_list=[]
  for r in range(0,row_sz):
    index_list.append(r)
  #print(index_list)  
  for r in range(0,row_sz):
   data = matrix
  df = pd.DataFrame(data, index =index_list )
  #print("DF",df) 
  return df



def isSubset(ar1,ar2):
  eq=0
  for i in range(0,len(ar1)):
    for j in range(0,len(ar2)):
      if(ar1[i]==ar2[j]):
        eq=eq+1
        #print(eq)

  if(eq==len(ar1)):
    return True #all elements of ar1 is in ar2 so ar1 is a subset of ar2
  else:
    return False
  
def check_onepos(axis,number,dataframe):
  onepos=[]
  row_size=dataframe.index
  #print(row_size)
  column_size=dataframe.columns
  #print(column_size)
  if((axis==0) and (number in column_size)):
    #print("Column")
    column_matrix=dataframe.loc[:,number]
    #print(column_matrix)

    for c in row_size:
      if(column_matrix[c]==1):
        onepos.append(c)
    #print(onepos)

  elif((axis==1)and (number in row_size)):
    #print("Row")
    row_matrix=dataframe.loc[number,:]
    #print(row_matrix)
    for r in column_size: 
      if(row_matrix[r]==1):
        onepos.append(r)
  return onepos 

#print(check_onepos(0,0,tdft))
#print(check_onepos(1,8,tdft))

def column_domcheck(column_no,dataframe):
  col_ar=check_onepos(0,column_no,dataframe)
  len1=len(col_ar)
  column_size=dataframe.columns
  
  if(len1!=0):
   for c in column_size:
    if(c!=column_no):
     col2=check_onepos(0,c,dataframe)
     len2=len(col2)
     cd=isSubset(col_ar,col2) 
     if(cd==True):
      return column_no
  return False 

def row_domcheck(row_no,dataframe):
  #print(dataframe)
  row_ar=check_onepos(1,row_no,dataframe)
  #print(col_ar)
  len1=len(row_ar)
  row_size=dataframe.index
  #row_size,column_size=dataframe.shape
  if(len1!=0):
   for r in row_size:
    if(r!=row_no):
     row2=check_onepos(1,r,dataframe)
     len2=len(row2)
     rd=isSubset(row_ar,row2) 
     if(rd==True):
      return r
  return False   

def check_essential(dataframe):
 es=[]
 row_size=dataframe.index
 #print(row_size)
 column_size=dataframe.columns
 #print(column_size)
 #row_size,column_size=matrix.shape
 row_sum=dataframe.sum(axis=1) #gives sum of every elements of each row
 #print(type(row_sum))
 #print(row_sum.loc[4])
 for row_no in row_size:
   if(row_sum[row_no]==1):
     es.append(row_no)
     ra=dataframe.loc[row_no,:]
     for column_no in column_size:
      #if(column_no in column_size): 
       if(ra[column_no]==1):
        es=[row_no,column_no]
        return list(es)
 return False

def checkfor_col(dataframe):
 sub=0
 coldm=[]
 row_size=dataframe.index
 column_size=dataframe.columns
 #row_size,column_size=dataframe.shape
 for c in column_size:
      subset_column=column_domcheck(c,dataframe)
      if((subset_column==False) and (type(subset_column)==bool)):
       sub=sub+1
      else:
        coldm.append(subset_column)
       
 if(sub==len(column_size)):
   return False   #no dominated column exists
 else:
   return coldm
 
def checkfor_row(dataframe):
 sub=0
 rowdm=[]
 row_size=dataframe.index
 column_size=dataframe.columns
 for r in row_size:
      subset_row=row_domcheck(r,dataframe)
      if((subset_row==False) and (type(subset_row)==bool)):
       sub=sub+1
      else:
        rowdm.append(subset_row)
      
 if(sub==len(row_size)):
   return False   #no dominated row exists
 else:
   return rowdm
 
def check_cyclic(dataframe):
  print("Starting matrix",dataframe)
  es=check_essential(dataframe)  
  if(es==False):
     check1=checkfor_col(dataframe)
     if(check1==False):
       check2=checkfor_row(dataframe)
       if(check2==False):
          print("matrix is cyclic")
          return True
       else:
         return False
       
def check_clmzero(dataframe):
 clm=dataframe.columns
 for col in clm:
  col_ones=check_onepos(0,col,dataframe)
  if(len(col_ones)==0):
    dataframe.drop(col, axis = 1, inplace = True)
    return dataframe
       
#essentials=[]
def matrix_red(essentials,dataframe):
  check_clmzero(dataframe)
  print("Starting matrix",dataframe)
  if ((dataframe.empty) or (check_cyclic(dataframe)==True)):
    return [essentials,dataframe]
  else:
    #check for essential
    es=check_essential(dataframe)  
    if(es!=False):
      essentials.append(es) #(row,column)
      es_col_elm=check_onepos(0,es[1],dataframe)
      for elm in es_col_elm:
        dataframe.drop(elm, axis = 0, inplace = True) #rows with 1s dropped
        #print(dataframe)
      dataframe.drop(es[1], axis = 1, inplace = True) #es col dropped
      print("Essential dropped",dataframe)
      return matrix_red(essentials,dataframe)
    else:  
     #check for col dom
     check1=checkfor_col(dataframe)
     if(check1!=False):
       dataframe.drop(check1[0], axis = 1, inplace = True)
       print("Dominated column dropped",dataframe)
       return matrix_red(essentials,dataframe)
     else:  
       #check for row dom
       check2=checkfor_row(dataframe)
       if(check2!=False):
          dataframe.drop(check2[0], axis = 0, inplace = True)
          print("Dominating row dropped",dataframe)
          return matrix_red(essentials,dataframe)
       
def row_intersect(sh_row_no,dataframe):
  intrsecting_rows=[]
  row_size=dataframe.index
  sh_ones=check_onepos(1,sh_row_no,dataframe)
  #len1=len(sh_ones)
  for row_no in row_size:
    if(sh_row_no!=row_no):
      row_ones=check_onepos(1,row_no,dataframe)
      #len2=len(row_ones)
      for i in range(0,len(sh_ones)):
        for j in range(0,len(row_ones)):
         if(sh_ones[i]==row_ones[j]):
          intrsecting_rows.append(row_no)
  if(len(intrsecting_rows)>0):
         return set(intrsecting_rows) 
  else:   
         return False 
  
def row_weights(row_no,dataframe):
  sum=0
  col_sum=dataframe.sum(axis=0)
  row_onepos=check_onepos(1,row_no,dataframe)
  for i in row_onepos:
    sum=col_sum[i]+sum
  return sum


def shortest_row(dataframe):
 sw=[]
 row_size=dataframe.index
 for rw_no in row_size:
   w=row_weights(rw_no,dataframe)
   sw.append(w)

 smallest=min(sw)
 for row_no in row_size:
   if(smallest==row_weights(row_no,dataframe)):
     return row_no

 

#k=shortest_row(tdft)
#print(k)

def misquick(mis,main_dataframe):
  dataframe=main_dataframe.copy()
  sr=shortest_row(dataframe)
  #print(shortest_rows)
  #sr=shortest_rows[0]
  mis.append(sr)
  cmn=row_intersect(sr,dataframe)
  #print("CMN",cmn)
  
  if(cmn!=False):
    for rw in cmn:
       dataframe.drop(rw, axis = 0, inplace = True)
    #print(after_drop=dataframe.index) 
  dataframe.drop(sr, axis = 0, inplace = True) 
  #print(dataframe)   
  if(dataframe.empty):
    return len(mis)
  else: 
    return misquick(mis,dataframe) 

#mis=[]  
#m=misquick(mis,tdft)  
#print(m)

def LowerBound(Currentsol,dataframe):
 LB=0
 mis=misquick(Currentsol,dataframe)
 #print(dataframe)
 #print(mis)
 LB=mis+len(Currentsol)
 return LB

def choose_variable(p,split,dataframe):
  if(split==1):
    #print("choosing variable for splitting")#p=1
    col_ones=check_onepos(0,p,dataframe)
    for elm in col_ones:
      dataframe.drop(elm, axis = 0, inplace = True) #rows with 1s dropped
      print(dataframe)
    dataframe.drop(p, axis = 1, inplace = True) #es col dropped
    print("variable column dropped",dataframe)
    return dataframe
  else:
    print("not choosing p") #p=0
    dataframe.drop(p, axis = 1, inplace = True)
  return dataframe

def get_splitvars(current_sol):
  cs=[]
  for c in current_sol:
    print(c)
    print(type(c))
    if(type(c)!=list):
      cs.append(c)
  #print(cs)
  return cs


def trim_CS(var,Current_Sol):
  #Current_Sol=list(Current_Sol)
  for i in range(0,len(Current_Sol)):
      if(type(Current_Sol[i])!=list):
        if(Current_Sol[i]==var):
          #print(type(Current_Sol[i]))
          print(Current_Sol[:i])
          return Current_Sol[:i]
      
 

  
df=[]

def UCP_S1(F,U,Current_Sol):
 Current_Sol,F=matrix_red(Current_Sol,F)
 #print(F)
 #print(Current_Sol)
 if F.empty:
    if(len(Current_Sol)<U):
      U=len(Current_Sol) 
      return Current_Sol
    else:
      print("No solution")
      return False  
 else:
    m=[]
    L=misquick(m,F)+len(Current_Sol)
    #print(L)
    if(L>=U):
      print("No solution")
      return False
    else:
      newdf = F.copy()
      df.append(newdf)
      print(df)
      var=F.columns
      F1=choose_variable(var[0],1,F)
      Current_Sol.append(var[0])
      S1=UCP_S1(F1,U,Current_Sol)  #currentsol returned when F=empty
      
      print(S1)
      if(len(Current_Sol)==L):
        return [Current_Sol,True]  #no need to do S0
      else:
        #CS=[Current_Sol,L]
        return [Current_Sol,df]


#c=[]
#fs1=BCP_S1(tdft,12,c)
#print(fs1)
#print(type(fs1))


def UCP_S0(F,U,Current_Sol):
  Current_Sol,F=matrix_red(Current_Sol,F)
  #print(F)
  #print(Current_Sol)
  if F.empty:
    if(len(Current_Sol)<U):
      U=len(Current_Sol) 
      return Current_Sol
    else:
      print("No solution")
      return False  
  else:
    ms=[]
    L=misquick(ms,F)+len(Current_Sol)
    #print(L)
    if(L>=U):
      print("No solution")
      return False
    else:
      #newdf = F.copy()
      #df.append(newdf)
      #print(df)
      var=F.columns
      F0=choose_variable(var[0],0,F)
      #Current_Sol.append(var[0])
      #S0=BCP_S0(F0,U,Current_Sol)  #currentsol returned when F=empty
      return UCP_S0(F0,U,Current_Sol)
      #print(S0)
      #if(len(Current_Sol)==L):
        #return Current_Sol  #best 
      #else:
        #CS=[Current_Sol,L]
        #return [Current_Sol,False] #less than UB that we got from s1 ut still not equal to lowest

def compare_soln(S1,S0):
  if((S1==False) and (S0==False)):
    print("No solution")
    return False
  elif(S0==False):
    return S1
  elif(S1==False):
    return S0
  else:
    if(len(S1)>len(S0)):
      return S0
    elif(len(S1)<len(S0)):
      return S1
    elif(len(S1)==len(S0)):
      return S1



def UCP(dataframe,UB,Current_Soln):
  F=dataframe.copy()
  print(F)
  S1=UCP_S1(dataframe,UB,Current_Soln)
  if(S1==False):
    print("No solution")
    return False
  elif(S1[1]==True):
    return S1  #optimum solution no need to do s0
  else:
    S0=[]
    s1_soln=S1[0]
    print(type(s1_soln))
    s1_dataframes=S1[1]
    vars=get_splitvars(s1_soln)
    #l=len(vars)
    for v in range( len(vars) - 1, -1, -1) :
      print(s1_dataframes[v])
      print(vars[v])
      f0=choose_variable(vars[v],0,s1_dataframes[v])
      cs=trim_CS(vars[v],s1_soln)
      print(cs)
      s0=UCP_S0(f0,len(s1_soln),cs)
      if(s0!=False):
       S0.append(s0)

    if(len(S0)==0):
      return s1_soln
    else:
      return compare_soln(s1_soln,S0[0])


# c=[]
# test=BCP(tdft,12,c)
# print(test)


ic=[]
intial_UB=len(my_df.columns)
result=UCP(my_df,intial_UB,ic)
print(result)




        