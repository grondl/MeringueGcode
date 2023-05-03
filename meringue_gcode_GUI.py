#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox as msg
from tkinter.ttk import Notebook, Combobox
from tkinter import filedialog as fidi
import re   # Regular Expressions
import os
import subprocess

import requests

class MeringueTool(tk.Tk):
    def __init__(self):
        super().__init__()

        self.nparas = [ "nX","nY","oX","oY","sX","sY","sZ", "tZ", "sV", "re","mH","mD","nS" ]
        self.tparas = [ "ho","sh" ]

        self.title("Meringue G-Code generator v1")
        self.geometry("880x650")

        self.notebook = Notebook(self)

        root_tab = tk.Frame(self.notebook)
        gcode_tab = tk.Frame(self.notebook)
        help_tab = tk.Frame(self.notebook)

        # root tab/page setup
        self.notebook.add(root_tab, text="Parameters/execution")



        self.label_noX = tk.Label(root_tab, text = "number of buds across (X)  : ", fg = 'black', bg = 'snow')
        self.label_noY = tk.Label(root_tab, text = "number of buds along  (Y)  : ", fg = 'black', bg = 'snow')
        self.label_ofX = tk.Label(root_tab, text = "X offset  : ", fg = 'black', bg = 'snow')
        self.label_ofY = tk.Label(root_tab, text = "Y offset  : ", fg = 'black', bg = 'snow')
        self.label_spX = tk.Label(root_tab, text = "X spacing  : ", fg = 'black', bg = 'snow')
        self.label_spY = tk.Label(root_tab, text = "Y spacing  : ", fg = 'black', bg = 'snow')

        self.label_sqZ = tk.Label(root_tab, text = "Z squirt height  : ", fg = 'black', bg = 'snow')
        self.label_trZ = tk.Label(root_tab, text = "Z travel height  : ", fg = 'black', bg = 'snow')

        self.label_tot = tk.Label(root_tab, text = "total number of buds  : ",  fg = 'black', bg = 'azure')
        self.label_fiN = tk.Label(root_tab, text = "filename : ",  fg = 'black', bg = 'azure')
        self.label_sqV = tk.Label(root_tab, text = "plunger travel (mm) => Squirt volume)  : ", fg = 'black', bg = 'snow')
        self.label_ret = tk.Label(root_tab, text = "retraction (mm)  : ", fg = 'black', bg = 'snow')
        self.label_meH = tk.Label(root_tab, text = "meringe height (mm)  : ", fg = 'black', bg = 'snow')
        self.label_meD = tk.Label(root_tab, text = "meringue diameter (mm)  : ", fg = 'black', bg = 'snow')
        self.label_noS = tk.Label(root_tab, text = "number of swirls  : ", fg = 'black', bg = 'snow')
        self.label_hom = tk.Label(root_tab, text = "homing after (yes/no)  : ", fg = 'black', bg = 'snow')
        self.label_sha = tk.Label(root_tab, text = "shape (bud/kiss/cone)  : ", fg = 'black', bg = 'snow')

        self.label_noX.grid(row =  1, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_noY.grid(row =  2, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_ofX.grid(row =  3, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_ofY.grid(row =  4, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_spX.grid(row =  5, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_spY.grid(row =  6, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_tot.grid(row =  7, column = 0, padx = 5, pady = 5 , sticky='e')
        self.label_fiN.grid(row =  8, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_sqV.grid(row =  9, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_ret.grid(row = 10, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_meH.grid(row = 11, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_meD.grid(row = 12, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_noS.grid(row = 13, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_hom.grid(row = 14, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_sha.grid(row = 15, column = 0, padx = 5, pady = 5,  sticky='e')
        self.label_sqZ.grid(row =  5, column = 2, padx = 5, pady = 5,  sticky='e')
        self.label_trZ.grid(row =  6, column = 2, padx = 5, pady = 5,  sticky='e')


        self.nX = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateInt  ), '%P'), width=5)
        self.nY = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateInt  ), '%P'), width=5)
        self.oX = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateInt), '%P'), width=8)
        self.oY = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateInt), '%P'), width=8)
        self.sX = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)
        self.sY = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)
        self.to = tk.Entry(root_tab, width=6)
        self.fN = tk.Entry(root_tab, width=40)
        self.sV = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)
        self.re = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)
        self.mH = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=6)
        self.mD = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=6)
        self.nS = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=5)
        #self.ho = tk.Entry(root_tab, width=10)
        self.ho = Combobox(root_tab, width="10", values=("yes","no"))
        #self.sh = tk.Entry(root_tab, width=10)
        self.sh = Combobox(root_tab, width="10", values=("kiss","coin","cone","nothing"))
        self.of = tk.Entry(root_tab, width=60)

        self.sZ = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)
        self.tZ = tk.Entry(root_tab,validate="key", validatecommand=(self.register(self.onValidateFloat), '%P'), width=8)


        self.nX.grid(row =  1, column = 1, padx = 5, pady = 5, sticky='w')
        self.nY.grid(row =  2, column = 1, padx = 5, pady = 5, sticky='w')
        self.oX.grid(row =  3, column = 1, padx = 5, pady = 5, sticky='w')
        self.oY.grid(row =  4, column = 1, padx = 5, pady = 5, sticky='w')
        self.sX.grid(row =  5, column = 1, padx = 5, pady = 5, sticky='w')
        self.sY.grid(row =  6, column = 1, padx = 5, pady = 5, sticky='w')
        self.to.grid(row =  7, column = 1, padx = 5, pady = 5, sticky='w')
        self.fN.grid(row =  8, column = 1, padx = 5, pady = 5, sticky='w', columnspan = 2)
        self.sV.grid(row =  9, column = 1, padx = 5, pady = 5, sticky='w')
        self.re.grid(row = 10, column = 1, padx = 5, pady = 5, sticky='w')
        self.mH.grid(row = 11, column = 1, padx = 5, pady = 5, sticky='w')
        self.mD.grid(row = 12, column = 1, padx = 5, pady = 5, sticky='w')
        self.nS.grid(row = 13, column = 1, padx = 5, pady = 5, sticky='w')
        self.ho.grid(row = 14, column = 1, padx = 5, pady = 5, sticky='w')
        self.sh.grid(row = 15, column = 1, padx = 5, pady = 5, sticky='w')
        self.of.grid(row = 16, column = 1, padx = 5, pady = 5, sticky='w', columnspan = 3)

        self.sZ.grid(row =  5, column = 3, padx = 5, pady = 5, sticky='w')
        self.tZ.grid(row =  6, column = 3, padx = 5, pady = 5, sticky='w')


        # Create  open and save file, submit and reset buttons - and attache them
        self.button_open =   tk.Button(root_tab, text = "open", bg = "green2", fg = "black", command = self.file_open)
        self.button_save =   tk.Button(root_tab, text = "save", bg = "orange", fg = "black", command = self.file_save)
        self.button_submit = tk.Button(root_tab, text = "Calculate Total",   bg = "green2", fg = "black", command = self.calculate)
        self.button_reset =  tk.Button(root_tab, text = "Reset all values",    bg = "red",    fg = "black", command = self.default_all)
        self.open_button =   tk.Button( root_tab, text='Open a File', command=self.file_open )
        self.proceed_button = tk.Button(root_tab, text="Produce G-Code", command=self.process)



       # submit, reset, open/save  file buttons
        self.button_submit.grid(  row = 1,  column = 3, pady = 5)
        self.button_reset.grid(   row = 2,  column = 3, pady = 5)
        self.open_button.grid(    row = 8,  column=  3, padx = 5, pady = 5)
        #self.button_open.grid(   row = 7,  column = 3, pady = 5)
        self.button_save.grid(    row = 8,  column = 4, pady = 5)
        self.proceed_button.grid( row = 18, column = 0, padx = 5, pady = 5)
        #self.test_button.grid( row = 18, column = 3, padx = 5, pady = 5 )

        # GCode tab/page setup
        self.notebook.add(gcode_tab, text="G-Code")

        self.param_gcgen = tk.Text(gcode_tab, bg="white", fg="black", width = 820, height=31)
        self.param_gcgen.pack(side=tk.TOP, expand=1)

        self.gcode_copy_button = tk.Button(gcode_tab, text="Copy G-Code to Clipboard", command=self.copy_to_clipboard)
        self.gcode_copy_button.pack(side=tk.TOP, fill=tk.NONE) #self.gcode_copy_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.test_button = tk.Button(gcode_tab, text="Copy command to Clipboard", command=self.copy_command_to_clipboard)
        self.test_button.pack(side=tk.BOTTOM, fill=tk.NONE)

        self.gcode_status = tk.StringVar(gcode_tab)
        self.gcode_status.set("--")

        self.gcode_label = tk.Label(gcode_tab, textvar=self.gcode_status, bg="lightgrey", fg="black")
        self.gcode_label.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.notebook.pack(fill=tk.BOTH, expand=1)
        self.default_all()

        # Help tab/page setup
        self.notebook.add(help_tab, text="Help/Info")
        self.docum = tk.Text(help_tab, bg="white", fg="black", width = 820, height=33)
        self.docum.pack(side=tk.TOP, expand=1)
        self.docum.insert(1.0,"this page will document  help, info and credits ... \n\nto come")

    def onValidateFloat(self, P ):
        pattern = r"[-+]?\d*\.?\d*"
        if re.fullmatch(pattern, P) is None:
            self.bell()
            return False
        else:
            return True

    def onValidateInt(self, P ):
        pattern = r"[-+]?\d*"
        if re.fullmatch(pattern, P) is None:
            self.bell()
            return False
        else:
            return True

    def process(self,text=None):
        if self.verify_parameters() == False:
            return
        if not text:
            text = " ".join(["python", "meringues_gcode_generator_para.py" , "-x" , self.nX.get(), "-y", self.nY.get(), "-a" , self.oX.get(), "-b", self.oY.get(),"-z" , self.sZ.get(), "-k", self.tZ.get(),
                                                                             "-i" , self.sX.get(), "-j", self.sY.get(), "-p" , self.sh.get(), "-m" , self.ho.get() ,
                                                                             "-d" , self.mD.get(), "-t", self.mH.get(), "-r", self.re.get() , "-s", self.sV.get(), "-w", self.nS.get() ])
        try:
            self.gcode_status.set(text)
            gcode_txt = subprocess.run(["python", "meringues_gcode_generator_para.py" , "-x" , self.nX.get(), "-y", self.nY.get(), "-a" , self.oX.get(), "-b", self.oY.get() ,"-z" , self.sZ.get(), "-k", self.tZ.get(),
                                                                             "-i" , self.sX.get(), "-j", self.sY.get(), "-p" , self.sh.get(), "-m" , self.ho.get() ,
                                                                             "-d" , self.mD.get(), "-t", self.mH.get(), "-r", self.re.get() , "-s", self.sV.get(), "-w", self.nS.get()
                                                                                          ]  , capture_output=True, text=True, check=True, timeout= 3)


            self.param_gcgen.delete(1.0,tk.END)
            self.param_gcgen.insert(1.0,gcode_txt.stdout)
            msg.showinfo("Gcode produced", "meringues_gcode_generator_param.py executed\n see G-Code tab for result")
        except Exception as e:
            msg.showerror("G-Code production failed" + text ,  str(e))

    def copy_to_clipboard(self, text=None):
        if not text:
            text = self.param_gcgen.get(1.0,tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        msg.showinfo("Copied Successfully", "Text copied to clipboard")

    def copy_command_to_clipboard(self):
        print( self.gcode_status.get() )
        self.clipboard_clear()
        self.clipboard_append(self.gcode_status.get())
        msg.showinfo("Copied Successfully", "Command copied to clipboard")

    def file_open(self):
        # file type
        filetypes = (('G-Code files', '*.gco *.nc *.gcode *.GCO *.NC *.GCODE *.Gcode'), ('All files', '*.*') )
        # show the open file dialog
        f = fidi.askopenfile(filetypes=filetypes)
        fn = f.name
        dn = os.path.dirname(fn)
        bn = os.path.basename(fn)
        self.of.delete(0,tk.END)
        self.of.insert(0,dn)
        self.fN.delete(0,tk.END)
        self.fN.insert(0,bn)
        data = f.read()
        self.param_gcgen.delete(1.0, tk.END)
        self.param_gcgen.insert(1.0, data)
        #print(data)
        f.close()

    def file_save(self, text=None):
        fin = self.fN.get()
        if ( fin is not None) and ( fin !='') and ( fin != "n.d." ):
            with open(fin, 'w') as f:
                content = self.param_gcgen.get('1.0', tk.END)
                f.write(content)
                msg.showinfo("File written", fin + " ... saved to local directory")
                f.close
        else:
            msg.showinfo("No file written", "file name not defined or empty")

    def runtest(self):
        param = " "
        for par in self.nparas:
            parv = eval("self." + par + ".get()" )
            if ( parv is not None) and ( parv !='') :
               param += par + "= " + eval("self." + par + ".get()" ) + " "
        msg.showinfo( " result ", param )

    def verify_parameters(self):
        for par in self.nparas:
            parv = eval("self." + par + ".get()" )
            if ( parv is None) or ( parv == '') :
               msg.showinfo( "one or more missing parameter ",par )
               return False
        if (self.ho.get()) is None or ( self.ho.get() == '' ) :
            msg.showinfo( "Problem","one or more missing parameter (--home)" )
            return False
        if (self.sh.get()) is None or ( self.sh.get() == '' ) :
            msg.showinfo( "Problem ","one or more missing parameter (--shape)" )
            return False
        return True



    def calculate(self, text=None):
        # get a content from entry box
        vnX = int(self.nX.get())
        vnY = int(self.nY.get())
        voX = int(self.oX.get())
        voY = int(self.oY.get())

        # Calculates compound interest
        if (vnY != '' ) and (vnY != '') :
            number = vnX * vnY
        else:
            number = 0

        # insert method inserting the value in the text entry box.
        self.to.delete(0, tk.END)
        self.to.insert(1, number)

    def default_all(self, text=None):
        # whole content of entry boxes set to default values

        self.nX.delete(0, tk.END) ; self.nX.insert(0,"2")
        self.nY.delete(0, tk.END) ; self.nY.insert(0,"2")
        self.oX.delete(0, tk.END) ; self.oX.insert(0,"20")
        self.oY.delete(0, tk.END) ; self.oY.insert(0,"20")
        self.sX.delete(0, tk.END) ; self.sX.insert(0,"25")
        self.sY.delete(0, tk.END) ; self.sY.insert(0,"25")

        self.sZ.delete(0, tk.END) ; self.sZ.insert(0,"0")
        self.tZ.delete(0, tk.END) ; self.tZ.insert(0,"25")

        self.to.delete(0, tk.END) ; self.to.insert(0,"4")
        self.fN.delete(0, tk.END) ; self.fN.insert(0,"n.d.")
        self.sV.delete(0, tk.END) ; self.sV.insert(0,"1.8")
        self.re.delete(0, tk.END) ; self.re.insert(0,"4.0")
        self.mH.delete(0, tk.END) ; self.mH.insert(0,"12.0")
        self.mD.delete(0, tk.END) ; self.mD.insert(0,"13.0")
        self.nS.delete(0, tk.END) ; self.nS.insert(0,"3.0")
        self.ho.delete(0, tk.END) ; self.ho.insert(0,"no")
        self.sh.delete(0, tk.END) ; self.sh.insert(0,"kiss")
        self.of.delete(0, tk.END) ; self.of.insert(0,"n.d.")

        # set focus on  an entry box
        self.nX.focus_set()


if __name__ == "__main__":
    meringuetool = MeringueTool()
    meringuetool.mainloop()
