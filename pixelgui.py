'''
Class layout adapted from 
https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter/7557028#7557028
'''

import sys 

import tkinter as tk
import numpy as np
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib import figure              #see self.fig, self.ax.

import matplotlib                          #I need this for matplotlib.use. sowwee.
matplotlib.use('TkAgg')                    #strange error messages will appear otherwise.

from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import filedialog
import glob

import matplotlib.ticker as ticker
from PIL import Image, ImageChops
import cv2

homedir = os.getenv('HOME')

#create main window container, into which the first page will be placed.
class App(tk.Tk):
    
    def __init__(self, path_to_repos, initial_browsedir, window_geometry, init_offset):  #INITIALIZE; will always run when App class is called.
        tk.Tk.__init__(self)     #initialize tkinter; *args are parameter arguments, **kwargs can be dictionary arguments
        
        self.title('Project Pixel: Generate Pixelated Images for Art')
        self.geometry(window_geometry)
        self.resizable(True,True)
        self.rowspan=10
        
        #will be filled with heaps of frames and frames of heaps. 
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)     #fills entire container space
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        ## Initialize Frames
        self.frames = {}     #empty dictionary
        frame = MainPage(container, self, path_to_repos, initial_browsedir, init_offset)   #define frame  
        self.frames[MainPage] = frame     #assign new dictionary entry {MainPage: frame}
        frame.grid(row=0,column=0,sticky='nsew')   #define where to place frame within the container...CENTER!
        for i in range(self.rowspan):
            frame.columnconfigure(i, weight=1)
            frame.rowconfigure(i, weight=1)
        
        self.show_frame(MainPage)  #a method to be defined below (see MainPage class)
    
    def show_frame(self, cont):     #'cont' represents the controller, enables switching between frames/windows...I think.
        frame = self.frames[cont]
        frame.tkraise()   #will raise window/frame to the 'front;' if there is more than one frame, quite handy.
        
#inherits all from tk.Frame; will be on first window
class MainPage(tk.Frame):    
    
    def __init__(self, parent, controller, path_to_repos, initial_browsedir, init_offset):
        
        #defines the number of rows/columns to resize when resizing the entire window.
        self.rowspan=10
        
        self.init_offset = float(init_offset)
        self.color = 'black'    #for gridlines
        
        #generalized parameters given in params.txt file
        self.path_to_repos = path_to_repos
        self.initial_browsedir = initial_browsedir
        
        #first frame...
        tk.Frame.__init__(self,parent)
        
        #create display frame!
        self.frame_display = tk.LabelFrame(self,text='Image',font='Vendana 15',padx=5,pady=5)
        self.frame_display.grid(row=0,column=0,rowspan=5)
        #include the following so that frame size adjusts correspondingly to window size
        for i in range(self.rowspan):
            self.frame_display.columnconfigure(i,weight=1)
            self.frame_display.rowconfigure(i,weight=1)
            
        #add the Browse/Refresh frame!
        self.frame_buttons=tk.LabelFrame(self,text='File Browser',padx=5,pady=5)
        self.frame_buttons.grid(row=0,column=1,columnspan=2)
        for i in range(self.rowspan):
            self.frame_buttons.columnconfigure(i,weight=1)
            self.frame_buttons.rowconfigure(i,weight=1)
        
        #create pixel parameter frame!
        self.frame_params = tk.LabelFrame(self,text='Parameters',padx=5,pady=5)
        self.frame_params.grid(row=1,column=1)
        for i in range(self.rowspan):
            self.frame_params.columnconfigure(i,weight=1)
            self.frame_params.rowconfigure(i,weight=1)
        
        ##############
        #SPECIFY INITIATION FUNCTIONS.
        #(All functions are defined below this section.)
        ##############
        self.im_to_display()   #creates browse frame
        self.init_display_size()   #creates canvas frame
        self.populate_params()     #creates parameter frame
    
    #add pixelation/resizing features
    def resize_widgets(self):
        
        npx_lab = tk.Label(self.frame_params,text='N Pixels',
                           font='Arial 13').grid(row=0,column=0)
        npx_lab = tk.Label(self.frame_params,text='(for x if x>y, y if y<x)',
                           font='Arial 13').grid(row=1,column=0)
        
        self.npx = tk.Entry(self.frame_params,width=5,borderwidth=2,bg='black',fg='lime green',font='Arial 15')
        self.npx.insert(0,'50')
        self.npx.grid(row=0,column=1,rowspan=2)
        
        self.pix_button = tk.Button(self.frame_params,text="Pixelate", padx=5, pady=5, 
                                        font='Arial 20', command=self.resize_im)
        self.pix_button.grid(row=3,column=0,columnspan=2,sticky='ew')
        
        
        self.divider = tk.Label(self.frame_params,text='=======================', 
                                font='Arial 13').grid(row=4,column=0,sticky='ew')
    
    #add grid checkbox to frame_params
    def grid_checkbox(self):
        
        self.var = tk.IntVar()   #initiate variable
        self.gridcheck = tk.Checkbutton(self.frame_params,text='Add Gridlines',
                                        onvalue=1,offvalue=0,command=self.add_grid,
                                        variable=self.var,font='Arial 18')
        self.gridcheck.grid(row=4,column=0,sticky='ew',columnspan=2)
    
    #add grid textbox to frame_params --> specify color of grid lines AND line spacing
    def grid_textbox(self):
        
        linespacing_lab = tk.Label(self.frame_params,text='Line Spacing',font='Arial 13').grid(row=5,column=0)
        color_grid_lab = tk.Label(self.frame_params,text='Grid Color',font='Arial 13').grid(row=6,column=0)
        offset_val_lab = tk.Label(self.frame_params,text='Offset Value',font='Arial 13').grid(row=7,column=0)
        
        self.line_spacing = tk.Entry(self.frame_params,width=5,borderwidth=2,bg='black',fg='lime green',
                                      font='Arial 15')
        self.line_spacing.insert(0,'1')
        self.line_spacing.grid(row=5,column=1)
        
        self.color_grid = tk.Entry(self.frame_params,width=5,borderwidth=2,bg='black',fg='lime green',
                                      font='Arial 15')
        self.color_grid.insert(0,'black')
        self.color_grid.grid(row=6,column=1)
        
        self.offset_val = tk.Entry(self.frame_params,width=5,borderwidth=2,bg='black',fg='lime green',
                                   font='Arial 15')
        self.offset_val.insert(0,str(self.init_offset))
        self.offset_val.grid(row=7,column=1)
        
    
    def populate_params(self):
        self.resize_widgets()
        self.grid_checkbox()    
        self.grid_textbox()
    
    
    #add browsing textbox to frame_buttons
    def im_to_display(self):
        self.path_to_im = tk.Entry(self.frame_buttons, width=35, borderwidth=2, 
                                   bg='black', fg='lime green', font='Arial 20')
        self.path_to_im.insert(0,'Type path/to/image.fits or click "Browse"')
        self.path_to_im.grid(row=0,column=0,columnspan=2)
        self.add_browse_button()
        self.add_enter_button()

    #add browse button to frame_buttons
    def add_browse_button(self):
        self.button_explore = tk.Button(self.frame_buttons ,text="Browse", padx=20, pady=10, 
                                        font='Arial 20', command=self.browseFiles)
        self.button_explore.grid(row=1,column=0)

    #add enter/refresh button to frame_buttons
    def add_enter_button(self):
        self.path_button = tk.Button(self.frame_buttons, text='Enter/Refresh', padx=20, pady=10, 
                                 font='Arial 20', command=self.initiate_canvas)
        self.path_button.grid(row=1,column=1)

    #function for opening the file explorer window
    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir = self.initial_browsedir, 
                                              title = "Select a File", 
                                              filetypes = ([('Image Files', '.jpg .png .jpeg')]))
        self.path_to_im.delete(0,tk.END)
        self.path_to_im.insert(0,filename)  

    def init_display_size(self):
        #aim --> match display frame size with that once the canvas is added
        #the idea is for consistent aestheticsTM
        self.fig = figure.Figure(figsize=(6,6), layout="constrained")
        #self.fig.subplots_adjust(left=0.06, right=0.94, top=0.94, bottom=0.06)

        self.ax = self.fig.add_subplot()
        self.im = self.ax.imshow(np.zeros(100).reshape(10,10))
        self.ax.set_title('Click "Browse" to the right to begin!',fontsize=15)
        self.text = self.ax.text(x=2.2,y=4.8,s='Your Image \n Goes Here',color='red',fontsize=25)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_display) 

        #add canvas 'frame'
        self.label = self.canvas.get_tk_widget()
        self.label.grid(row=0,column=0,columnspan=4,rowspan=6,sticky='nsew')
    
    #setting up file variables
    def img_firstpass(self):
        full_filepath = str(self.path_to_im.get())

        self.img_only = Image.open(full_filepath)
        self.img_array = np.asarray(self.img_only)

        #add title...because why not?
        try:
            full_filepath = full_filepath.split('/')   #split full pathname into components
            full_filename = full_filepath[-1]          #isolate filename
            split_filename = full_filename.split('.')  #separate image name from file extension
            self.filename = split_filename[0]
        except:
            print('Error. Defaulting to "Generic" for canvas title.')
            self.filename = 'Generic'
        
    def draw_im_canvas(self):

        #delete any and all miscellany from the canvas (including that which was created using self.init_display_size())
        self.label.delete('all')
        self.ax.remove()

        self.ax = self.fig.add_subplot()
        self.im = self.ax.imshow(np.flipud(self.img_array),origin='lower')
        self.ax.set_xlim(0,np.shape(self.img_array)[1]-1)
        self.ax.set_ylim(0,np.shape(self.img_array)[0]-1)

        self.ax.set_title(f'{self.filename}',fontsize=15)

        #self.im_x, self.im_y = np.shape(self.img_array)[1], np.shape(self.img_array)[0]
        #print('img dimensions', (self.im_x, self.im_y))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_display)    

        #add canvas 'frame'
        self.label = self.canvas.get_tk_widget()
        self.label.grid(row=0,column=0,columnspan=3,rowspan=6)
    
    #use ONLY for the enter/refresh button. first file pass!
    def initiate_canvas(self):
        self.img_firstpass()
        self.draw_im_canvas()
    
    #this function helps ensure that pixel cells are square- and not rectangular-shaped
    def get_scaling_fraction(self):
        
        self.height = np.shape(self.img_array)[0]
        self.width = np.shape(self.img_array)[1]
        
        if self.height>self.width:
            fraction = self.width/self.height
            return 1, fraction
        elif self.height<self.width:
            fraction = self.height/self.width
            return fraction, 1
        elif self.height==self.width:
            return 1, 1
        else:
            print("I don't know what to tell ye. Your width and/or height are not numbers.")
            return None
    
    #resizing the image and recreating the canvas.
    def resize_im(self):
        
        self.img_firstpass()
        
        self.frac_h, self.frac_w = self.get_scaling_fraction() 
        self.npixels = int(self.npx.get())
        
        #resize "smoothly" down to desired number of pixels for x (nx*frac_w) and y (nx*frac_h)
        #resample options: NEAREST, BILINEAR, BICUBIX, LANCZOS, BOX, HAMMING
        self.img_scaled = self.img_only.resize((int(self.npixels*self.frac_w), 
                                                int(self.npixels*self.frac_h)),
                                               resample=Image.NEAREST)
        
        self.img_array = np.asarray(self.img_scaled)
        
        self.draw_im_canvas()
        
        
    def add_grid(self):
        
        if self.var.get()==1:
        
            self.xticks = []
            self.yticks = []
            self.xlabels = []
            self.ylabels = []
            
            user_color = self.color_grid.get()
            line_spacing = int(self.line_spacing.get())
            offset = float(self.offset_val.get())
            
            self.xlines = []
            self.ylines = []
    
            #set y gridlines and labels
            for n in range(0,np.shape(self.img_array)[0],line_spacing):
                line = self.ax.axhline(n+offset,lw=1,color=user_color,alpha=0.3)
                self.xlines.append(line)
                
                #for labels --> only include 0s and multiples of 10.
                if n==0:
                    self.yticks.append(n-offset)
                    self.ylabels.append(n)
                if (n+1)%10==0:
                    self.yticks.append(n+offset)
                    self.ylabels.append(n+1)
           
            #set x gridlines and labels
            for n in range(0,np.shape(self.img_array)[1],line_spacing):
                
                line = self.ax.axvline(n+offset,lw=1,color=user_color,alpha=0.3)
                self.ylines.append(line)    
                    
                #for labels --> only include 0s and multiples of 10.
                if n==0:
                    self.xticks.append(n-offset)
                    self.xlabels.append(n)
                if (n+1)%10==0:
                    self.xticks.append(n+offset)
                    self.xlabels.append(n+1)
            
            self.ax.tick_params(labelsize=15)
            self.ax.set_xticks(self.xticks,labels=self.xlabels,fontsize=15)
            self.ax.set_yticks(self.yticks,labels=self.ylabels,fontsize=15)
            
            self.canvas.draw()
                
        else:
            for n in self.xlines:
                n.remove()
                self.ax.xaxis.set_major_locator(ticker.AutoLocator())
            for n in self.ylines:
                n.remove()
                self.ax.yaxis.set_major_locator(ticker.AutoLocator())
            self.canvas.draw()
            
if __name__ == "__main__":
    
    #unpack params.txt file here
    if '-h' in sys.argv or '--help' in sys.argv:
        print("USAGE: %s [-params (name of parameter.txt file, no single or double quotations marks)]")
    
    if '-params' in sys.argv:
        p = sys.argv.index('-params')
        param_file = str(sys.argv[p+1])
        
    #create dictionary with keyword and values from param textfile
    param_dict={}
    with open(param_file) as f:
        for line in f:
            try:
                key = line.split()[0]
                val = line.split()[1]
                param_dict[key] = val
            except:
                continue
        
        #extract parameters and assign to variables...
        path_to_repos = param_dict['path_to_repos']
        initial_browsedir = param_dict['initial_browsedir']
        window_geometry = param_dict['window_geometry']
        init_offset = param_dict['init_offset']
        
        app = App(path_to_repos, initial_browsedir, window_geometry, init_offset)
        app.mainloop()
        
        
#add following features:
#checkbox to flip x-axis 
#slider to change spaces between grid lines (i.e., how many grid lines are shown)
#widget with +1, -1 increments for desired px cells on x or y axis
#choose number of representing colors...trying to avoid grays. commit to black or white!
#save button!