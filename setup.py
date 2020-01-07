import os
import glob
# Code is still under GPLv3 as per superDARN licensing
# CU SEDA has broken it out from DavitPy for solo usage
os.environ['DISTUTILS_DEBUG'] = "1"

from setuptools import setup, Extension
from setuptools.command import install as _install
from numpy.distutils.core import setup, Extension

# Fortran extensions
igrf11 = Extension("igrf11",sources=["igrfpy/igrf11.f"],extra_f77_compile_args=["-w"])
igrf12 = Extension("igrf12",sources=["igrfpy/igrf12.f"],extra_f77_compile_args=["-w"])

setup(name='igrfpy',
      version = "0.2",
      description = "International Geomagnetic Reference Field 11&12 Wrapper",
      #author = "VT SuperDARN Lab and friends",
      #author_email = "ajribeiro86@gmail.com",
      author = "CU SEDA Group",
      author_email = "liam.kilcommons@colorado.edu",
      url = "",
      download_url = "https://github.com/lkilcommons/igrfpy",
      packages=['igrfpy'],
      package_dir={'igrfpy' : 'igrfpy'},
      long_description = "",
      zip_safe = False,
      ext_modules = [igrf11,igrf12],
      install_requires=[],
      classifiers = [
            "Development Status :: 4 - Beta",
            "Topic :: Scientific/Engineering",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Natural Language :: English",
            "Programming Language :: Python"
            ],
      )

