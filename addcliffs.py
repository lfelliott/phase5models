from arcpy import management as DM
gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_working_20120712.gdb\\"
selectbase = "\"slope100\" = 1 AND \"epa_ecoreg\" like "
vegtypes =[]
vegdict = {}

#define selectstrings for each cliff type
vegtypes.append(2100)
vegdict[2100] = selectbase + "'26%'"
vegtypes.append(3100)
vegdict[3100] = selectbase + "'25%' AND (\"lulc\" = 1 OR \"lulc\" = 15 OR \"lulc\" = 27)"
vegtypes.append(3104)
vegdict[3104] = selectbase + "'25%' AND (\"lulc\" = 3 OR \"lulc\" = 5 OR \"lulc\" = 7 OR \"lulc\" = 11 OR \"lulc\" = 19 OR \"lulc\" = 31)"
vegtypes.append(10100)
vegdict[10100] = selectbase + "'24%'"
vegtypes.append(807)
vegdict[807] = "\"slope100\" = 1 AND (\"epa_ecoreg\" like '30%' OR \"epa_ecoreg\" = '24e') AND (\"lulc\" = 1 OR \"lulc\" = 15 OR \"lulc\" = 27)"
vegtypes.append(806)
vegdict[806] = "\"slope100\" = 1 AND (\"epa_ecoreg\" like '30%' OR \"epa_ecoreg\" = '24e') AND (\"lulc\" = 3 OR \"lulc\" = 5 OR \"lulc\" = 7 OR \"lulc\" = 11 OR \"lulc\" = 19 OR \"lulc\" = 31)"

def addcliffs(fc):
	p5_working = "%s%s" % (gdbpath,fc)
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	for clifftype in vegtypes:
		print vegdict[clifftype]
		DM.SelectLayerByAttribute(layername, "NEW_SELECTION", vegdict[clifftype])
		if (int(str(DM.GetCount(layername))) > 0):
			print "adding cliff to " + str(DM.GetCount(layername)) + " objects"
			DM.CalculateField(layername, "VegNum", clifftype, "VB", "")

fcs = ["south_test5", "west_test5", "north_test5"]
for item in fcs:
	addcliffs(item)	