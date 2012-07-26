import arcpy
import os
import csv
from arcpy import management as DM
from time import time
from string import zfill
from datetime import date
arcpy.env.workspace = "C:/WorkSpace/Phase5/Objects/p5_working.gdb"
outf = open("c:/workspace/phase5/Objects/modellog.txt", "a")
outf.writelines("\n" + str(date.today()) + " -- Import Phase 5 from dbfs --\n")
dbfpath = "C:/Workspace/Phase5/Objects/"

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

def import_dbf(fcl, dbfname):
	processstart = time()
	layername = "l_" + fcl
	fc = fcl
	joindbf = dbfname
	joindbfname = dbfpath + joindbf + ".DBF"
#	print "layername: " + layername + "; featureclass : " + fc + "; DBF Path: " + joindbfname + "; DBF Name: " + joindbf + "\n"
	selectstr = "\"%s.VegNum\" <> \"%s.VEGNUM\" OR \"%s.VegNum\" IS NULL" % (fc, joindbf, fc)
	targetfield = "%s.VegNum" % fc
	sourcefield = "[%s.VEGNUM]" % joindbf
	print "\nMake feature layer:"
	DM.MakeFeatureLayer(fc, layername)
	print elapsed_time(processstart) + "\n\nAdd join: "
	DM.AddJoin(layername, "OBJECTID", joindbfname, "OBJECTID", "KEEP_COMMON")
	print elapsed_time(processstart) + "\n\nSelect by attribute with " + selectstr + ": "
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
	print elapsed_time(processstart) + "\n\nCalculate field for " + str(DM.GetCount(layername)) + " objects."
	if (int(str(DM.GetCount(layername))) > 0):
		DM.CalculateField(layername, targetfield, sourcefield, "VB", "")
	print elapsed_time(processstart) + "\n\nRemove join"
	DM.RemoveJoin(layername, joindbf)
	print "\nFinished moving vegnum to " + fc + " from " + joindbf + ".DBF in " + elapsed_time(processstart)

	
starttime = time()

basenames = ["north", "west", "south"]
# basenames = ["west", "south"]
# basenames = ["north"]
for basename in basenames:
	fcname = "p5_" + basename + "_working"
	dname = basename.upper() + "OUT"
	print "\n" + fcname + ", " + dname
	import_dbf(fcname, dname)


print "Finished - Elapsed Time = " + elapsed_time(starttime)
outf.writelines("\nFinished. " + elapsed_time(starttime) + "\n\n")
outf.close()




