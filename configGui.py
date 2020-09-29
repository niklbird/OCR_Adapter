from tkinter import mainloop
from tkinter import *
from tkinter import filedialog
import sys
import cv2
import copy

class ScreenClass(object):
    stopPro = 0
    
    input_0 = 0
    input_1 = 0
    input_2 = 0
    input_3 = 0
    button_0 = 0
    button_1 = 0
    button_2 = 0
    button_3 = 0
    
    label_0 = 0
    label_1 = 0
    
    error_label = 0
    correct_label = 0
    
    levelComplete = 0
    
    File_Name = 'C:/Users/Niklas/Desktop/PEM OCR/Videos/vid1.mp4'
    Dir_Name = 'EMPTY'
    
    master = 0
    
    X_left = 0
    X_right = 1920
    Y_up = 0
    Y_down = 1080
    
    frame = 0
    edit_frame = 0
    
    Start_Time = 0
    End_Time = 10
    OCR_Active = 0
    Plot_Graphs = 0
    Multiple_Graphs = 0
    
    Color_LB = 150
    Color_UB = 254
    Binary_LB = 127
    Binary_UB = 254
    
    Color_Filter_Active = False
    Grey_Filter_Active = False
    Binary_Filter_Active = False
    Blurr_Filter_Active = False
    Invert_Color_Active = False
    Brightness_Adj_Active = False
    Contrast_Adj_Active = False
    
    exiPro = 1
    
    scale = 0
    
    cvWindow = 0
    cvWindow_2 = 0
    
    height = 0
    width = 0
    
    alpha_b = 1.0
    gamma_b = 2.25
    alpha_c = 0.0
    gamma_c = 0.0
    
    def __init__(self,master):
        print('Init')
        self.master = master
        #return self.screen_0()
    
    def start(self):
        return self.screen_0()
        
    def commandMock(self):
        print('Mock')
        return 0
    
    def clearWindow(self):
        self.master.destroy()
        
    def nextLevel(self, master):
        print(master)
        print('Quitting')
        self.levelComplete = 1
        self.root.destroy()
    
    def standardEntry(self, master, co, ro):
        entry = Entry(master, borderwidth=2, relief="groove", font=("MS Sans Serif", 11))
        entry.grid(column=co, row=ro)
        return entry
    
    def standardLabel(self, master, textField, co, ro):
        lab = Label(master,bg="white", text=textField, font=('Arial', 11))
        lab.grid(column=co, row=ro)
        return lab

    def standardButton(self, master, textField, com, co, ro):
        button = Button(master, text=textField, width=20, height=1,bg="white",borderwidth=2, relief="groove", command=com)
        button.grid(column=co, row=ro)
        return button

    def dirDialog(self):
        dname = filedialog.askdirectory()
        self.Dir_Name = dname
        self.label_1 = self.standardLabel(self.master, str(dname).split('/')[-1],0,1)
        self.checkScreen_0()
        
    def fileDialog(self):
        fname = filedialog.askopenfilename(filetypes=(("*mp4", "*.mp4"),
                                                      ("*avi", "*.avi"),
                                               ("All files", "*.*") ))
        self.File_Name = fname
        self.label_0 = self.standardLabel(self.master, str(fname).split('/')[-1],0,0)
        self.checkScreen_0()
        
    #Turn input into number
    def stringInt(self, s,default):
        if(s == ''):
            return default
        else:
            return int(s)
    
    def adjScreen(self,x):
        if(cv2.getTrackbarPos('Links', 'Win') > 0 and cv2.getTrackbarPos('Links', 'Win') < cv2.getTrackbarPos('Rechts', 'Win')):
            self.X_left = cv2.getTrackbarPos('Links', 'Win')
        if(cv2.getTrackbarPos('Rechts', 'Win') > cv2.getTrackbarPos('Links', 'Win')):
             self.X_right = cv2.getTrackbarPos('Rechts', 'Win')
        if(cv2.getTrackbarPos('Oben', 'Win') > 0 and cv2.getTrackbarPos('Oben', 'Win') < cv2.getTrackbarPos('Unten', 'Win')):
             self.Y_up = cv2.getTrackbarPos('Oben', 'Win')  
        if(cv2.getTrackbarPos('Unten', 'Win') > cv2.getTrackbarPos('Oben', 'Win')):
            self.Y_down = cv2.getTrackbarPos('Unten', 'Win') 
        if(cv2.getTrackbarPos('Speichern', 'Win') == 1):
            self.cvWindow = 0
            cv2.destroyAllWindows()
            self.frame = self.frame[int(self.Y_up):int(self.Y_down), int(self.X_left):int(self.X_right)]
            return 0
        p_frame = self.frame[int(self.Y_up):int(self.Y_down), int(self.X_left):int(self.X_right)]
        cv2.imshow('Win2', p_frame)
    
    def cutWindow(self):
        cv2.imshow('Win2',self.frame)
        self.cvWin_0(self.height, self.width)
    
    def checkScreen_0(self):
        pre_frame = 0
        #Take 50th frame to test if video-file input works
        try:
            cap = cv2.VideoCapture(self.File_Name)
            ret, self.frame = cap.read()
            for i in range(0,50):
                ret, self.frame = cap.read()
            #self.frame = cv2.imread('bildNiefhoff.jpg')
            print(self.frame.shape)
            self.X_right = self.frame.shape[1]
            self.Y_down = self.frame.shape[0]
        except:
            #Make error_label singleton
            print('Video-File not found')
            try:
                self.error_label.destroy()
            except:
                pass
            self.error_label = Label(self.master,bg="red",width = 13, text='ERROR\n-->Lesefehler', font=("MS Sans Serif", 14))
            self.error_label.grid(column=0, row=6)
            return -1
        self.height, self.width, channels = self.frame.shape
        
        try:
            self.error_label.destroy()
        except:
            pass
        self.correct_label = Label(self.master,bg="green",width = 13,relief=SUNKEN, borderwidth=2, text='Einlesen\nErfolgreich', font=("MS Sans Serif", 14))
        self.correct_label.grid(column=0, row=2,rowspan = 2 )
        print('Coordinates read') 
        #cv2.imshow('Win',self.frame)
        cv2.waitKey()
        if(str(self.Dir_Name) == '0' or str(self.Dir_Name) == 'EMPTY'):
            try:
                self.correct_label.destroy()
            except:
                pass
            return -1
            self.error_label = Label(self.master,bg="red", width = 13, text='Fehlend\n-->Zielordner', font=("MS Sans Serif", 14))
            self.error_label.grid(column=0, row=2,rowspan = 2 )
            return -1
        else:
            print(str(self.Dir_Name))
            self.button_3.config(state=ACTIVE)
            self.button_3.config(bg='White')
            try:
                self.error_label.destroy()
            except:
                pass
            return 0
        
    def plotUnique(self):
        self.Multiple_Graphs = not self.Multiple_Graphs    
    
    def plotGraphs(self):
        self.Plot_Graphs = not self.Plot_Graphs
        if(self.Plot_Graphs):
            self.lab_4 = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Einzeln",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.plotUnique)
            self.lab_4.grid(column=0, row=3)
        else:
            try:
                self.lab_4.destroy()
            except:
                return -1
        
        
    def OCR_Button(self):   
        self.OCR_Active = not self.OCR_Active
        if(not self.OCR_Active):
            self.Plot_Graphs = 0
            self.Multiple_Graphs = 0
            try:
                self.lab_3.destroy()
            except:
                pass
            try:
                self.lab_4.destroy()
            except:
                return -1
        else:
            self.lab_3 = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Plotten",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.plotGraphs)
            self.lab_3.grid(column=0, row=2)
            
    def colorFilter(self):
        print('Color-Filter active = ' + str(not self.Color_Filter_Active))
        self.Color_Filter_Active = not self.Color_Filter_Active
        self.callFilter()
    
    def binFilter(self):
        print('Binary Filter active = ' + str(not self.Binary_Filter_Active))
        self.Binary_Filter_Active =  not self.Binary_Filter_Active
        self.callFilter()
            
    def greyFilter(self):
        print('Grey-Filter = ' + str(not self.Grey_Filter_Active))
        self.Grey_Filter_Active = not self.Grey_Filter_Active
        self.callFilter()
    
    def blurrFilter(self):
        print('Blurr-Filter = ' + str(not self.Blurr_Filter_Active))
        self.Blurr_Filter_Active = not self.Blurr_Filter_Active
        self.callFilter()
        
    def invertColor(self):
        print('Invert-Color = ' + str(not self.Invert_Color_Active))
        self.Invert_Color_Active = not self.Invert_Color_Active
        self.callFilter()
    
    def brightAdj(self):
        print('Brightness = ' + str(not self.Brightness_Adj_Active))
        self.Brightness_Adj_Active = not self.Brightness_Adj_Active
        self.callFilter()
        
    def contrastAdj(self):
        print('Contrast = ' + str(not self.Contrast_Adj_Active))
        self.Contrast_Adj_Active = not self.Contrast_Adj_Active
        self.callFilter()
        
    def exitProgram(self):   
        self.exiPro = 1
        self.master.destroy()
    
    def safeToFile(self):
        f = open('configuration.config', 'w')
        out = ''
        out += str(self.File_Name) + '\n'
        out += str(self.X_left) + ',' + str(self.X_right) + ','  + str(self.Y_up) + ',' + str(self.Y_down) + '\n'
        out += str(self.Start_Time) + ',' + str(self.End_Time) + '\n'
        out += str(int(self.OCR_Active)) + ',' + str(int(self.Plot_Graphs)) + ',' + str(int(self.Multiple_Graphs)) + '\n'
        out += str(int(self.Color_Filter_Active)) + ',' + str(int(self.Grey_Filter_Active)) + ',' + str(int(self.Binary_Filter_Active)) 
        out += ',' + str(int(self.Blurr_Filter_Active)) + ',' + str(int(self.Invert_Color_Active)) + '\n'
        out += str(self.Color_LB) + ',' + str(self.Color_UB) + ',' + str(self.Binary_LB) + ',' + str(self.Binary_UB) + '\n'
        out += str(int(self.Brightness_Adj_Active)) + ',' + str(int(self.Contrast_Adj_Active)) + '\n'
        out += str(self.alpha_b) + ',' + str(self.gamma_b) + ',' + str(self.alpha_c) + ',' + str(self.gamma_c) + '\n'
        out += str(self.Dir_Name)
        f.write(out)
        f.close()
        
        self.master.destroy()
        self.master = Tk()
        self.master.geometry('150x70')
        self.master.title('File-Safe')
        self.master.configure(bg="white")
        self.lab_1 = Label(self.master,bg="white", text='Konfiguration wurde \n gespeichert', font=("MS Sans Serif", 12))
        self.lab_1.grid(column=0,row=0)
        button = Button(self.master, text="Weiter", width=12, height=1,bg="white",borderwidth=2, relief="groove", command=self.exitProgram)
        button.grid(column=0, row=1)
        mainloop()
        if(self.exiPro == 1):
            print('Safed')
            return 1
    
    def callFilter(self):
        ed_frame = copy.copy(self.frame)
        print(self.Y_up)
        print(self.Y_down)
        print(self.X_left)
        print(self.X_right)
        #ed_frame = self.frame[int(self.Y_up):int(self.Y_down), int(self.X_left):int(self.X_right)]
        if(self.Color_Filter_Active):
            rev, ed_frame = cv2.threshold(ed_frame,self.Color_LB,self.Color_UB, cv2.THRESH_BINARY)
        if(self.Grey_Filter_Active):
            ed_frame = cv2.cvtColor(ed_frame, cv2.COLOR_BGR2GRAY)
        if(self.Binary_Filter_Active):
            trev,ed_frame = cv2.threshold(ed_frame, self.Binary_LB, self.Binary_UB, cv2.THRESH_BINARY)
        if(self.Blurr_Filter_Active == 1):
            ed_frame = cv2.medianBlur(ed_frame, 5)
        if(self.Brightness_Adj_Active):
            ed_frame = cv2.addWeighted(ed_frame, self.alpha_b, ed_frame, 0, self.gamma_b)
        if(self.Contrast_Adj_Active):
            ed_frame = cv2.addWeighted(ed_frame, self.alpha_c, ed_frame, 0, self.gamma_c)
        if(self.Invert_Color_Active):
            ed_frame = 255 - ed_frame    
        ed_frame[int(self.Y_up):int(self.Y_down), int(self.X_left):int(self.X_right)]
        print(ed_frame.shape)
        #print(showFrame.shape)
        cv2.imshow('Win4', ed_frame)
            
    def changeText(self, x):
        self.label_0.config(text = str(cv2.getTrackbarPos('R', 'Win')))
        
        
    def cvWin_0(self, width, height):
        if(self.cvWindow == 0):
            self.cvWindow = cv2.namedWindow('Win', cv2.WINDOW_AUTOSIZE)
            cv2.resizeWindow('Win', 300, 200)
            #cv2.imshow('Win',self.frame)
            print('Window1 created')
            cv2.createTrackbar('Links','Win',0, self.X_right, self.adjScreen)
            cv2.createTrackbar('Rechts','Win',self.X_right, self.X_right, self.adjScreen)
            cv2.createTrackbar('Oben','Win', 0, self.Y_down, self.adjScreen)
            cv2.createTrackbar('Unten','Win', self.Y_down, self.Y_down, self.adjScreen)
            cv2.createTrackbar('Speichern','Win', 0, 1, self.adjScreen)  
                  
                  
    def adjScreen_2(self,x):
        if(cv2.getTrackbarPos('Farbe_LB', 'Win3') > 0):
            self.Color_LB = cv2.getTrackbarPos('Farbe_LB', 'Win3')
        if(cv2.getTrackbarPos('Farbe_UB', 'Win3') > 0):
             self.Color_UB = cv2.getTrackbarPos('Farbe_UB', 'Win3')
        if(cv2.getTrackbarPos('Binary_LB', 'Win3') > 0):
             self.Binary_LB = cv2.getTrackbarPos('Binary_LB', 'Win3')  
        if(cv2.getTrackbarPos('Binary_UB', 'Win3') > 0):
            self.Binary_UB = cv2.getTrackbarPos('Binary_UB', 'Win3') 
        if(cv2.getTrackbarPos('Helligkeit', 'Win3')-255 != 0):
            brightness = cv2.getTrackbarPos('Helligkeit', 'Win3') - 255
            highlight = 0
            shadow = 0
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            self.alpha_b = (highlight - shadow)/255
            self.gamma_b = shadow
        if(cv2.getTrackbarPos('Kontrast', 'Win3') > 0):
            contrast = cv2.getTrackbarPos('Kontrast', 'Win3') 
            f = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            self.alpha_c = f
            self.gamma_c = 127*(1-f)
        if(cv2.getTrackbarPos('Speichern', 'Win3') == 1):
            self.cvWindow_2 = 0
            cv2.destroyAllWindows()
            return 0
        self.callFilter()
        
    def cvWin_2(self):
            self.cvWindow_2 = cv2.namedWindow('Win3', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Win4', self.frame)
            print('Window 3 created')
            cv2.createTrackbar('Farbe_LB','Win3',0, 255, self.adjScreen_2)
            cv2.createTrackbar('Farbe_UB','Win3',150, 255, self.adjScreen_2)
            cv2.createTrackbar('Binary_LB','Win3', 127, 255, self.adjScreen_2)
            cv2.createTrackbar('Binary_UB','Win3', 255, 255, self.adjScreen_2)
            cv2.createTrackbar('Helligkeit','Win3', 255, 510, self.adjScreen_2)
            cv2.createTrackbar('Kontrast','Win3', 50, 100, self.adjScreen_2)
            cv2.createTrackbar('Speichern','Win3', 0, 1, self.adjScreen_2)
        
    def quitProgram(self):
        self.stopPro = 1
        self.master.destroy()
            
    def continueProgram(self):
        self.master.destroy()    
        
    
    def screen_0(self):
        lab_0 = Button(self.master,bg="white",width = 15, text='Neu konfigurieren', font=("MS Sans Serif", 11),borderwidth=2, relief="groove", command=self.continueProgram)
        lab_0.grid(column=0, row=0)
        lab_1 = Button(self.master,bg="white",width = 15, text='Konfiguration laden', font=("MS Sans Serif", 11),borderwidth=2, relief="groove", command=self.quitProgram)
        lab_1.grid(column=0, row=1)
        mainloop()
        #Ueeebel haesslich aber einfachste Moeglichkeit
        if(self.stopPro):
            return -1
        self.master = Tk()
        self.master.title('Konfiguration2')
        self.master.configure(bg="white")
        button_0 = self.standardButton(self.master, 'Video', self.fileDialog, 1,0)
        button_1 = self.standardButton(self.master, 'CSV-Ordner', self.dirDialog, 1,1)
        button_2 = self.standardButton(self.master, 'Zuschneiden', self.cutWindow, 1,2)
        self.button_3 = self.standardButton(self.master, 'Weiter', self.screen_1, 1, 3)
        #TODO
        #self.button_3.config(state=DISABLED)
        mainloop()
        return 1

    def screen_1(self):
        self.clearWindow()
        self.master = Tk()
        self.master.title('Konfiguration')
        self.master.configure(bg="white")
        
        
        lab_0 = self.standardLabel(self.master, 'Start-Zeit', 0, 0)
        lab_1 = self.standardLabel(self.master, 'End-Zeit', 2, 0)
        self.input_0 = self.standardEntry(self.master, 1, 0)
        self.input_0.config(width=3)
        self.input_1 = self.standardEntry(self.master, 3, 0)
        self.input_1.config(width=3)
        
        lab_2 = Checkbutton(self.master,bg="white", height = 1, width = 10, text="OCR",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.OCR_Button)
        lab_2.grid(column=0, row=1)
        button_0 = self.standardButton(self.master, 'Weiter', self.screen_2, 0 ,5)
        self.master.mainloop()
        if(self.levelComplete == 0):
            return -1
        else:
            return 1
        
    def screen_2(self):
        try:
            self.Start_Time = self.stringInt(self.input_0.get(), 0)
        except:
            pass
        try:
            self.End_Time = self.stringInt(self.input_1.get(), 60)
        except:
            pass
        cv2.imshow('Win4', self.frame)
        self.cvWin_2()
        self.clearWindow()
        self.master = Tk()
        self.master.title('Konfiguration')
        self.master.configure(bg="white")
        colorButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Farb-Filter",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.colorFilter)
        colorButton.grid(column=0, row=0)
        greyButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Grau-Filter",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.greyFilter)
        greyButton.grid(column=0, row=1)
        binButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Binary-Filter",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.binFilter)
        binButton.grid(column=0, row=2)
        blurButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Blurr-Filter",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.blurrFilter)
        blurButton.grid(column=0, row=3)
        invButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Invertieren",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.invertColor)
        invButton.grid(column=0, row=4)
        brightButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Helligkeit",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.brightAdj)
        brightButton.grid(column=0, row=5)
        contrastButton = Checkbutton(self.master,bg="white", height = 1, width = 10, text="Kontrast",font=("MS Sans Serif", 14), borderwidth=2, relief="groove", command=self.contrastAdj)
        contrastButton.grid(column=0, row=6)
        greyButton.invoke()
        binButton.invoke()
        blurButton.invoke()
        #self.standardButton(self.master, 'Neues Fenster', self.cvWin_2(), 0 ,7)
        self.standardButton(self.master, 'Speicher', self.safeToFile, 0 ,8)
        self.callFilter()
        
        self.master.mainloop()
        return 1