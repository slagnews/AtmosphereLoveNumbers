# AtmosphereLoveNumbers
This repository contains the code that was created to figure out the effect of a planet's atmosphere, and the potential loss of said atmosphere, on the planet's tidal Love number $k_2$, and the resulting migration rate. The calculation of Love numbers was done using the ![ALMA3](https://github.com/danielemelini/ALMA3) package.

To study this effect, I used a simple two-layer planetary model:
- A rocky core, represented by a Maxwell rheology, with homgeneous density, viscosity and rigidity.
- A gaseous atmosphere surrounding this core, represented by a Newton rheology, with homogeneous density and viscosity.
The fiducial model uses the radius, density, viscosity and rigidity of the Earth for the rocky core, and the density and viscosity of air for the atmosphere. The size of the atmosphere is varied from non-existent all the way up to the radius of Jupiter to study the effect of atmosphere size on the tidal Love number. The results for this fiducial model can be seen below


### How to use this code
To use the code in this repository, clone the repository inlucluding submodules, to include ALMA3:
```git clone --recurse-submodules git@github.com:slagnews/AtmosphereLoveNumbers.git```
Then, inside the repository, build the ALMA3 submodule using
```cd ALMA3/src```
```make```
Now you can have a look at the Jupyter Notebooks that use ALMA3 for various models.

### File overview
