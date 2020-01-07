# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# Broken out from DavitPy by University of Colorado
# SEDA Group in 2014.
"""
*********************
**Module**: models.igrf
*********************
Basic plotting tools

**Modules**:
  * :mod:`models.igrf`: fortran subroutines

"""
import numpy as np
import datetime
import igrf11
import igrf12

def getmainfield(times,lats,lons,alts,geocentric=True,altisradius=False,silent=False,igrf11=False):
	"""Takes lists of times, latitudes, longitudes and altitudes;
	returns east north and up components of main field

	Explaination of IGRF inputs/output from original fortran source

	c
	c     This is a synthesis routine for the 12th generation IGRF as agreed
	c     in December 2014 by IAGA Working Group V-MOD. It is valid 1900.0 to
	c     2020.0 inclusive. Values for dates from 1945.0 to 2010.0 inclusive are
	c     definitive, otherwise they are non-definitive.
	c   INPUT
	c     isv   = 0 if main-field values are required
	c     isv   = 1 if secular variation values are required
	c     date  = year A.D. Must be greater than or equal to 1900.0 and
	c             less than or equal to 2025.0. Warning message is given
	c             for dates greater than 2020.0. Must be double precision.
	c     itype = 1 if geodetic (spheroid)
	c     itype = 2 if geocentric (sphere)
	c     alt   = height in km above sea level if itype = 1
	c           = distance from centre of Earth in km if itype = 2 (>3485 km)
	c     colat = colatitude (0-180)
	c     elong = east-longitude (0-360)
	c     alt, colat and elong must be double precision.
	c   OUTPUT
	c     x     = north component (nT) if isv = 0, nT/year if isv = 1
	c     y     = east component (nT) if isv = 0, nT/year if isv = 1
	c     z     = vertical component (nT) if isv = 0, nT/year if isv = 1
	c     f     = total intensity (nT) if isv = 0, rubbish if isv = 1
	c
	c     To get the other geomagnetic elements (D, I, H and secular
	c     variations dD, dH, dI and dF) use routines ptoc and ptocsv.
	c
	c     Adapted from 8th generation version to include new maximum degree for
	c     main-field models for 2000.0 and onwards and use WGS84 spheroid instead
	c     of International Astronomical Union 1966 spheroid as recommended by IAGA
	c     in July 2003. Reference radius remains as 6371.2 km - it is NOT the mean
	c     radius (= 6371.0 km) but 6371.2 km is what is used in determining the
	c     coefficients. Adaptation by Susan Macmillan, August 2003 (for
	c     9th generation), December 2004, December 2009 & December 2014.
	c
	c     Coefficients at 1995.0 incorrectly rounded (rounded up instead of
	c     to even) included as these are the coefficients published in Excel
	c     spreadsheet July 2005.
	c
	"""

	itype = 2 if geocentric else 1

	if not isinstance(times,list):
		if isinstance(times,np.ndarray):
			times = times.flatten().tolist()
		elif isinstance(times,datetime.datetime):
			times = [times] # Deal with possibility of single time
		else:
			raise ValueError('Unable to convert times'
							 'variable {} to a list'.format(times))

	if not isinstance(alts,list):
		if isinstance(alts,np.ndarray):
			alts = alts.flatten().tolist()
		elif isinstance(alts,float):
			alts = [alts] # Deal with possibility of single altitude/radius
		else:
			raise ValueError('Unable to convert altitudes'
							 'variable {} to a list'.format(alts))

	if not isinstance(lons,list):
		if isinstance(lons,np.ndarray):
			lons = lons.flatten().tolist()
		elif isinstance(lons,float):
			lons = [lons] # Deal with possibility of single longitude
		else:
			raise ValueError('Unable to convert longitudes'
							 'variable {} to a list'.format(lons))

	if not isinstance(lats,list):
		if isinstance(lats,np.ndarray):
			lats = lats.flatten().tolist()
		elif isinstance(lats,float):
			lats = [lats] # Deal with possibility of single latitude
		else:
			raise ValueError('Unable to convert latitudes'
							 'variable {} to a list'.format(lats))

	#Standarize altitude to height if it was input as radius
	if altisradius:
		alts = [alt-6371.2 for alt in alts]

	#Convert height to radius if we are doing calculations
	#using geocentric
	if geocentric:
		alts = [alt+6371.2 for alt in alts]

	#Check that radial distances are sane
	#if using geocentric
	if geocentric:
		if any(alt < 3485. for alt in alts):
			raise ValueError('Error: IGRF not valid for altitudes < -3485 km')

	# Deterimine which input has the largest number of values
	lengths = [len(alts),len(times),len(lats),len(lons)]
	niters = max(lengths)

	# Check that we either have 1 input value for each variable or
	# one value for each iteration
	for varlist in [times,alts,lats,lons]:
		if len(varlist) not in [1,niters]:
			raise ValueError('Unexpected number of inputs:'
							 'Input {}, '.format(varlist),
							 'Expected length 1 or {}'.format(niters))

	BE,BN,BU = [],[],[]
	if not silent:
		print "Running IGRF for %d values" % (len(lats))
	for k in range(niters):
		colat = 90.-lats[k] if k < len(lats) else 90.-lats[-1]
		lon = lons[k] if k < len(lons) else lons[-1]
		elong = lon if lon > 0. else 360. + lon
		alt = alts[k] if k < len(times) else alts[-1]
		time = times[k] if k < len(times) else times[-1]
		#Use closest epoch to month of data, probably sufficient precision
		#Initial 0 means use main field not secular variation
		#Calculate epoch / decimal year to the closest day
		year_days = 366. if np.mod(time.year,4)==0 else 365.
		doy = float(time.timetuple().tm_yday)
		t_years = time.year+doy/year_days
		if igrf11:
			bn,be,bd,f = igrf11.igrf11syn(0,t_years,
											itype,alt,colat,elong)
		else:
			print(t_years,alt,colat,elong)
			bn,be,bd,f = igrf12.igrf12syn(0,t_years,
											itype,alt,colat,elong)

		BE.append(be)
		BN.append(bn)
		BU.append(-1*bd)

	return BE,BN,BU
