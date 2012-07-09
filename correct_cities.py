from arcpy import management as DM

cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
DM.MakeFeatureLayer(cities, citylayer)
print "Making city layer."

selectstr = "\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 11 or \"lulc\" = 31 or \"lulc\" =27"
print selectstr

def applycities(fc):
	p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\%s" % fc
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

fcs = ["west_test5", "south_test5", "north_test5"]
for item in fcs:
	applycities(item)