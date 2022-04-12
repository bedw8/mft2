#! /usr/bin/python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Cargamos datos
d1 = pd.read_csv('data/1501.dat')
d2 = pd.read_csv('data/1508.dat')

# Agregamos fecha
d1.loc[:,'month'] = 1
d2.loc[:,'month'] = 8
df = pd.concat([d1,d2])
df.loc[:,'day'] = 15
df.loc[:,'year'] = 1997

# Nos quedamos con columnas relevantes  
df = df[['PRES','TEMP','MIXR','day','month','year']]

# Corregimos unidades 
df.MIXR = df.MIXR/1000
df.PRES = df.PRES*100
df.TEMP = df.TEMP + 273.15

# Definimos funciones para el cálculo de la temperatura virtual y la densidad
def Tv(T,q):
    return T*(1 + 0.61*q)

def rho(P,Tv):
    Rd = 287.04
    return P/(Rd*Tv)

# Calculamos la temperatura virtual y la densidad
df['Tv'] = Tv(df.TEMP,df.MIXR)
df['rho'] = rho(df.PRES,df.Tv)

d1 = df[df.month == 1].copy()
d2 = df[df.month == 8].copy()

# Definimos función para calcular la altura según la atmósfera standard
def isaZ1(P,T0,P0):
    m = -6.5/1000
    R = 287.04
    g = 9.78
    return (T0/m)*(np.power(P/P0,-(m*R/g)) - 1)

def consecutive_deltas(s):
    s2 = s.shift(-1)[:-1]
    s1 = s[:-1]
    return pd.concat([pd.Series(0),s2 - s1]).reset_index(drop=True)

def consecutive_ratio(s):
    s2 = s.shift(-1)[:-1]
    s1 = s[:-1]
    return pd.concat([pd.Series(1),s2/s1]).reset_index(drop=True)

def hypsoZ2(T,P):
    dT = consecutive_deltas(T)
    ratioP = consecutive_ratio(P)

    T_mean = T + dT/2
    
    R = 287.04
    g = 9.78
    
    dz = R*T_mean*np.log(1/ratioP)/g

    z = dz.cumsum()

    return z

d1.loc[:,'Z1'] = isaZ1(d1.PRES,d1.Tv[0],d1.PRES[0])
d1.loc[:,'Z2'] = hypsoZ2(d1.Tv,d1.PRES)

d2.loc[:,'Z1'] = isaZ1(d2.PRES,d2.Tv[0],d2.PRES[0])
d2.loc[:,'Z2'] = hypsoZ2(d2.Tv,d2.PRES)



latex_cols = ['Pres. [Pa]', 'Temp [K]', r'$q$','Virt.Temp [K]', r'$\rho$ [Kg/m$^3$]', 'Z1 [m]' , 'Z2 [m]']
latex_cols_format = 'lllllll'
d1.drop(columns=['day','month','year']).to_latex('tbl1.tex',header=latex_cols,column_format=latex_cols_format,index=False,escape=False)
d2.drop(columns=['day','month','year']).to_latex('tbl2.tex',header=latex_cols,column_format=latex_cols_format,index=False,escape=False)


#### Plots
sns.set_context('paper')
### Z1 

f1, ax = plt.subplots(1,1)
ax.scatter(d1.TEMP,d1.Z1,s=10,label='Verano')
ax.plot(d1.TEMP,d1.Z1)
ax.scatter(d2.TEMP,d2.Z1,s=10,label='Invierno')
ax.plot(d2.TEMP,d2.Z1)
ax.set_ylabel('Z1 [m]')
ax.set_xlabel('Temperatura [K]')

ax.legend()
f1.savefig('Z1.png')

### Z2

f2, ax = plt.subplots(1,1)
ax.scatter(d1.TEMP,d1.Z2,s=10,label='Verano')
ax.plot(d1.TEMP,d1.Z2)
ax.scatter(d2.TEMP,d2.Z2,s=10,label='Invierno')
ax.plot(d2.TEMP,d2.Z2)
ax.set_ylabel('Z2 [m]')
ax.set_xlabel('Temperatura [K]')

ax.legend()
f2.savefig('Z2.png')


