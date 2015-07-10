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
	
	BE,BN,BU = [],[],[] 
	print "Running IGRF for %d values" % (len(lats))
	for k in range(len(lats)):
		colat = 90.-lats[k]
		elong = lons[k] if lons[k] > 0. else 360. + lons[k]
		alt = alts[k] if not geocentric or altisradius else alts[k] + 6371.2 #Add earth radius if using geocentric
		yr = times[k].year+times[k].month/12.
		be,bn,bu,f = igrf11syn(0,yr,itype,alt,colat,elong)
		BE.append(be)
		BN.append(bn)
		BU.append(bu)

	return BE,BN,BU