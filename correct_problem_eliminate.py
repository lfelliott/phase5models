from arcpy import management as DM
from arcpy import analysis as AN
from time import time
from string import zfill
from datetime import date

gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_working_20120712.gdb\\"
elim_objs = "%stemp_elim" % gdbpath

eliminated_result = "%stemp_eliminated" % gdbpath

intrsct_result = "%stemp_intrsct" % gdbpath
intrsct_lyr = "l_temp_intrsct"

elim_subset = "%stemp_elim_subset" % gdbpath
elim_subsetlyr = "l_temp_elim_subset"

starttime = time()

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)
	
def applyelimupdate(fc):
	elim_count = 1
	while (elim_count > 0):
		calcfield = "%s.VegNum" % fc
		selectstr = "\"%s.Vegnum\" = 99998" % fc
		p5_working = "%s%s" % (gdbpath, fc)
		layername = "l_p5_%s" % fc
		print "Making working layer for " + fc
		DM.MakeFeatureLayer(p5_working, layername)
		print "selecting for vegnum = 99998"
		DM.SelectLayerByAttribute(layername, "NEW_SELECTION", '"VegNum" = 99998')
		elim_count = int(str(DM.GetCount(layername)))
		if (elim_count == 0):
			print "no remaining problem eliminate polygons in " + fc
			return
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
		DM.AddJoin(layername, "morap_objid", intrsct_lyr, "morap_objid_1", "KEEP_ALL")
		DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
		if (int(str(DM.GetCount(layername))) > 0):
			print "calculate vegnum to vegnum for " + str(DM.GetCount(layername)) + " objects"
			DM.CalculateField(layername, calcfield, "[temp_intrsct.VegNum]", "VB", "")
		print "deleting temp layers"
		DM.Delete(elim_subsetlyr)
		DM.Delete(intrsct_lyr)
		DM.Delete(elim_objs)
		DM.Delete(eliminated_result)
		DM.Delete(intrsct_result)
		DM.Delete(elim_subset)
	
fcs = ["south_working", "west_working", "north_working"]
fcs = ["west_working", "north_working"]
for item in fcs:
	processstart = time()
	applyelimupdate(item)
	print "process time = " + elapsed_time(processstart) + " for " + item + "."
