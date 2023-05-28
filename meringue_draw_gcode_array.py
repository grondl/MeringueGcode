#!/usr/bin/env python3
# Simple G-Code Drawing Application Using Python

#importing all the necessary Libraries
import pickle
from tkinter import *
from tkinter.ttk import Scale
from tkinter import colorchooser,filedialog,messagebox

#Defining Class and constructor of the Program
class GCDoodle():
    def __init__(self,root):

        #Defining title and Size of the Tkinter Window GUI
        self.root =root
        self.root.title("Doodle to G-Code and to Tabular data")
        self.root.geometry("900x600")
        self.root.configure(background="white")
        self.root.resizable(False, False)

        #variables for pointer and Eraser
        self.pointer= "black"
        self.erase="white"
        self.colors = ['black','blue','red','green', 'orange','violet']

        # variables for line drawing and storing G-Code
        self.xdraw, self.ydraw = 700, 500
        self.px = 0
        self.py  = 0
        self.pz = 0
        self.gcode = ""
        self.table = ""
        self.dataArray = []  # for saving the draw area coordinates
        self.GCodeArray = [] # for saving the scaled coordinates which can directly be converted to G-Code

        self.name_label = Label(self.root, text="misc info:  left-mouse=draw-line\nright-mouse=undo , center-mouse=show coords", bg="lightgrey", fg="black")
        self.name_label.place(x=4,y=535,width=320,height= 45)

        #Widgets for Tkinter Window
        # Pick a color/z height for drawing from color panel
        self.pick_color = LabelFrame(self.root,text='Colors',font =('arial',15),bd=3,relief=RIDGE,bg="white")
        self.pick_color.place(x=4,y=10,width=90,height=230)
        i=0
        for color in self.colors:
            Button(self.pick_color,text="z="+ str(i) , bg=color,bd=2,relief=RIDGE,width=3,command=lambda col=color:self.select_color(col)).grid(row=i)
            i+=1

        # Reset Button to clear the entire screen
        self.clear_screen= Button(self.root,text="Clear",bd=4,bg='orange',command=self.start_over ,width=9,relief=RIDGE)
        self.clear_screen.place(x=4,y=250)

        # Save Button for saving the image in local computer
        self.save_btn= Button(self.root,text="Save",bd=4,bg='springgreen',command=self.save_drawing,width=9,relief=RIDGE)
        self.save_btn.place(x=4,y=287)

        #Creating a Scale for line size with a label indicating the actual value
        self.pointer_frame= LabelFrame(self.root,text='line\nsize',bd=4,bg='white',font=('arial',10,'bold'),relief=RIDGE)
        self.pointer_frame.place(x=4,y=325,height=190,width=90)
        self.pointer_size_label = Label (self.pointer_frame,text="2", bg="lightgrey", fg="black")
        self.pointer_size =Scale(self.pointer_frame,orient=VERTICAL,from_ =40 , to =2, length=130, command = self.set_pointer_size_label)
        self.pointer_size.set(2)
        self.pointer_size.grid(row=0,column=1,padx=5)
        self.pointer_size_label.grid(row=0,column=2)

        #Creating a Scale for draw area scale ... size of the divisions with a label indicating the actual value
        self.scale_frame= LabelFrame(self.root,text='area\nscale',bd=4,bg='white',font=('arial',10,'bold'),relief=RIDGE)
        self.scale_frame.place(x=340,y=520,height=60,width=480)
        self.div_size_label = Label (self.scale_frame,text="div=10 mm", bg="lightgrey", fg="black")
        self.div_size_label.grid(row=0,column=2)
        self.div_size =Scale(self.scale_frame,orient=HORIZONTAL,from_ =5 , to =20, length=355, command = self.set_div_size_label)  #
        self.div_size.set(10)
        self.div_size.grid(row=0,column=1,padx=3)


        #Defining a drawArea color for the Canvas
        self.drawArea = Canvas(self.root,bg='white',bd=3,relief=GROOVE,height=self.ydraw,width=self.xdraw)
        self.drawArea.place(x=115,y=10)
        # drawing the gridl lines
        for i in range(1,10):
            self.drawArea.create_line(2,i*50,700,i*50,fill="DodgerBlue",width=1)
        for i in range(1,14):
            self.drawArea.create_line(i*50,2,i*50,500,fill="DodgerBlue",width=1)



        #Bind the drawArea Canvas with mouse click
        #self.drawArea.bind("<B1-Motion>",self.paint)
        self.drawArea.bind('<ButtonPress-1>', self.on_leftClick)
        self.drawArea.bind('<ButtonPress-3>', self.on_rightClick)
        self.drawArea.bind('<ButtonPress-2>', self.on_MiddleCLick)

        # read local datafile if present and show it in the draw area
        self.read_array()
        self.draw_blank_canvas_with_gridlines() # blanks the graphic canvas and draws the grid lines
        self.draw_lines() # draws saved lines on the graphic canvas  ... if there is any


# Functions are defined here

    # Function for Drawing the one line on draw Area
    def on_leftClick(self,event):
        w = round( self.pointer_size.get()*6/10 , 3 )
        x1,y1 = (event.x), (event.y)
        self.dataArray.append( [ x1 , y1 , self.pz , self.pointer_size.get(), self.pointer ] )
        if ( self.px != 0 )  and ( self.py != 0 ) :
            self.drawArea.create_line(x1,y1,self.px,self.py,fill=self.pointer,width=self.pointer_size.get())
            self.drawArea.create_oval(x1-w,y1-w, x1+w,y1+w,outline = "black", fill = "white",width = 2)
            self.drawArea.create_oval(self.px-w,self.py-w, self.px+w,self.py+w,outline = "black", fill = "white",width = 2)
            self.gcode = self.gcode + "G1 X" + "{:3.2f}".format(float(self.tox(x1))) + " Y "+ "{:3.2f}".format(float(self.toy(y1))) + "  Z " + "{:3.2f}".format(float( self.pz)) +  " F 900  \n"
            self.table = self.table + "[ " + "{:3.2f}".format(float(self.tox(x1))) + ", "+   "{:3.2f}".format(float(self.toy(y1))) +  " , " + "{:3.2f}".format(float( self.pz)) + " ,  0 ] , \n"
        else:
            self.gcode = self.gcode + "G0 X" + "{:3.2f}".format(float(self.tox(x1))) + " Y "+ "{:3.2f}".format(float(self.toy(y1))) + "  Z " + "{:3.2f}".format(float( self.pz)) +  " F 900  \n"
            self.table = self.table + "[ " + "{:3.2f}".format(float(self.tox(x1))) + ", "+   "{:3.2f}".format(float(self.toy(y1))) +  " , " + "{:3.2f}".format(float( self.pz)) + " ,  0 ] , \n"
        #self.drawArea.create_oval(x1,y1,x2,y2,fill=self.pointer,outline=self.pointer,width=self.pointer_size.get())
        self.px, self.py = (event.x), (event.y)

    # Function for removing the last line segment drawn
    def on_rightClick(self,event):
        if len( self.dataArray ) == 0 :
            self.px, self.py = 0, 0
        else :
            self.dataArray.pop()
            self.gcode = ""
            self.table = ""
            self.px , self.py =  0 , 0
            self.draw_blank_canvas_with_gridlines()
            self.draw_lines()

    # Function that draws/redraws the draw Area using the dataArray either after deleting a line or on reading the dataArray file during program startup
    def draw_lines(self):
        if len( self.dataArray ) == 0 :
            self.px, self.py = 0, 0
        else :
            self.px , self.py =  0 , 0
            for i in range (0,len(self.dataArray)):
                x1 , y1 , pz, wo , cc  = self.dataArray[i][0] , self.dataArray[i][1] , self.dataArray[i][2] , self.dataArray[i][3]*6/10 , self.dataArray[i][4]
                ww = round( wo * 6/10 , 3 )
                if ( i == 0  )  :
                    self.gcode = self.gcode + "G0 X" + "{:3.2f}".format(float(self.tox(x1))) + " Y "+ "{:3.2f}".format(float(self.toy(y1))) + "  Z " + "{:3.2f}".format(float( pz)) +  " F 900  \n"
                    self.table = self.table + "[ " + "{:3.2f}".format(float(self.tox(x1))) + ", "+   "{:3.2f}".format(float(self.toy(y1))) +  " , " + "{:3.2f}".format(float( pz)) + " ,  0 ] , \n"
                else:
                    px = self.dataArray[i-1][0]
                    py = self.dataArray[i-1][1]
                    self.drawArea.create_line(x1,y1,px,py,fill=cc,width=wo)
                    self.drawArea.create_oval(x1-ww,y1-ww, x1+ww,y1+ww,outline = "black", fill = "white",width = 2)
                    self.drawArea.create_oval(px-ww,py-ww, px+ww,py+ww,outline = "black", fill = "white",width = 2)
                    self.gcode = self.gcode + "G1 X" + "{:3.2f}".format(float(self.tox(x1))) + " Y "+ "{:3.2f}".format(float(self.toy(y1))) + "  Z " + "{:3.2f}".format(float( pz)) +  " F 900  \n"
                    self.table = self.table + "[ " + "{:3.2f}".format(float(self.tox(x1))) + ", "+   "{:3.2f}".format(float(self.toy(y1))) +  " , " + "{:3.2f}".format(float( pz)) + " ,  0 ] , \n"
                    self.px, self.py = x1, y1

    # Function for choosing the color of pointer
    def select_color(self,col):
        self.pointer = col
        self.pz = self.colors.index( self.pointer )



    # Function that erases everything and resets the data strings
    def start_over(self):
        self.gcode = ""
        self.table = ""
        self.px , self.py =  0 , 0
        self.dataArray = []
        self.draw_blank_canvas_with_gridlines()

    # Function that erases everything and resets the data strings
    def draw_blank_canvas_with_gridlines(self):
        self.drawArea.delete('all')
        for i in range(1,10):  # redraw grid lines
            self.drawArea.create_line(2,i*50,700,i*50,fill="DodgerBlue",width=1)
        for i in range(1,14):
            self.drawArea.create_line(i*50,2,i*50,500,fill="DodgerBlue",width=1)

    # Function for choosing the drawArea color of the Canvas
    def canvas_color(self):
        color=colorchooser.askcolor()
        self.drawArea.configure(background=color[1])
        self.erase= color[1]

    # Function for reading stored data if present
    def read_array(self):
        try:
            afn =  filedialog.askopenfilename(title='Open a file', filetypes=(('raw', '*.raw'),('All files', '*.*'))  )
            if (len(afn) != 0):
                with open(afn, "rb") as af:
                    self.dataArray = pickle.load(af)
        except Exception as e:
            print("Error in reading array data from arraydata.raw, >>" , e)
            self.dataArray = []

    # Function that fills GCodeArray with adjusted dataArray values
    def fill_GCodeArray(self):
        self.GCodeArray=[]
        if len( self.dataArray ) > 0 :
            for i in range (0,len(self.dataArray)):
                x1 , y1 , pz, wo , cc  = self.dataArray[i][0] , self.dataArray[i][1] , self.dataArray[i][2] , self.dataArray[i][3]*6/10 , self.dataArray[i][4]
                self.GCodeArray.append([ self.tox(x1), self.toy(y1) , pz , wo , cc ])

    # Function for saving the image and array to files in Local directory
    def save_drawing(self):
        try:
            f = open("Gcode_and_Array_data.txt", "w")
            f.write("; gcode   -----------------\n" + self.gcode + "\n\n\n")
            f.write( "table = [ " + self.table + " ] ")
            f.close()
            messagebox.showinfo('Data saved in files', 'Gcode_and_Array_data.txt\narraydata.raw\nGCode-array.pik')
            #for i in range(1,len(self.dataArray)):
            #   print(self.dataArray[i][0]," ", self.dataArray[i][1]," ",self.dataArray[i][2]," ",self.dataArray[i][3]," ",self.dataArray[i][4])
        except Exception as e:
            print("Error in saving to local text file, >>" , e)

        try:
            f = open("arraydata.raw", "wb")
            pickle.dump(self.dataArray,f)  #  save original coordinates without scaling
            f.close()
        except Exception as e:
            print("Error in saving array data to arraydata.raw, >>" , e)

        try:
            self.fill_GCodeArray()
            f = open("GCode-array.pik", "wb")  # save coordinates adjusted for scaling
            pickle.dump(self.GCodeArray,f)
            f.close()
        except Exception as e:
            print("Error in saving array data to arraydata.raw, >>" , e)
        #print( self.dataArray )

    # function converts area X coordinate (width) to cartesian coordinate
    def tox (self, px):
        x = round( px / self.xdraw * self.div_size.get() * 14 , 5)
        return x
    # function converts area Y coordinate (height) to cartesian coordinate
    def toy (self, py):
        y = round( ( self.ydraw - py )/self.ydraw  * self.div_size.get() * 10 , 5)
        return y

#
#
    # function writes x,y coordinates at bottom or root window
    def on_MiddleCLick(self, event):
        mouse_coordinates= "x=" + "{:3.2f}".format(self.tox(event.x)) + "   , y=" + "{:3.2f}".format(self.toy(event.y))
        self.name_label.configure(text = mouse_coordinates)
        #self.name_label.set( mouse_coordinates)

    def set_pointer_size_label(self,val):
        self.pointer_size_label.configure(text = "{:2.2f}".format(float(val)))

    def set_div_size_label(self,val):
        self.div_size_label.configure(text ="div="+ "{:2.2f}".format(float(val))+" mm")

if __name__ =="__main__":
    root = Tk()
    p= GCDoodle(root)
    root.mainloop()
