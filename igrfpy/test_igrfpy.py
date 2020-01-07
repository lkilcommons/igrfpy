import pytest
import numpy as np
import datetime
from igrfpy import igrf11,igrf12,getmainfield

#From NCEI IGRF Calculator (using igrf12)
# https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm
# (retrieved Jan 7, 2020)
ncei_output = {
  "result": [
    {
      "date": 2010.01644,
      "elevation": 1.60934,
      "inclination": 66.68529,
      "ycomponent": 3378.3,
      "totalintensity_sv": -121.3,
      "horintensity": 20979.9,
      "latitude": 39.99111,
      "zcomponent": 48680.4,
      "zcomponent_sv": -124,
      "declination": 9.26632,
      "ycomponent_sv": -45.4,
      "declination_sv": -0.11722,
      "xcomponent_sv": -11.7,
      "xcomponent": 20706.1,
      "totalintensity": 53008.8,
      "inclination_sv": -0.03435,
      "longitude": -105.23278,
      "horintensity_sv": -18.8
    }
  ],
  "model": "IGRF2015",
  "units": {
    "inclination": "degrees",
    "elevation": "km",
    "ycomponent": "nanoTesla (nT)",
    "totalintensity_sv": "nanoTesla (nT)",
    "horintensity": "nanoTesla (nT)",
    "latitude": "degrees",
    "zcomponent": "nanoTesla (nT)",
    "zcomponent_sv": "nanoTesla (nT)",
    "declination": "degrees",
    "ycomponent_sv": "nanoTesla (nT)",
    "declination_sv": "degrees",
    "xcomponent_sv": "nanoTesla (nT)",
    "xcomponent": "nanoTesla (nT)",
    "totalintensity": "nanoTesla (nT)",
    "inclination_sv": "degrees",
    "horintensity_sv": "nanoTesla (nT)",
    "longitude": "degrees"
  },
  "version": "0.5.1.7"
}

#Fortran function
def ncei_igrfsyn_inouts():
    #Example apparently uses geocentric latitude
    geocentric = False

    data = ncei_output['result'][0]
    isv = 0 #0 for main field, 1 for secular variation
    decimal_year = data['date']
    itype = 2 if geocentric else 1#1 for geodetic, 2 for geocentric
    alt = data['elevation']+6371.2 if geocentric else data['elevation'] #km
    colat = 90.-data['latitude']
    elon = data['longitude']
    if elon < 0:
        elon += 360.
    syn_inargs = (isv,decimal_year,itype,alt,colat,elon)

    syn_outargs = (data['xcomponent'],
                data['ycomponent'],
                data['zcomponent'],
                data['totalintensity'])

    return syn_inargs,syn_outargs

def ncei_getmainfield_ins():
    data = ncei_output['result'][0]
    decimal_year = data['date']
    year = int(np.floor(decimal_year))
    doy = (365. if np.mod(year,4)!=0 else 366.) * (decimal_year - year)
    dt = datetime.datetime(year,1,1)+datetime.timedelta(days=doy-1)
    lat = data['latitude']
    lon = data['longitude']
    alt = data['elevation']
    return dt,lat,lon,alt

def ncei_getmainfield_outs():
    data = ncei_output['result'][0]
    decimal_year = data['date']
    year = np.floor(decimal_year)
    doy = (365. if np.mod(year,4)!=0 else 366. * decimal_year - year)
    be = data['ycomponent']
    bn = data['xcomponent']
    bu = -1*data['zcomponent']
    return be,bn,bu

def test_igrf12_b_same_as_ncei():

    syn_inargs,syn_outargs_expected = ncei_igrfsyn_inouts()

    print(syn_inargs)
    syn_outargs = igrf12.igrf12syn(*syn_inargs)

    tol = .5 #nT

    #B North
    assert np.abs(syn_outargs[0]-syn_outargs_expected[0])<tol
    #B East
    assert np.abs(syn_outargs[1]-syn_outargs_expected[1])<tol
    #B Down
    assert np.abs(syn_outargs[2]-syn_outargs_expected[2])<tol
    #B Total
    assert np.abs(syn_outargs[3]-syn_outargs_expected[3])<tol

#Python Interface
def ex_as_arr(example_value,shape):
    """Make arrays or lists of input shape of an example value"""
    if shape is None:
        return example_value
    elif isinstance(shape,int):
        return [example_value] * shape
    elif isinstance(shape,tuple):
        array_type = 'object' if isinstance(example_value,datetime.datetime) else float
        example_arr = np.full(shape,example_value,dtype=array_type)
        return example_arr
    else:
        raise ValueError('Invalid inputs')

@pytest.mark.parametrize('t_shape,latlon_shape,alt_shape',
                         [(None,None,None),# All scalar inputs
                            (3,3,3), # All list inputs
                            ((3,),(3,),(3,)), # All 1D array inputs
                            ((3,1),(3,1),(3,1)), # All 2D array inputs
                            (3,None,None)]) #List and scalars

def test_getmainfield_against_ncei(t_shape,latlon_shape,alt_shape):
    dt,lat,lon,alt = ncei_getmainfield_ins()

    dts = ex_as_arr(dt,t_shape)
    lats = ex_as_arr(lat,latlon_shape)
    lons = ex_as_arr(lon,latlon_shape)
    alts = ex_as_arr(alt,alt_shape)

    bes,bns,bus = getmainfield(dts,lats,lons,alts,altisradius=False,geocentric=False)

    besarr = np.array(bes)
    bnsarr = np.array(bns)
    busarr = np.array(bus)


    be_exp,bn_exp,bu_exp = ncei_getmainfield_outs()

    tol = .5

    #East
    np.testing.assert_allclose(besarr,np.ones_like(besarr)*be_exp,rtol=0,atol=tol)
    #North
    np.testing.assert_allclose(bnsarr,np.ones_like(bnsarr)*bn_exp,rtol=0,atol=tol)
    #Up
    np.testing.assert_allclose(busarr,np.ones_like(busarr)*bu_exp,rtol=0,atol=tol)

