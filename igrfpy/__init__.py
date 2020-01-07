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

def invartolist(invar,expected_scalar_type):
	"""Parse an input variable from a list, single value, or numpy
	array into a flat list"""
	if not isinstance(invar,list):
		if isinstance(invar,np.ndarray):
			if len(invar.shape) > 1 and all([dim > 1 for dim in invar.shape]):
				raise ValueError(('2D numpy arrays that are not column'
								 +' or row vectors are not allowed as inputs'))
			listvar = invar.flatten().tolist()
		elif isinstance(invar,expected_scalar_type):
			listvar = [invar] # Deal with possibility of single altitude/radius
		else:
			raise ValueError('Unable to convert input'
							 'variable {} to a list'.format(invar))
	else:
		listvar = invar

	return listvar


def getmainfield(intimes,inlats,inlons,inalts,geocentric=True,altisradius=False,silent=False,igrf11=False):
	"""Takes times, latitudes, longitudes and altitudes and returns
	east north and up components of main field.

	Allows time and location inputs as single values, lists, or numpy arrays.


	PARAMETERS
	----------

		intimes - datetime.datetime, list, or np.ndarray
			Datetime for desired magnetic field value
		inlats - float, list, or np.ndarray
			Latitude in degrees
		inlons - float, list or np.ndarray
			Longitude in degrees
		inalts - float, list or np.ndarray
			Altitude in km
		geocentric - bool, optional
			If True (default) input latitudes are assumed to be geocentric,
			if False, they will be treated as geodetic
		altisradius - bool, optional
			If False (default) altitude is assumed to be height above
			earth's surface in kilometers.
			If True, altitude is taken as distance from the earth's center,
			in kilometers
		silent - bool, optional
			Default is False. If True, no messages will be printed
		igrf11 - bool, optional
			If False (default), IGRF12 is used, if True, IGRF11 is used

	RETURNS
	-------

		BE - list
			Eastward magnetic field in nT
		BN - list
			Northward magnetic field in nT
		BU - list
			Upward magnetic field in nT


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

	#Make inputs into flat lists, regardless of their original type
	times = invartolist(intimes,datetime.datetime)
	lats = invartolist(inlats,float)
	lons = invartolist(inlons,float)
	alts = invartolist(inalts,float)

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
		alt = alts[k] if k < len(alts) else alts[-1]
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
