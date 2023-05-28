# MeringueGcode

meringues_gcode_generator_para.py   is a command line program that outputs G-Code to the standard output.  It accepts parameters in both formats (-p  and  --parameter= ).
The program produces G-Code that is meant to cold extrude meringues onto a sheet.  It will make X x Y  meringue buds  and the offset,spacing,  shape, height, diameter etc are passed as parameters.  I run it with Linux Mint and the 3D printer is marlin 1.0.2 based ... it is a work in progress but I actually use it.

meringue_gcode_GUI.py is a tkinter graphical interface that calls meringues_gcode_generator_para.py (which has to be in the same directory).  It can save the G-Code to a file in the local directory or the G-Code can be copied (for pasting) from the 'G-Code' tab.  Again,  work in progress here for example   dealing with files is not robust.

Having added the custom shape to the main program and since the sustom shape is stored in the GCode-array.pik (pickled) file. I've added the
meringue_draw_gcode_array.py program.  It helps in drawing a rudimentary shape and makes the corresponding '.pik' file.
