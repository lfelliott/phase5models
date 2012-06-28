import os
import csv
from arcpy import management as DM
from time import time
from string import zfill
from datetime import date
# arcpy.env.workspace = "C:/WorkSpace/Phase5/Objects/p5_working.gdb"
# outf = open("c:/workspace/phase5/Objects/modellog.txt", "a")
# outf.writelines("\n" + str(date.today()) + " --Phase 5 --\n")


soils = "D:\\Projects\\Texas Ecological Systems\\Phase V\\GIS\\P5Soils.gdb\\p5soils_working"
soillayer = "l_p5soils_working"
DM.MakeFeatureLayer(soils, soillayer)

f = open('ecogrps.csv')
ecogrps = []
for item in f.readlines():
	ecogrps.append(item.strip())
f.close()
p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\north_test4"
layername = "l_p5_north_working"
cntchangedobjects = 0
DM.MakeFeatureLayer(p5_working, layername)
for ecogrp in ecogrps:
	selectstr = "\"EcoGroupFinal\" = '%s'" % ecogrp
	selectstr2 = "\"EcoGroup\" = '%s'" % ecogrp
	calcstr = "\"%s\"" % ecogrp
	print "Selecting soils where " + selectstr
	DM.SelectLayerByAttribute(soillayer, "NEW_SELECTION", selectstr)
	print str(int(str(DM.GetCount(soillayer)))) + " soil polygons selected."
	print "Selecting objects completely within selected soil polygons."
	DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", soillayer, "", "NEW_SELECTION")
	print str(int(str(DM.GetCount(layername)))) + " objects selected."
	if (int(str(DM.GetCount(layername))) > 0):
		print "Removing objects where " + selectstr2
		DM.SelectLayerByAttribute(layername, "REMOVE_FROM_SELECTION", selectstr2)
		countint = 0
		countint = int(str(DM.GetCount(layername)))
		print str(countint) + " objects remaining for calculation."
		if (countint > 0):
			cntchangedobjects = cntchangedobjects + countint
			DM.CalculateField(layername, "EcoGroup", calcstr, "VB")
		else:
			print "No objects to calculate."
	else:
		print "No objects to remove or calculate."
	print str(cntchangedobjects) + " objects changed.\n\a"