# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# Broken out from DavitPy by University of Colorado
# SEDA Group in 2014. We claim no copyright.
"""
*********************
**Module**: models.igrf
*********************
Basic plotting tools

**Modules**:
  * :mod:`models.igrf`: fortran subroutines

"""

try:
    from igrf import *
except Exception, e:
    print __file__+' -> igrf: ', e

def getmainfield(times,lats,lons,alts,geocentric=True,altisradius=False):
	"""Takes lists of times, latitudes, longitudes and altitudes, and returns east north and up components of main fields"""
	# Call fortran subroutine

	#Explaination of IGRF inputs/output from original fortran source

# 	This is a synthesis routine for the 11th generation IGRF as agreed 
# c     in December 2009 by IAGA Working Group V-MOD. It is valid 1900.0 to
# c     2015.0 inclusive. Values for dates from 1945.0 to 2005.0 inclusive are 
# c     definitive, otherwise they are non-definitive.
# c   INPUT
# c     isv   = 0 if main-field values are required
# c     isv   = 1 if secular variation values are required
# c     date  = year A.D. Must be greater than or equal to 1900.0 and 
# c             less than or equal to 2020.0. Warning message is given 
# c             for dates greater than 2015.0. Must be double precision.
# c     itype = 1 if geodetic (spheroid)
# c     itype = 2 if geocentric (sphere)
# c     alt   = height in km above sea level if itype = 1
# c           = distance from centre of Earth in km if itype = 2 (>3485 km)
# c     colat = colatitude (0-180)
# c     elong = east-longitude (0-360)
# c     alt, colat and elong must be double precision.
# c   OUTPUT
# c     x     = north component (nT) if isv = 0, nT/year if isv = 1
# c     y     = east component (nT) if isv = 0, nT/year if isv = 1
# c     z     = vertical component (nT) if isv = 0, nT/year if isv = 1
# c     f     = total intensity (nT) if isv = 0, rubbish if isv = 1
# c
# c     To get the other geomagnetic elements (D, I, H and secular
# c     variations dD, dH, dI and dF) use routines ptoc and ptocsv.
# c
# c     Adapted from 8th generation version to include new maximum degree for
# c     main-field models for 2000.0 and onwards and use WGS84 spheroid instead
# c     of International Astronomical Union 1966 spheroid as recommended by IAGA
# c     in July 2003. Reference radius remains as 6371.2 km - it is NOT the mean
# c     radius (= 6371.0 km) but 6371.2 km is what is used in determining the
# c     coefficients. Adaptation by Susan Macmillan, August 2003 (for 
# c     9th generation), December 2004 & December 2009.
# c
# c     Coefficients at 1995.0 incorrectly rounded (rounded up instead of
# c     to even) included as these are the coefficients published in Excel 
# c     spreadsheet July 2005.
	
	
	itype = 2 if geocentric else 1
	if geocentric and not altisradius: 
		alts = alts + 6371.2 #Add earth radius if using geocentric

	if not isinstance(times,list):
		times = [times] # Deal with possibility of single time

	if not isinstance(alts,list):
		alts = [alts] # Deal with possibility of single altitude/radius

	if not isinstance(lons,list):
		lons = [lons] # Deal with possibility of single longitude
	
	if not isinstance(lats,list):
		lats = [lats] # Deal with possibility of single latitude
		

	niters = max([len(alts),len(times),len(lats),len(lons)]) 
	# Deterimine which input has the largest number of values
	# Inputs which run out of values just keep repeating last value until
	# the number of interations runs out

	BE,BN,BU = [],[],[] 
	print "Running IGRF for %d values" % (len(lats))
	for k in range(niters):
		colat = 90.-lats[k] if k < len(lats) else 90.-lats[-1]
		lon = lons[k] if k < len(lons) else lons[-1]
		elong = lon if lon > 0. else 360. + lon
		alt = alts[k] if k < len(times) else alts[-1]
		time = times[k] if k < len(times) else times[-1]
		#Use closest epoch to month of data, probably sufficient precision
		#Initial 0 means use main field not secular variation
		bn,be,bd,f = igrf11syn(0,time.year+time.month/12.,  
								itype,alt,colat,elong) # NED coordinates to ENU for return
		BE.append(be)
		BN.append(bn)
		BU.append(-1*bd)

	return BE,BN,BU