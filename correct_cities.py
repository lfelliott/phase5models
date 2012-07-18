from arcpy import management as DM
gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_working_20120712.gdb\\"
cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
DM.MakeFeatureLayer(cities, citylayer)
print "Making city layer."

selectstr = "\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 11 or \"lulc\" = 31 or \"lulc\" =27"
print selectstr

def applycities(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by location"
	DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", citylayer, "", "NEW_SELECTION")
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "SUBSET_SELECTION", selectstr)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
#		DM.CalculateField(layername, "lulc", 25)
		DM.CalculateField(layername, "VegNum", 9411)
	else:
		print "nothing to calculate"
		
def applyroads(fc):
	roadselect = "\"road\" = 1 and not (\"VegNum\" = 9410 or \"VegNum\" = 9411)"
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lr_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", roadselect)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9411)
	else:
		print "nothing to calculate"

fcs = ["west_test5", "south_test5", "north_test5"]
for item in fcs:
	applycities(item)
	applyroads(item)