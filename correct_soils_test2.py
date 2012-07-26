import csv
from arcpy import management as DM


soils = "D:\\Projects\\Texas Ecological Systems\\Phase V\\GIS\\P5Soils.gdb\\p5soils_working"
soillayer = "l_p5soils_working"
DM.MakeFeatureLayer(soils, soillayer)

f = open('ecogrps.csv')
ecogrps = []

for item in f.readlines():
	ecogrps.append(item.strip())
f.close()
p5path = "C:\\WorkSpace\\Phase5\\Objects\\p5_checksoils_20120725.gdb\\"
def checksoils(fc):
	p5_working = "%s%s" % (p5path, fc)
	# p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\north_test4"
	layername = "l_%s" % fc
	#layername = "l_p5_north_working"
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
				DM.CalculateField(layername, "EcoGroup2", calcstr, "VB")
			else:
				print "No objects to calculate."
		else:
			print "No objects to remove or calculate."
		print str(cntchangedobjects) + " objects changed.\n\a"

fcs = ["south_checksoils", "west_checksoils", "north_checksoils"]
for fc in fcs:
	checksoils(fc)