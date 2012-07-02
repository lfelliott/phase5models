from arcpy import management as DM
from arcpy import analysis as AN

elim_objs = "c:\\Workspace\\Phase5\\Objects\\p5_working_test.gdb\\temp_elim"
elim_lyr = "l_temp_elim"

eliminated_result = "c:\\Workspace\\Phase5\\Objects\\p5_working_test.gdb\\temp_eliminated"

intrsct_result = "c:\\Workspace\\Phase5\Objects\\p5_working_test.gdb\\temp_intrsct"
intrsct_lyr = "l_temp_intrsct"

elim_subset = "c:\\Workspace\\Phase5\\Objects\\p5_working_test.gdb\\temp_elim_subset"
elim_subsetlyr = "l_temp_elim_subset"

def applyelimupdate(fc):
	calcfield = "%s.VegNum" % fc
	selectstr = "\"%s.Vegnum\" = 99998" % fc
	p5_working = "C:\\WorkSpace\\Phase5\\Objects\\p5_working_test.gdb\\%s" % fc
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting for vegnum = 99998"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", '"VegNum" = 99998')
	print "copying selected objects to temp"
	DM.CopyFeatures(layername, elim_objs)
	print "select touching polys in larger layer to limit eliminate and select those with VegNum = 99998"
	DM.SelectLayerByLocation(layername, "INTERSECT", elim_objs)
	DM.CopyFeatures(layername, elim_subset)
	DM.MakeFeatureLayer(elim_subset, elim_subsetlyr)
	DM.SelectLayerByAttribute(elim_subsetlyr, "NEW_SELECTION", '"VegNum" = 99998')
	print "eliminating selected features"
	DM.Eliminate(elim_subsetlyr, eliminated_result, "LENGTH")
	print "intersect eliminated by elim objects"
	AN.Intersect([eliminated_result, elim_objs], intrsct_result)
	print "make feature layer for joining and join on morap_objid_1"
	DM.MakeFeatureLayer(intrsct_result, intrsct_lyr)
	DM.AddJoin(layername, "OBJECTID", intrsct_lyr, "morap_objid_1", "KEEP_ALL")
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculate vegnum to vegnum for " + str(DM.GetCount(layername)) + " objects"
		DM.CalculateField(layername, calcfield, "[temp_intrsct.VegNum]", "VB", "")
	print "deleting temp layers"
	DM.Delete(elim_lyr)	
	DM.Delete(elim_objs)
	DM.Delete(eliminated_result)
	DM.Delete(intrsct_lyr)
	DM.Delete(intrsct_result)
	DM.Delete(elim_subsetlyr)
	DM.Delete(elim_subset)
	
#fcs = ["south_test5", "west_test5", "north_test5"]
fcs = ["west_test5", "north_test5"]
for item in fcs:
	applyelimupdate(item)
