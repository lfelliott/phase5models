from arcpy import management as DM

juniper_range = "D:\\GIS\\US\\Litlle\\junipers.shp"
juniperlayer = "l_juniper"
DM.MakeFeatureLayer(juniper_range, juniperlayer)
print "Making juniper layer."

selectstr = "(\"VegNum\" = 9101 or \"VegNum\" = 9105) and  \"epa_ecoreg\" like '25%'"
print selectstr

def applyjuniper(fc):
	p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\%s" % fc
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
	DM.SelectLayerByLocation(layername, "INTERSECT", juniperlayer, "", "REMOVE_FROM_SELECTION")	
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9204)
	else:
		print "nothing to calculate"
	print "selecting by location"

def fixsaltcedar(fc):
	# this is mostly on riparian or loamy, clay loam etc.
	selectstr2 = "(\"lulc\" = 11 or \"lulc\" = 19) and \"EcoGroup\" not like '%Bottomland%' and \"VegNum\" = 9204 and (\"epa_ecoreg\" like '30%' or \"epa_ecoreg\" like '26%' or \"epa_ecoreg\" = '24e')"
	p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\%s" % fc
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr2)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9105)
	else:
		print "nothing to calculate"	
	
applyjuniper("north_test5")


fcs = ["north_test5", "south_test5"]
for item in fcs:
	fixsaltcedar(item)