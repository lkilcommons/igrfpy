import os
import glob
# Code is still under GPLv3 as per superDARN licensing
# CU SEDA has broken it out from DavitPy for solo usage
os.environ['DISTUTILS_DEBUG'] = "1"

from setuptools import setup, Extension
from setuptools.command import install as _install
from numpy.distutils.core import setup, Extension


# Fortran extensions
igrf = Extension("igrf",sources=["igrfpy/igrf11.f90",'igrfpy/igrf11.pyf'])

setup(name='igrfpy',
      version = "0.1",
      description = "International Geomagnetic Reference Field 11 Wrapper",
      #author = "VT SuperDARN Lab and friends",
      #author_email = "ajribeiro86@gmail.com",
      author = "CU SEDA Group",
      author_email = "liam.kilcommons@colorado.edu",
      url = "",
      download_url = "https://github.com/lkilcommons/igrfpy",
      #packages =
      long_description = "",
      zip_safe = False,
      ext_modules = [igrf],
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

