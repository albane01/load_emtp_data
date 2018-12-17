# Post treatment of EMTP and Parametric Studio

## Description of the project
This project is intended for EMTP and Parametric Studio users. 
Users can load the data of an EMTP simulation or numerous EMTP simulations performed with parametric Studio.
The data loaded can then be used for specific post treatment. 

### Description of files
* simulation.py   
	* Class ParamSimulation determines position in .mda file of all signals in the white list
	* Class Simulation loads the data of all signals in the white list for a simulation EMTP
	* Class Simulations loads the data of all signals in the white list for a Parametric Studio simulation  
* pss\_reader.py  
	* Class PssParams creates a dictionnary containing the variable parameters of a Parametric Simulation

### The user should define the white list
The white list is the list of signals to load  
The white list must have the following format ['signal1', 'signal2',...] 

### To get the parameters of a simulation
Build an object of class ParamSimulation with path of .m file and white list as arguments
```
Ps = ParamSimulation(mpath, white list)
```
domain() returns the domain of the simulation (frequency or time)
```
print('domain of simulation : ', Ps.domain)
```
the object returns the parameters of m file
```
print('parameters of m file : ', Ps)
``` 

### To load data of a simulation with EMTP
Build an object of class Simulation with path of .mda file, path of .m file and white list as arguments
```
s = Simulation(mdapath, mpath, white list)  
s.load_data()
```
get\_ftmin() returns the minimum time or frequency value
```
print('ftmin : ', s.get_ftmin())
```
get\_ftmax() returns the maximum time or frequency value
```
print('ftmax : ', s.get_ftmax())
```
get\_ftdelta() returns the frequency or time step
```
print('simulation step : ', s.get_ftdelta())
```

### To visualize the first signal of the white list
Import pyplot from libray matplotlib 
```
from matplotlib import pyplot as plt
```
plot() draw the signal as function of frequency or time
```
plt.plot(s._ft, s._data[0], linewidth=3.0)  
plt.show()
```

### To load data of a parametric simulation with Parametric Studio
Build an object of class Simulations with path of simulation, name of emtp file and white list as arguments  
Path of simulation must indicate the repertory containing CP\_00001 ... repertories
```
S = Simulations(simulation path, name of emtp file, white list)  
S.build_all_simulations()
```

### To visualize the first signal of the white list in the first simulation
get\_simulation(i) returns simulation i 
```
s0 = S.get_simulation(0)  
plt.plot(s0._ft, s0._data[0], linewidth=3.0)  
plt.show()
```

### To get the parameters of Parametric Studio 
Build an object of class Parametric Studio with path of pss file
```
Pss =  PssParams(pss path)
```
attribute ord\_keys returns the parameters 
```
print('parameters of Parametric Studio : ', Pss.ord_keys)
```
attribute \_values returns the parameters 
```
print('values of Parametric Studio : ', Pss._values)
```
