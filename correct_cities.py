from arcpy import management as DM

cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
DM.MakeFeatureLayer(cities, citylayer)
print "Making city layer."

p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\north_test6"
layername = "l_p5_north_test6"
DM.MakeFeatureLayer(p5_working, layername)
print "Making working layer"

selectstr = "\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 31 or \"lulc\" =27"
print selectstr
print "selecting by location"
DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", citylayer, "", "NEW_SELECTION")
print "selecting by attribute"
DM.SelectLayerByAttribute(layername, "SUBSET_SELECTION", selectstr)
if (int(str(DM.GetCount(layername))) > 0):
	print "calculating"
	DM.CalculateField(layername, "lulc", 25)
else:
	print "nothing to calculate"
