# Traslation of shortwavc.aml (written by Lalit Kumar and Niklaus E. Zimmermann) from aml to python
# Original was developed based on Kumar, L., Skidmore, A.K., Knowles, E., (1997) Modelling  Topographic Variation in Solar Radiation in a GIS Environment. International Journal of Geographical Information Science, 11(5): 475-497.
# Result differs from aml output slightly, probably from rounding errors
# I probably trust the math in python slightly better than Arc
# Lee F. Elliott 7/20/2012

import arcinfo
from arcpy import env
import arcpy
from arcpy.sa import *
import math
from time import time
from string import zfill
from datetime import date
import sys
import os

#env.workspace = "e:/workspace/p6"
env.workspace = sys.path[0]

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        print "Spatial Analyst license is AVAILABLE"
    else:
        # raise a custom exception
        #
        raise LicenseError

except LicenseError:
    print "Spatial Analyst license is unavailable"
except:
    print arcpy.GetMessages(2)

# cover = "30m_guads"
cover = raw_input('Enter DEM grid name: ')
outgrid = raw_input('Enter output grid name: ')
#latdeg = 31.5
latdeg = float(raw_input('Enter latitude in decimal degrees: '))
#daystart = 80
daystart = int(raw_input('Enter julian date for day to start calculation: '))
#dayend = 80
dayend = int(raw_input('Enter julian date for day to end calculation: '))
# interval = 60
interval = int(raw_input('Enter time interval in minutes: '))
starttime = time()
daynumber = daystart
timev = interval * 0.0043633
deg2rad = math.pi/180
latitude = latdeg * deg2rad
slopegrid2 = (Slope(cover, "DEGREE")) * deg2rad
cosslope = Cos(slopegrid2)
sinslope = Sin(slopegrid2)
aspectgrid = Aspect(cover)
aspectgrid1 = Con(aspectgrid, 0, aspectgrid, "VALUE == -1")
aspectgrid1 = Con(aspectgrid, 180 - aspectgrid, aspectgrid1, "VALUE <= 180 & VALUE <> -1")
aspectgrid1 = Con(aspectgrid, 540 - aspectgrid, aspectgrid1, "VALUE > 180")
aspectgrid2 = aspectgrid1 * deg2rad
cosaspect = Cos(aspectgrid2)
sinaspect = Sin(aspectgrid2)
outgrid0 = Hillshade(cover, 0, 0, "SHADOWS", 1)
initialgrid = outgrid0 * 0
tanlat = math.tan(latitude)
sinlat = math.sin(latitude)
asinlat = math.asin(latitude)
coslat = math.cos(latitude)
acosminusone = math.acos(-1)
acosone = math.acos(1)

while daynumber <= dayend:
	# solar radiation, Kumar et al 1997, Eq. 7
	vio = 1.367 * (1 + 0.0344 * math.cos(360 * deg2rad * daynumber / 365))
	# solar declination, Kumar et al 1997, Eq. 4
	decl = 23.45 * deg2rad * math.sin(deg2rad * 360 * (284 + daynumber)/365)
	tandecl = math.tan(decl)
	cosdecl = math.cos(decl)
	sindecl = math.sin(decl)
	if ((-1 * tanlat * tandecl) < -1):
		sunrise = acosminusone
	elif ((-1 * tanlat * tandecl) > 1.0):
		sunrise = acosone
	else:
		sunrise = math.acos(-1 * tanlat * tandecl)
	sunset = -1 * sunrise
	hourangle = sunrise - (timev / 2)
	vpass = 1
	#print "vio: " + str(vio)
	#print "decl: " + str(decl)
	#print "sunrise: " + str(sunrise)
	#print "sunset: " + str(sunset)
	#print "hourangle: " + str(hourangle)
  
	while (hourangle >= sunset):
		coshour = math.cos(hourangle)
		sinhour = math.sin(hourangle)
		solaralt = math.asin(sinlat * sindecl + coslat * cosdecl * coshour)
		cossolalt = math.cos(solaralt)
		sinsolalt = math.sin(solaralt)
		vtest = tandecl/tanlat
		if (coshour > vtest):
			solaraz = math.asin(cosdecl * sinhour/cossolalt)
		elif (coshour < vtest):
			solaraz = math.pi - math.asin(cosdecl * sinhour/cossolalt)
		elif (vtest == coshour & hourangle >= 0):
			solaraz = math.pi/2
		elif (vtest == coshour & hourangle < 0):
			solaraz = -1 * math.pi/ 2
		if (solaraz >= 0):
			solarazdeg = solaraz * 57.29578
		else:
			solarazdeg = 360 - (abs(solaraz) * 57.29578)
		# Air mass correction, Kumar et al 1997, Eq. 11
		M = (math.sqrt(1229 + (614 * sinsolalt)**2))-614 * sinsolalt
		# e = 2.7182818
		# Tau is atmospheric transmittance, Kumar et al 1997, Eq. 14
		# tau = 0.56 * (e ** (-0.65 ** M) + e ** (-0.095 ** M)
		# Shortwave solar radiation striking surface normal to sun, Kumar et al 1997, Eq. 
		# vis = vio * tau
		vis = vio * 0.56 * (math.exp(-0.65 * M) + math.exp(-0.095 * M))
		solaraltdeg = solaralt * 57.29578
		if (solarazdeg <= 180):
			azi = 180 - solarazdeg
		else:
			azi = 180 + (360 - solarazdeg)
		sungrid = Hillshade(cover, azi, solaraltdeg, "SHADOWS", 1)
		sungrid2 = Con(sungrid, 1, 0, "VALUE > 0")

		#print "solaralt: " + str(solaralt)
		#print "vtest: " + str(vtest)
		#print "solaraz: " + str(solaraz)
		#print "solarazdeg: " + str(solarazdeg)
		#print "M: " + str(M)
		#print "vis: " + str(vis)
		#print "solaraltdeg: " + str(solaraltdeg)
		#print "azi: " + str(azi)
		cosi = sindecl * (sinlat * cosslope - coslat * sinslope * cosaspect) + cosdecl * coshour * (coslat * cosslope + sinlat * sinslope * cosaspect) + cosdecl * sinslope * sinaspect * sinhour
		shaded = Con(cosi, 0, 1, "VALUE < 0")
		wattsgrid = vis * cosi * sungrid2 * shaded * 60 * interval
		initialgrid = wattsgrid + initialgrid
		hourangle = hourangle - timev
		vpass = vpass + 1
	daynumber = daynumber + 1
initialgrid = Int(initialgrid)
initialgrid.save(outgrid)
print "process time = " + elapsed_time(starttime) + ".\n"
		