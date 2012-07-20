# Traslation of shortwavc.aml (written by Lalit Kumar and Niklaus E. Zimmermann) from aml to python
# Result differs from aml output slightly, probably from rounding errors
# I probably trust the math in python slightly better than Arc
# Lee F. Elliott 7/20/2012

import arcinfo
from arcpy import env
import arcpy
from arcpy.sa import *
import math
env.workspace = "e:/workspace/p6"


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
daynumber = daystart
timev = interval * 0.0043633
deg2rad = math.pi/180
latitude = latdeg * deg2rad
slopegrid2 = (Slope(cover, "DEGREE")) * deg2rad
aspectgrid = Aspect(cover)
aspectgrid1 = Con(aspectgrid, 0, aspectgrid, "VALUE == -1")
aspectgrid1 = Con(aspectgrid, 180 - aspectgrid, aspectgrid1, "VALUE <= 180 & VALUE <> -1")
aspectgrid1 = Con(aspectgrid, 540 - aspectgrid, aspectgrid1, "VALUE > 180")
aspectgrid2 = aspectgrid1 * deg2rad
outgrid0 = Hillshade(cover, 0, 0, "SHADOWS", 1)
initialgrid = outgrid0 * 0
tanlat = math.tan(latitude)
sinlat = math.sin(latitude)
asinlat = math.asin(latitude)
coslat = math.cos(latitude)
acosminusone = math.acos(-1)
acosone = math.acos(1)

while daynumber <= dayend:
	vio = 1.367 * (1 + 0.034 * math.cos(360 * deg2rad * daynumber / 365))
	decl = 23.45 * deg2rad * math.sin(deg2rad * 360 * (284 + daynumber)/365)
	if ((-1 * tanlat * math.tan(decl)) < -1):
		sunrise = acosminusone
	elif ((-1 * tanlat * math.tan(decl)) > 1.0):
		sunrise = acosone
	else:
		sunrise = math.acos(-1 * tanlat * math.tan(decl))
	sunset = -1 * sunrise
	hourangle = sunrise - (timev / 2)
	vpass = 1
	#print "vio: " + str(vio)
	#print "decl: " + str(decl)
	#print "sunrise: " + str(sunrise)
	#print "sunset: " + str(sunset)
	#print "hourangle: " + str(hourangle)
  
	while (hourangle >= sunset):
		solaralt = math.asin(sinlat * math.sin(decl) + coslat * math.cos(decl) * math.cos(hourangle))
		vtest = math.tan(decl)/tanlat
		if (math.cos(hourangle) > vtest):
			solaraz = math.asin(math.cos(decl) * math.sin(hourangle)/math.cos(solaralt))
		elif (math.cos(hourangle) < vtest):
			solaraz = math.pi - math.asin(math.cos(decl) * math.sin(hourangle)/math.cos(solaralt))
		elif (vtest == math.cos(hourangle) & hourangle >= 0):
			solaraz = math.pi/2
		elif (vtest == math.cos(hourangle) & hourangle < 0):
			solaraz = -1 * math.pi/ 2
		if (solaraz >= 0):
			solarazdeg = solaraz * 57.29578
		else:
			solarazdeg = 360 - (abs(solaraz) * 57.29578)
		# next line was modified to allow newer arcinfo
		#M = 1229 + (614 * sin(solaralt)**2)**0.5 - 614 * sin(solaralt)
		M = (math.sqrt(1229 + (614 * math.sin(solaralt))**2))-614 * math.sin(solaralt)
		# e = 2.7182818
		# tau = 0.56 * e ** (-0.65 * M) + e ** (-0.095 * M)
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
		cosi = math.sin(decl) * (sinlat * Cos(slopegrid2) - coslat * Sin(slopegrid2) * Cos(aspectgrid2)) + math.cos(decl) * math.cos(hourangle) * (coslat * Cos(slopegrid2) + sinlat * Sin(slopegrid2) * Cos(aspectgrid2)) + math.cos(decl) * Sin(slopegrid2) * Sin(aspectgrid2) * math.sin(hourangle)
		shaded = Con(cosi, 0, 1, "VALUE < 0")
		wattsgrid = vis * cosi * sungrid2 * shaded * 60 * interval
		initialgrid = wattsgrid + initialgrid
		hourangle = hourangle - timev
		# limit to one pass for test
		# hourangle = sunset - 1
		vpass = vpass + 1
	daynumber = daynumber + 1
initialgrid = Int(initialgrid)
initialgrid.save(outgrid)
		