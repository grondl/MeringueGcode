#!/usr/bin/env python3

import argparse
import math
import pickle


# default values
sqvol = 2.2
totsqvol = 0.0
retract =1.8

xrows = 6
ycolumns = 7
xspacing = 35
xoffset = 20
yspacing = 36
yoffset = 3
zsquirt = 0.0
ztravel = 30.0
mer_diameter =  3
mer_height = 10
swirls = 3
homing = False
eshape = 'kiss'
list_of_shapes = [ 'kiss', 'coin' , 'cone','leaf' ,'custom', 'cycle', 'nothing' ]
pfile = 'none'



def gcode_header():
    print("; Header start")
    print("G21 ; metric (mm) ")
    print("M302 S0 ; Allow cold extrusion") # allow cold extrusion
    print("G92 E0 ; Zero the extrusion counter")  # ZERO extrusion counter
    print("M18 S3600 ; keep motors locked for one hour when idle")
    print("G0 Z50 ; Raise Z off its limit switch")
    print("; Header end")

def gcode_footer(homing=False):
    print("; Footer start" )
    print("G0 Z{0:.3f}".format(ztravel))
    if homing:
        print("G0 X20 Y20 ; homing=yes ... extrusion head moved close to home ")
    else:
        print("; stay there , do not drip on way back or sweep accross top of kisses  .. removed G0 X20 Y20")
    print("; Footer end")

def gcode_coin( tsqvol , sqvol , xpos, ypos, zsquirt, ztravel , mer_diameter, mer_height, retract):
    # extrudes a circle then a climbing diagonal to the center  with a height of the actual merengue
    print("; Extrusion is Coin shaped ")
    print( "G1 X{0} Y{1} F1600".format( xpos ,ypos) )
    print( "G1 Z{0:.3f} F1500".format(zsquirt))
    print( "G1 F200 E{0:.4f}".format(tsqvol)) # return E to end of previous extrusion ... before previous retraction
    print( "G4 P1000")
    # print("G92 E0")
    merr  = mer_diameter / 2
    circum_l = 3.1416 * mer_diameter
    diag_l = math.sqrt(merr**2 + mer_height**2)
    tsqvol+= sqvol* circum_l/(circum_l + diag_l)
    print( "G2 I{0} J{1} F800 E{2:.4f}".format( merr,merr, tsqvol))
    tsqvol += sqvol* diag_l/(circum_l + diag_l)
    print( "G1 X{0} Y{1} Z{2} F1500 E{3:.4f}".format(xpos+merr , ypos+merr , mer_height ,  tsqvol ))
    print( "G4 P2000")
    print("G1 Z{0} F600".format(mer_height+5))
    print( "G1 F200 E{0:.4f}".format(tsqvol-retract ))
    print( "G4 P2000")
    print("G1 Z{0:.3f} F600".format(ztravel))
    # print ... G1 E0 F600
    print("; Bud end")
    return( tsqvol );

def gcode_kiss( tsqvol , sqvol ,retract, xpos, ypos, zsquirt, ztravel , mer_diameter):
    # squirt half on target base then other half climbing to meringue height
    print("; Extrusion is Kiss shaped")
    print( "G1 X{0} Y{1} F2800".format( xpos ,ypos) )
    print( "G1 Z{0:.3f} F1000".format(zsquirt))
    print( "G1 F200 E{0:.4f}".format(tsqvol)) # return E to end of previous extrusion ... before previous retraction
    # print("G92 E0")
    print( "G4 P2000")
    tsqvol+= sqvol/2
    print( "G1 Z{0:.3f} F200 E{1:.3f}".format( zsquirt,tsqvol))
    tsqvol += sqvol/2
    print( "G1 X{0} Y{1} Z{2} F200 E{3:.3f}".format(xpos , ypos , mer_height ,  tsqvol ))
    print( "G1 X{0} Y{1} Z{2} F200 E{3:.3f}".format(xpos , ypos , mer_height+10 ,  tsqvol-retract ))
    print( "G4 P1000")
    print("G1 Z{0:.3f} F1000".format(ztravel))
    # print ... G1 E0 F600
    print("; kiss shaped end")
    return( tsqvol );

def gcode_cone( tsqvol , sqvol , xpos, ypos, zsquirt, ztravel ,mer_diameter, mer_height, swirls, retr):
    steps = 60
    print("; Extrusion is Cone start")
    print( "G1 X{0} Y{1} F1200".format( xpos ,ypos) )
    print( "G1 Z{0:.3f} F1200".format(zsquirt))
    zp = zsquirt ; xpo = xpos ; ypo = ypos ;   zpo = zp
    # print("G92 E0")
    merr  = mer_diameter / 2
    angmax = int(swirls * 360)
    angst = int( 360 / steps)
    tle = 0
    for ang in range(0, angmax  , angst):  # first pass to determine total swirl length
       if ang < 360 :  
          rr =   merr  # first turn radius does not diminishes as swirl is built
       else:
          rr =   merr * (angmax - ang) / angmax # radius diminishes as swirl is built
          zp +=  mer_height /( (swirls-1) * steps)
       xp =  xpos + (math.cos( math.radians(ang)) * rr)
       yp =  ypos + (math.sin( math.radians(ang)) * rr)
       le = math.sqrt( (xp-xpo) ** 2 + (yp - ypo) ** 2 + (zp - zpo ) ** 2 )
       xpo = xp
       ypo = yp
       zpo = zp
       tle += le
    print( "; total swirl squirt length : {0:.3f}mm,{1:.2f} *ml {2:.2f} *ml-tot    for a {3} swirl {4} mm diameter {5} mm high cone ".format(float(tle),float(sqvol), float(tsqvol), swirls, mer_diameter, mer_height) )
    zp = zsquirt ; xpo = xpos ; ypo = ypos ;   zpo = zp
    for ang in range(0, angmax  , angst):
        if ang < 360 :  
            rr =   merr  # first turn radius does not diminishes as swirl is built
        else:
            rr =   merr * (angmax - ang) / angmax # radius diminishes as swirl is built
            zp +=  mer_height /( (swirls-1) * steps)
        xp =  xpos + (math.cos( math.radians(ang)) * rr)
        yp =  ypos + (math.sin( math.radians(ang)) * rr)
        le = math.sqrt( (xp-xpo) ** 2 + (yp - ypo) ** 2 + (zp - zpo ) ** 2 )
        xpo = xp
        ypo = yp
        zpo = zp
        tsqvol += sqvol * le / tle
        print( "G1 X{0:.2f} Y{1:.2f} Z{2:.2f} F1600 E{3:.2f}".format( xp,yp,zp, tsqvol))
    if mer_height < 4:
       finishh = zp + 4
    else:
       finishh = zp + mer_height /2
    print( "G1 Z{0:.3f} E{1:.3f} F900".format(finishh, tsqvol - retr ))
    print( "G4 P1500")
    print("G1 Z{0:.3f} F750".format(ztravel))
    # print ... G1 E0 F600
    print("; Cone end")
    return( tsqvol );


def gcode_leaf( tsqvol , sqvol , xpos, ypos, zsquirt, ztravel ,mer_diameter, mer_height, swirls, retr):
    l = [ [ 10.00, 0.20 , 0.00 ,  0 ] ,[ 10.50, 2.70 , 0.00 ,  0 ] ,[ 11.60, 6.10 , 0.00 ,  0 ] ,
          [ 11.10, 8.30 , 0.00 ,  0 ] ,[ 10.40, 9.90 , 0.00 ,  0 ] ,[ 9.70, 9.60 , 0.00 ,  0 ] ,
          [ 7.70, 8.40 , 0.00 ,  0 ] ,[ 6.20, 9.00 , 0.00 ,  0 ] ,[ 3.70, 11.30 , 0.00 ,  0 ] ,
          [ 3.00, 14.60 , 0.00 ,  0 ] ,[ 3.90, 17.60 , 0.00 ,  0 ] ,[ 4.80, 19.30 , 0.00 ,  0 ] ,
          [ 7.00, 21.10 , 0.00 ,  0 ] ,[ 7.30, 21.10 , 0.00 ,  0 ] ,[ 7.60, 20.30 , 0.00 ,  0 ] ,
          [ 8.10, 19.60 , 0.00 ,  0 ] ,[ 9.70, 18.80 , 0.00 ,  0 ] ,[ 12.60, 18.10 , 0.00 ,  0 ] ,
          [ 13.70, 16.40 , 0.00 ,  0 ] ,[ 14.20, 14.50 , 0.00 ,  0 ] ,[ 14.40, 12.40 , 0.00 ,  0 ] ,
          [ 13.20, 10.50 , 0.00 ,  0 ] ,[ 12.00, 9.90 , 0.00 ,  0 ] ,[ 10.60, 9.70 , 0.00 ,  0 ] ,
          [ 10.30, 10.60 , 0.00 ,  0 ] ,[ 9.00, 12.10 , 0.00 ,  0 ] ,[ 8.10, 13.30 , 0.00 ,  0 ] ,
          [ 7.00, 15.20 , 0.00 ,  0 ] ,[ 6.50, 17.70 , 0.00 ,  0 ] ,[ 8.20, 14.60 , 4.00 ,  0 ] ,
          [ 9.70, 13.20 , 4.00 ,  0 ] ,[ 9.80, 11.40 , 4.00 ,  0 ] ,[ 11.60, 6.70 , 4.00 ,  0 ] ,
          [ 11.10, 4.20 , 4.00 ,  0 ] , ]
    #m = mer_diameter / 10
    m = 1
    print("; Extrusion is Leaf Shaped ...  start")
    print( "G1 X{0} Y{1} F1000".format( xpos ,ypos) )
    print( "G1 Z{0:.3f} F1000".format(zsquirt))
    print( "G1 X{0:.4f} Y{1:.4f} Z{2:.4f} F900".format( xpos+l[0][0]*m ,ypos +l[0][1]*m, zsquirt+l[0][2]  ))
    le = 0.001
    for i in range(1,len(l)):
        le = math.sqrt( (l[i-1][0]-l[i][0]) ** 2 + (l[i-1][1] - l[i][1]) ** 2 + (l[i-1][2] - l[i][2] ) ** 2 ) * m
        #print(";le  sqvol, tsqvol + ",  le, sqvol, tsqvol)
        tsqvol += sqvol * le / 250
        #print( xpos+l[i][0] ,ypos +l[i][1], zsquirt+l[i][2], tsqvol )
        print( "G1 X{0:.4f} Y{1:.4f} Z{2:.4f} E{3:.4f} F900".format( xpos+l[i][0]*m ,ypos +l[i][1]*m, zsquirt+l[i][2]*m , tsqvol ))
        print( "G4 P{0}".format( 500 ))
    print( "G1 Z{0:.3f} F900".format(ztravel))
    print( "G1 E{0:.4f} F200".format( tsqvol - retr))
    return( tsqvol );



def gcode_custom( tsqvol , sqvol , xpos, ypos, zsquirt, ztravel ,mer_diameter, mer_height, swirls, retr, pfile):
    l = []
    try:
        afn =  "GCode-array.pik"
        with open(afn, "rb") as af:
            l = pickle.load(af)
    except Exception as e:
        print("Error in reading array data from "+ afn , e)
        l = []

    #print(l)
    #m = mer_diameter / 10
    m = 1
    print("; Extrusion is Custom shaped ...  start")
    print( "G1 X{0} Y{1} F1000".format( xpos ,ypos) )
    print( "G1 Z{0:.3f} F1000".format(zsquirt))
    print( "G1 X{0:.4f} Y{1:.4f} Z{2:.4f} F900".format( xpos+l[0][0]*m ,ypos +l[0][1]*m, zsquirt+l[0][2]  ))
    le = 0.001
    for i in range(1,len(l)):
        le = math.sqrt( (l[i-1][0]-l[i][0]) ** 2 + (l[i-1][1] - l[i][1]) ** 2 + (l[i-1][2] - l[i][2] ) ** 2 ) * m
        #print(";le  sqvol, tsqvol + ",  le, sqvol, tsqvol)
        tsqvol += sqvol * le / 250
        #print( xpos+l[i][0] ,ypos +l[i][1], zsquirt+l[i][2], tsqvol )
        print( "G1 X{0:.4f} Y{1:.4f} Z{2:.4f} E{3:.4f} F900".format( xpos+l[i][0]*m ,ypos +l[i][1]*m, zsquirt+l[i][2]*m , tsqvol ))
        print( "G4 P{0}".format( 500 ))
    print( "G1 Z{0:.3f} F900".format(ztravel))
    print( "G1 E{0:.4f} F200".format( tsqvol - retr))
    return( tsqvol );







# Main program starts here


argParser = argparse.ArgumentParser()

argParser.add_argument("-f", "--pfile", help="pickled gcode array file name ")
argParser.add_argument("-s", "--sqvol", type=float, help="syringe squirt volume in mm plunger travel")
argParser.add_argument("-r", "--retract", type=float, help="syringe retraction after squirt in mm plunger travel")
argParser.add_argument("-x", "--xrows", type=int, help="number of rows X")
argParser.add_argument("-y", "--ycolumns", type=int, help="number of columns Y")
argParser.add_argument("-z", "--zsquirt", type=float, help="Z height when squirting material")
argParser.add_argument("-a", "--xoffset", type=int, help="X offset in mm")
argParser.add_argument("-b", "--yoffset", type=int, help="Y offset ei mm")
argParser.add_argument("-i", "--xspacing", type=float, help="spacing between buds on X in mm")
argParser.add_argument("-j", "--yspacing", type=float, help="spacing between buds on Y in mm")
argParser.add_argument("-k", "--ztravel", type=float, help="Z height when travelling between buds")
argParser.add_argument("-w", "--swirls", type=float, help="number of swirls when making a cone")
argParser.add_argument("-d", "--mer_diameter", type=float, help="meringue diameter in mm")
argParser.add_argument("-t", "--mer_height", type=float, help="meringue height in mm")
argParser.add_argument("-m", "--homing", help="home when finished (yes/no)")
argParser.add_argument("-p", "--shape", help="shape of extrusion (kiss/coin/cone/leaf/custom)")

args = argParser.parse_args()
print("; args=%s" % args)


if args.pfile is not None:
    pfile = args.pfile
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
if args.zsquirt is not None:
    zsquirt = args.zsquirt
if args.ztravel is not None:
    ztravel = args.ztravel
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




#print('; Python program - Number of arguments:', len(sys.argv), 'arguments.')
print("; xrows = {0}, ycolumns = {1}, xspacing = {2}, yspacing = {3}, xoffset = {4},  yoffset = {5} ".format (xrows, ycolumns, xspacing,yspacing, xoffset,  yoffset  ))
print("; zsquirt = {0:.2f}mm, ztravel = {1:.2f}mm ".format (zsquirt, ztravel ))
print("; sqvol = {0:.2f}mm, retract = {1:.2f}mm, mer_diameter = {2:.2f}, mer_height = {3:2f}, swirls = {4:.2f} homing = {5} ".format ( sqvol, retract,  mer_diameter, mer_height, swirls, homing  ))
print("; shape = {0} ".format(eshape))


gcode_header()

totsqvol = 0.0
cshape = eshape
for j in range( ycolumns): # Y
  xr = range(xrows)
  if (j%2) == 1:
    xr = range(xrows-1,-1,-1)
  for i in xr: # X
    mx = xoffset + i * xspacing
    my = yoffset + j * yspacing
    if cshape == 'cycle':
        eshape = list_of_shapes[j%(len(list_of_shapes)-2)]

    if eshape == "kiss":
        totsqvol = gcode_kiss( totsqvol , sqvol , retract, mx , my , zsquirt, ztravel , mer_diameter )
    elif eshape == "cone":
        totsqvol = gcode_cone(totsqvol, sqvol, mx, my, zsquirt, ztravel , mer_diameter, mer_height, swirls, retract)
    elif eshape == "coin":
        totsqvol = gcode_coin( totsqvol , sqvol , mx , my, zsquirt , ztravel , mer_diameter, mer_height, retract )
    elif eshape == "leaf":
        totsqvol = gcode_leaf(totsqvol, sqvol, mx, my, zsquirt, ztravel , mer_diameter, mer_height, swirls, retract)
    elif eshape == "custom":
        totsqvol = gcode_custom(totsqvol, sqvol, mx, my, zsquirt, ztravel , mer_diameter, mer_height, swirls, retract, pfile)
    else:
        print(";No shape chosen !")


gcode_footer(homing)
