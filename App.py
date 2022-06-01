from tkinter.tix import COLUMN
import customtkinter as ctK
import tkinter as tk
from tkinter import filedialog as fd
import os
from pathlib import Path 
import mne
import matplotlib.pyplot as plt
from tkinter import ttk
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from win32api import GetSystemMetrics
import numpy as np
plt.style.use('dark_background')
mne.set_log_level(0)
DARK_MODE = "dark"
LIGHT_MODE = "light"
ctK.set_appearance_mode(DARK_MODE)
ctK.set_default_color_theme("dark-blue")
SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)


class App(ctK.CTk):
    global i
    def __init__(self, *args, fg_color="default_theme", **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        # self.geometry("1700x920")
        # self.minsize(1650,850)
        self.geometry(f'{int(SCREEN_WIDTH/1.5)}x{int(SCREEN_HEIGHT/1.5)}')
        self.minsize(int(SCREEN_WIDTH/1.7),int(SCREEN_HEIGHT/1.8))
        self.title('EEG by Amin Fakia')
        #self.resizable(0, 0)
        left_frame_width = 300
        
        self.frame_left = ctK.CTkFrame(master=self,width=left_frame_width)
        #frames
        self.info_frame = ctK.CTkFrame(master=self.frame_left,width=left_frame_width, height=100,corner_radius=15)
        
        self.editing_frame = ctK.CTkFrame(master=self.frame_left,width=left_frame_width, height=400,corner_radius=15)

        self.log_frame = ctK.CTkFrame(master=self.frame_left,width=left_frame_width, height=50,corner_radius=15)

        self.plot_frame = ctK.CTkFrame(master=self, width=SCREEN_WIDTH/2, height=SCREEN_HEIGHT/2,corner_radius=15)
        
        self.freq_frame = ctK.CTkFrame(master=self.editing_frame,width=left_frame_width)
        
        #figures
        self.fig, self.ax = plt.subplots(nrows=2,figsize=(12,8))

        self.frame_left.pack(side="left",fill="y")
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=1)
        #buttons
        self.get_edf_btn = ctK.CTkButton(master=self.frame_left,text="Load EDF",width=left_frame_width,command=self.get_edf)
        self.apply_bandpass_btn = ctK.CTkButton(master=self.editing_frame,text="Apply Filter",command=self.apply_bandpass)
        self.reset_data_btn = ctK.CTkButton(master=self.editing_frame,text="Reset data",command=self.reset) # TODO: reset function
        # labels
        self.info_label = ctK.CTkLabel(master=self.info_frame,text="")

        self.sep = ttk.Separator(master=self.editing_frame,orient='horizontal')
        self.error_label = ctK.CTkLabel(master=self.editing_frame,text="")
        # entries
        self.lf_entry = ctK.CTkEntry(master=self.freq_frame , placeholder_text="Low Frequency")
        self.hf_entry = ctK.CTkEntry(master=self.freq_frame , placeholder_text="High Frequency")
        # sliders
        self.slider = ctK.CTkSlider(master=self.plot_frame, from_=0, to=100, command=self.slider_event)
        


        self.get_edf_btn.pack(fill="x")
        self.last_t = 0
        self.filepath = ""
        self.edfFile = ""
        self.info = None
        self.raw = None
        self.frequency = []
    def get_edf(self):
        self.filepath = fd.askopenfilename()
        _, file_extension = os.path.splitext(self.filepath)
        if file_extension == ".edf":
            #self.get_edf_btn.place(relx=0.025, rely=0.05, anchor=tk.NW)

            self.edfFile = self.filepath
            self.get_mne_raw()
            self.get_editing_tools()
            # self.error_label.place(relx=0.5,rely=0.4,anchor=tk.CENTER)
            self.plot_frame.place(relx=0.6,rely=0.48,anchor=tk.CENTER)
            
            #self.plot_frame.pack(fill="x",pady=10)

            
            #self.plot_frame.pack(fill="x")
            #self.reset_data_btn.place(relx=0.5,rely=0.3,anchor=tk.CENTER)
            
            self.slider.pack(fill=tk.BOTH,padx=70)
            self.get_plot()
            self.get_edf_btn.pack(fill="x",pady=10)
    def get_plot(self,min_s=0,max_s=5):
        self.ax[0].clear()
        self.ax[1].clear()
        data = self.raw.get_data()
        times = self.raw.times
        

        self.ax[0].plot(times, data[13])
        self.ax[0].axvspan(min_s, max_s, color='red', alpha=0.25)
        try:
            ft = np.abs(np.fft.rfft(data[13][int(min_s*300):int(max_s*300)]))
            frequency = np.linspace(0, 300/2, len(ft))
            self.ax[1].plot(frequency,ft,color='red',label=(f'{sum(ft):.3f}'))
            self.ax[1].legend()
            self.ax[1].set_ylim((0,10e-3))
        except:
            pass

        plt.draw()
        self.canvas.draw()
    def slider_event(self,value):
        t = self.last_t * (value/100)
        self.get_plot(t,t+5)

  
    def apply_bandpass(self):
        try:
            lf = float(self.lf_entry.get())
            hf = float(self.hf_entry.get())
            self.raw.filter(lf,hf)
            self.error_label.configure(text_color="green")
            self.error_label.set_text("Successfully applied filter") 
            self.get_plot()
        except:
            self.error_label.configure(text_color="red")
            self.error_label.set_text("please enter a valid frequency range") 
        
    def reset(self):
        self.get_mne_raw()
        self.get_plot()
        self.error_label.configure(text_color="yellow")
        self.error_label.set_text("Succefully reset the data") 
        pass
    def get_editing_tools(self):
        #self.editing_frame.place(relx=0.025,rely=0.25, anchor=tk.NW)
        self.editing_frame.pack(fill="x",pady=10)
        # self.lf_entry.place(relx=0.25,rely=0.1,anchor=tk.CENTER)
        # self.hf_entry.place(relx=0.75,rely=0.1,anchor=tk.CENTER)
        self.freq_frame.pack(pady=10)
        self.lf_entry.pack(side=tk.LEFT,padx=5)
        self.hf_entry.pack(side=tk.LEFT,padx=5)
        # self.apply_bandpass_btn.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
        self.apply_bandpass_btn.pack(pady=10)
        
        self.reset_data_btn.pack(pady=10)
        self.error_label.pack(fill="x",pady=10)
        #self.lf_slider.place(relx=0.5,rely=0.1,anchor=tk.CENTER)
        # self.lf_slider.pack()
        pass   
    def get_mne_raw(self):
        self.raw = mne.io.read_raw_edf(self.edfFile,preload=True).copy()
        #filename, _ = os.path.splitext(edfFile)
        self.last_t = self.raw.times[-1]
        
        keys = ['sfreq','nchan','highpass','lowpass']
        self.info =  [self.raw.info.get(k) for k in keys]
        #self.info_frame.place(relx=0.025,rely=0.1, anchor=tk.NW)
        
        self.info_label.set_text(f'Loaded: {Path(self.edfFile).name}\nsample frequency: {self.info[0]} Hz\nnumber of channels: {self.info[1]}\nhighpass: {self.info[2]} Hz\nlowpass: {self.info[3]} Hz')
        self.info_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.info_frame.pack(fill="x",pady=10)
        #self.info_label.pack()

        
 


if __name__ == "__main__":
    app = App()
    
    app.mainloop()
