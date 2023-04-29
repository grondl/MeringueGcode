#!/usr/bin/env python3

import sys
import argparse
import math


# default values
sqvol = 2.2
totsqvol = 0
retract =1.8

xrows = 6
ycolumns = 7
xspacing = 35
xoffset = 20
yspacing = 36
yoffset = 3
mer_diameter =  3
mer_height = 10
swirls = 3
homing = False
eshape = 'kiss'
list_of_shapes = [ 'kiss', 'coin' , 'cone', 'pyramid' ]



def gcode_header():
  print("; Header start")
  print("M302 S0 ; Allow cold extrusion") # allow cold extrusion
  print("G92 E0 ; Zero the extrusion counter")  # ZERO extrusion counter
  print("M18 S3600 ; lock motors for one hour when idle")
  print("G0 Z50 ; Raise Z off its limit switch")
  print("; Header end")

def gcode_footer(homing=False):
  print("; Footer start" )
  print("G0 Z80")
  if homing:
      print("G0 X20 Y20 ; homing=yes ... extrusion head moved close to home ")
  else:
      print("; stay there , do not drip on way back or sweep accross top of kisses  .. removed G0 X20 Y20")
  print("; Footer end")

def gcode_coin( tsqvol , sqvol , xpos, ypos, mer_diameter):
  print("; Bud is coin shaped ")
  print( "G1 X{0} Y{1} F800".format( xpos ,ypos) )
  print( "G1 Z2 F600")
  # print("G92 E0")
  tsqvol+= sqvol
  merr  = mer_diameter / 2
  print( "G2 I{0} J{1} F100 E{2}".format( merr,merr, tsqvol))
  tsqvol +=1
  print( "G1 X{0} Y{1} Z{2} F100 E{3}".format(xpos+merr , ypos+merr , mer_diameter ,  tsqvol ))
  print( "G4 P5000")
  print("G1 Z50 F600")
  # print ... G1 E0 F600
  print("; Bud end")
  return( tsqvol );

def gcode_kiss( tsqvol , sqvol ,retract, xpos, ypos, mer_diameter):
  print("; Bud is kiss shaped")
  print( "G1 X{0} Y{1} F2800".format( xpos ,ypos) )
  print( "G1 Z0 F1500")
  # print("G92 E0")
  tsqvol+= sqvol
  merr  = mer_diameter / 2
  print( "G1 Z8 F80 E{0:.3f}".format( tsqvol))
  tsqvol +=.1
  print( "G1 X{0} Y{1} Z{2} F100 E{3:.3f}".format(xpos , ypos , mer_height ,  tsqvol ))
  print( "G1 X{0} Y{1} Z{2} F100 E{3:.3f}".format(xpos , ypos , mer_height+10 ,  tsqvol-retract ))
  print( "G4 P2000")
  print( "G1 Z40 F1200")
  # print ... G1 E0 F600
  print("; kiss shaped end")
  return( tsqvol );

def gcode_cone( tsqvol , sqvol , xpos, ypos, mer_diameter, mer_height, swirls):
  steps = 20
  print("; bud is Cone start")
  print( "G1 X{0} Y{1} F800".format( xpos ,ypos) )
  print( "G1 Z2 F600")
  zp = 2 ; xpo = xpos ; ypo = ypos ;   zpo = zp
  # print("G92 E0")
  merr  = mer_diameter / 2
  angmax = int(swirls * 360)
  angst = int( 360 / steps)
  tle = 0
  for ang in range(0, angmax  , angst):  # first pass to determine total swirl length
    rr =   merr * (angmax - ang) / angmax # radius diminishes as swirl is built
    xp =  xpos + (math.cos( math.radians(ang)) * rr)
    yp =  ypos + (math.sin( math.radians(ang)) * rr)
    zp +=  mer_height /( swirls + steps)
    le = math.sqrt( (xp-xpo) ** 2 + (yp - ypo) ** 2 + (zp - zpo ) ** 2 )
    xpo = xp
    ypo = yp
    zpo = zp
    tle += le
  print( "; total swirl squirt length : {0:.3f}mm,{1:.2f} *ml {2:.2f} *ml-tot    for a {3} swirl {4} mm diameter {5} mm high cone ".format(float(tle),float(sqvol), float(tsqvol), swirls, mer_diameter, mer_height) )
  zp = 2 ; xpo = xpos ; ypo = ypos ;   zpo = zp
  for ang in range(0, angmax  , angst):
    rr =   merr * (angmax - ang) / angmax
    xp =  xpos + (math.cos( math.radians(ang)) * rr)
    yp =  ypos + (math.sin( math.radians(ang)) * rr)
    zp +=  mer_height /( swirls + steps)
    le = math.sqrt( (xp-xpo) ** 2 + (yp - ypo) ** 2 + (zp - zpo ) ** 2 )
    xpo = xp
    ypo = yp
    zpo = zp
    tsqvol += sqvol * le / tle
    print( "G1 X{0:.2f} Y{1:.2f} Z{2:.2f} F100 E{3:.2f}".format( xp,yp,zp, tsqvol))

  print( "G1 Z{0:.3f} F100".format(zp + mer_height /2 ))
  print( "G4 P4000")
  print("G1 Z50 F600")
  # print ... G1 E0 F600
  print("; Cone end")
  return( tsqvol );




# Main program starts here


argParser = argparse.ArgumentParser()

argParser.add_argument("-f", "--ofile", help="output gcode file name ")
argParser.add_argument("-s", "--sqvol", type=float, help="syringe squirt volume in mm plunger travel")
argParser.add_argument("-r", "--retract", type=float, help="syringe retraction after squirt in mm plunger travel")
argParser.add_argument("-x", "--xrows", type=int, help="number of rows X")
argParser.add_argument("-y", "--ycolumns", type=int, help="number of columns Y")
argParser.add_argument("-a", "--xoffset", type=int, help="X offset in mm")
argParser.add_argument("-b", "--yoffset", type=int, help="Y offset ei mm")
argParser.add_argument("-i", "--xspacing", type=float, help="spacing between buds on X in mm")
argParser.add_argument("-j", "--yspacing", type=float, help="spacing between buds on Y in mm")
argParser.add_argument("-w", "--swirls", type=float, help="number of swirls when making a cone")
argParser.add_argument("-d", "--mer_diameter", type=float, help="meringue diameter in mm")
argParser.add_argument("-t", "--mer_height", type=float, help="meringue height in mm")
argParser.add_argument("-m", "--homing", help="home when finished (yes/no)")
argParser.add_argument("-p", "--shape", help="shape of extrusion (kiss/coin/cone)")

args = argParser.parse_args()
#print("args=%s" % args)
#print("args.ofile=%s" % args.ofile)

if args.ofile is not None:
    ofile = args.ofile
if args.sqvol is not None:
    sqvol = args.sqvol
if args.retract is not None:
    retract = args.retract
if args.xrows is not None:
    xrows = args.xrows
if args.ycolumns is not None:
    ycolumns = args.ycolumns
if args.xoffset is not None:
    xoffset = args.xoffset
if args.yoffset is not None:
    yoffset = args.yoffset
if args.xspacing is not None:
    xspacing = args.xspacing
if args.yspacing is not None:
    yspacing = args.yspacing
if args.swirls is not None:
    swirls = args.swirls
if args.mer_diameter is not None:
    mer_diameter = args.mer_diameter
if args.mer_height is not None:
    mer_height = args.mer_height
if args.homing is not None:
    if args.homing == 'yes':
        homing = True
    elif args.homing =='no':
        homing = False
    else:
        homing = False
if ( args.shape is not None) and (args.shape in list_of_shapes) :
    eshape = args.shape
else:
    eshape = 'kiss'




print('; Python program - Number of arguments:', len(sys.argv), 'arguments.')
print("; sqvol = {0:.2f}mm, retract = {1:.2f}mm, xrows = {2}, ycolumns = {3}, xspacing = {4}, xoffset = {5}, yspacing = {6}, yoffset = {7}, mer_diameter = {8}, mer_height = {9}, swirls = {10} homing = {11} ".format (
  sqvol, retract, xrows, ycolumns, xspacing, xoffset, yspacing, yoffset, mer_diameter, mer_height, swirls, homing  ))

print("; xrows = {0}, ycolumns = {1}, xspacing = {2}, yspacing = {3}, xoffset = {4},  yoffset = {5} ".format (xrows, ycolumns, xspacing,yspacing, xoffset,  yoffset  ))
print("; sqvol = {0:.2f}mm, retract = {1:.2f}mm, mer_diameter = {2}, mer_height = {3}, swirls = {4} homing = {5} ".format ( sqvol, retract,  mer_diameter, mer_height, swirls, homing  ))
print("; shape = {0} ".format(eshape))


gcode_header()

for j in range( ycolumns): # Y
  xr = range(xrows)
  if (j%2) == 1:
    xr = range(xrows-1,-1,-1)
  for i in xr: # X
    mx = xoffset + i * xspacing
    my = yoffset + j * yspacing


    if eshape == "kiss":
        totsqvol = gcode_kiss( totsqvol , sqvol , retract, mx , my , mer_diameter )
    elif eshape == "cone":
        totsqvol = gcode_cone(totsqvol, sqvol, mx, my, mer_diameter, mer_height, swirls)
    elif eshape == "coin":
        totsqvol = gcode_coin( totsqvol , sqvol , mx , my , mer_diameter )
    else:
        print("pas de forme choisie")


gcode_footer(homing)
