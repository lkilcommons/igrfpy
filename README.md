# igrfpy
Python wrappers on the International Geomagnetic Reference Field 11 and 12 Fortran code

This code is mostly the work of VT SuperDARN's [ DavitPy Project ](https://github.com/vtsuperdarn/davitpy) and 
of course the original IGRF authors. 

The contributions here are a simplified interface (getmainfield function) which 
operates on a list of locations and datetime (or date) objects and a seperate install script.

I have also updated the module to use the 12-th generation of the IGRF (igrf12) and added pytest unit tests
