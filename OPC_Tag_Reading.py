import OpenOPC
from OpenOPC import *
import time
import pywintypes
import datetime
import math
import sys
import tkinter
from tkinter import *
from tkinter import filedialog as tkFile
from tkinter import ttk
from matplotlib import pyplot as plt
import numpy as np
import win32com.client
from numpy import record

class OPC_Reader():
    """
    This class enables to read values from an OPC Server installed on the users machine and store them. 
    A graphical user interface is provided to input information about the server, the tags and the connection. 
    All tags of the server can be read for an arbitrary time amount. The sample rate can
    be chosen with respect to the latency of the connection.
    The read values can be saved in CSV format for later use and displayed as a plot.
    
    The class can be extended to connect to an OPC Server in the network as mentioned in the OPC manual.
    This was not intended as an 
    GUI text is currently in German.
    """ 
    
    __author__  = "Niklas Vogel"
    __license__ = "GPL"
    __version__  = "1.0 - 23.01.2020"
    __maintainer__  = "(Niklas Vogel)"
    __email__ = "niklas-vogel@hotmail.com"
    __status__  = "Development"
    
    recordingTime_s = 5
    scanInterval_s = 0.1
    scanTestCycles = 50
    scanInterval_limit_ms = 0
    
    countFactor = float(1.0/scanInterval_s)
    serverNames = []
    addedTags = []
    tagNames = []
    master = 0
    tagWindow = 0
    serverName = 'NONE'
    labelText = ''
    labelText_formated = ''
    og_text = ''
    opc = 0
    buttonID_Counter = 0
    recordingErrors = []
    csvNodes = []
    stopRec = 0
    folderName = ''
    
    def __init__(self):
        """Init method of class calls main()"""
        
        try:
            self.main()
        except Exception as e:
            self.writeError('FATAL ERROR IN CLASS INITILAZATION: ' + str(e))
            print(e)
            self.opc.close()
        
    def main(self):
        """Main function"""
        
        #Bugfix
        pywintypes.datetime = pywintypes.TimeType
        
        self.screen_0()
        
        
    def screen_0(self):
        """First half of first GUI screen"""
        
        print('Init program')
        self.master = Tk()
        self.master.title('Tag Reader')
        self.master.config(bg='white')
        label = self.standardLabel(self.master, 'OPC Tag Leser Umicore', 0, 0)
        label.config(font=('Arial', 12,'bold'))
        b = self.standardButton(self.master, 'Server Suche', self.mock, 0 , 1)
        b['command'] = lambda listrow=2, listcol=1, label_config=(self.master, '', 0, 2): self.scanOPCServer(listrow, listcol, label_config)
        mainloop()
     
        
    def screen_1(self):
        """Second half of first GUI screen""" 
        
        self.standardLabel(self.master, 'Kanal.Gerat.', 0, 4)
        self.standardLabel(self.master, 'Tag-Name:', 0, 5)
        input_1 = self.standardEntry(self.master, 1, 4)
        input_2 = self.standardEntry(self.master, 1, 5)
        input_1.focus_set()
        button_1 = self.standardButton(self.master, 'Neuer Tag', self.mock, 2, 5)
        button_1.config(width = 10)
        button_1['command'] = lambda  channel_input=input_1,  tag_input=input_2: self.newTag(channel_input, tag_input)
        tmp = self.standardButton(self.master, 'Speichern', self.mock, 0, 7)
        tmp['command'] = lambda label_config=(self.master, '', 1, 7): self.saveTags(label_config)
        tmp = self.standardButton(self.master, 'Laden', self.mock, 0, 8)
        tmp['command'] = lambda channel_input = input_1, label_config=(self.master, '', 1, 7): self.loadTags(channel_input, label_config)
        button_2 = self.standardButton(self.master, 'Weiter', self.screen_2, len(self.serverNames), 8)
        button_2.config(fg='green')
        
           
    def screen_2(self):
        """Second screen of GUI""" 
        
        self.master.destroy()
        self.master = Tk()
        self.master.title('OPC Verbindung')
        self.master.config(bg='white')
        
        tmp_lab = self.standardLabel(self.master, self.serverName, 0, 1) 
        tmp_lab.config(font=('Arial', 12,'bold'))
        tmp_lab2 = self.standardLabel(self.master, ' - Verbunden - ', 1, 1) 
        tmp_lab2.config(fg='green')   
        
        self.tagNames = []
        self.labelText = 'Zeit [s]; '
        self.labelText_formated = ''
        #Read in all added tag-buttons to save their text in "tag names". Create text for label
        for i in range(0, len(self.addedTags)):
            name = str(self.addedTags[i]['text'])
            self.tagNames.append(name)
            tmp = name.split('.')[-1] + ', '
            self.labelText_formated += tmp
            self.labelText += tmp
            if(len(self.labelText_formated.split('\n')[-1]) > 40): self.labelText_formated += '\n'   
        try: self.tagWindow.destroy()
        except: pass
        #Cut off last comma/last \n to make string look good
        if(len(self.labelText_formated) > 1 and not self.labelText_formated[-2] == ','): self.labelText_formated = self.labelText_formated[0:-3]
        elif(len(self.labelText_formated) > 1): self.labelText_formated = self.labelText_formated[0:-2]
        
        label = self.standardLabel(self.master, 'Teste Tags ...', 0, 0)
        self.master.update()
        label.config(text='Tags: [ ' + self.labelText_formated + ' ]', font=('Arial', 12,'bold'),fg='grey')
        label.grid(columnspan=3)
        #Verify tags
        s, _ = self.testTags(self.opc, self.tagNames)
        
        label_2 = self.standardLabel(self.master, 'Scan-Intervall...', 0, 2)
        self.master.update()
        if(s==''): pass
        else:
            label.config(fg='red', text='! Tags konnten nicht gelesen werden: ' + s)
            label_2.config(fg='red', text='! ERROR !')
            self.writeError('Screen 2: Tags konnten nicht gelesen werden: ' + s)
            return -1
        
        try:
            #Initiate group connection and test latency of connection for given group
            self.initConnection(self.opc, self.tagNames)
            self.scanInterval_limit_ms = self.minimalScnaInterval(self.opc, self.scanTestCycles)
        except Exception as e:
            self.writeError('Screen 2: Error in init connection/scaninterval: ' + str(e))
            label.config(fg='red', text=e)
            return -1
        
        label_2.config(text='Minimale Scan-Rate: ', font=('Arial', 12,'bold'))
        tmp_lab3 = self.standardLabel(self.master, '[ ' + str(int(self.scanInterval_limit_ms*1000)) + ' ms ]', 1, 2)
        tmp_lab3.config(fg='green')
        self.standardLabel(self.master, 'Aufnahme Dauer [s]: ', 0, 3)
        input_1 = self.standardEntry(self.master, 1, 3)
        self.standardLabel(self.master, 'Scan-Rate [ms]: ', 0, 4)
        input_2 = self.standardEntry(self.master, 1, 4)
        button = self.standardButton(self.master, 'Aufnahme starten', self.startRecording, 0, 5)
        button['command'] = lambda duration=input_1, scanInterval=input_2, label_config=(self.master, '', 1, 5), button_config=(self.master, '', 0, 6), lab_tags=label, lab_server=tmp_lab2 : self.startRecording(duration, scanInterval, button, label_config, button_config, lab_tags, lab_server)
        
     
    def scanOPCServer(self, listrow, listcol, label_config):
        """Scan the system for running OPC servers like KEPServerEx"""   
        
        print('Searching for OPC servers on user system')
        label = self.standardLabel(label_config[0], label_config[1], label_config[2], label_config[3])
        self.opc = OpenOPC.client()
        serverlist = self.opc.servers()
        self.serverNames.clear()
        for i in range (0, len(serverlist)):
            b = self.standardButton(self.master, serverlist[i], self.mock, i+listcol, listrow)
            b['command'] = lambda id=serverlist[i], instance=b, label_config=(self.master, '', 0,3): self.chooseServer(id, instance, label_config)
            self.serverNames.append(b)
        if(len(serverlist) > 0):
            label = self.standardLabel(label_config[0], 'Server gefunden:', label_config[2], label_config[3])
            print('Found ' + str(len(serverlist)) + ' servers: ' + str(serverlist))
        else:
            self.writeError('Scan-OPC-Server: No servers found')
            
    
    
    def chooseServer(self, id, instance, label_config):
        """Connects to the server the user clicked on""" 
          
        try: self.find_in_grid(self.master, label_config[2], label_config[3]).destroy()
        except: pass
        
        for i in range(0, len(self.serverNames)):
            self.serverNames[i].config(bg='white')
        self.serverName = id
        instance.config(bg='green')
        print('Connecting to server [' + id + ' ]')
        label = self.standardLabel(label_config[0], 'Connecting...', label_config[2], label_config[3])
        label.config(font=('Arial', 12, 'italic'))
        self.master.update()
        try:
            self.opc.connect(self.serverName)
            label.config(font=('Arial', 12, 'bold'), text='Connected', fg='green')
            print('Connection established')
        except Exception as e:
            self.writeError('Choose Server: No connection possible | ' + str(e))
            label.config(font=('Arial', 12, 'bold'), text='ERROR', fg='red')
            return -1
        label.destroy()
        label = self.standardLabel(self.master, '', 0, 3)
        label.grid(columnspan=5)
        label.config(height=1)
        self.screen_1()
    
    
    def newTag(self, channel_input, tag_input):
        """Create a new OPC tag by reading user input from GUI"""
        
        if(tag_input.get() == ''): return -1
        print('Adding new tag: ' +  str(channel_input.get()) + str(tag_input.get()))
        if(self.tagWindow == 0):
            self.tagWindow = Tk()
            self.tagWindow.title('TAGS')
        button = self.standardButton(self.tagWindow, str(channel_input.get()) + str(tag_input.get()), self.mock, 0, self.buttonID_Counter)
        button['command'] = lambda instance=button: self.removeTag(instance)
        self.addedTags.insert(self.buttonID_Counter, button)
        self.buttonID_Counter += 1
        tmp = self.standardEntry(self.master, tag_input.grid_info().get('column'), tag_input.grid_info().get('row'))
        tmp.focus_set()
            
            
    def saveTags(self, label_config):
        """Save tags to external file"""
        
        s = 'Tags\n'
        print('Saving tags')
        if(len(self.addedTags) == 0): return -1
        
        #Generate output string by putting each tag in a new row
        for i in range(0, len(self.addedTags)):
            s += str(self.addedTags[i]['text']) + '\n'
        
        f = tkFile.asksaveasfile(mode='w', defaultextension=".csv")
        if f is None:
            return -1
        f.write(s)
        
        try: self.find_in_grid(self.master, label_config[2], label_config[3]).destroy()
        except: pass
        
        label = self.standardLabel(label_config[0], 'Gespeichert', label_config[2], label_config[3])
        label.config(fg = 'green')
        self.tagWindow.focus_set()
        print('Tags saved to ' + str(f.name))
        f.close()
        
    
    def loadTags(self, channel_input, label_config):
        """Load Tags from external file, saved in separate lines
        Reading in from a exported KepServer CSV file also possible
        In that case the user has to enter the channel.device. in the GUI field as Kepware only exports tag-names"""
        
        print('Loading tags')
        fname = tkFile.askopenfilename(filetypes=((".csv", "*.csv"),
                                               ("All files", "*.*") ))
        if fname is None:
            return -1
        f = 0
        s = ''
        self.addedTags.clear()
        try: self.find_in_grid(label_config[0], label_config[2], label_config[3]).destroy()
        except: pass
        
        try:
            f = open(fname)
            s = f.read()
        except Exception as e:
            self.writeError('Load tags: Lesefehler | ' + str(e))
            label = self.standardLabel(label_config[0], 'Lesefehler', label_config[2], label_config[3])
            label.config(fg = 'red')
            self.writeError('Load-Tags: File could not be read | ' + str(e) )
            return -1
        
        try: self.tagWindow.destroy()
        except: pass
        
        self.tagWindow = Tk()
        self.tagWindow.title('TAGS')
        
        #Convert the read CSV file to a list containing all rows
        list = s.split('\n')
        if(len(list) < 1):
            self.writeError('Load-Tags: Not enough tags | ' + str(e) )
            label = self.standardLabel(label_config[0], 'Format-Fehler', label_config[2], label_config[3])
            label.config(fg = 'red')
            return -1
        
        #Create a button with unique ID for every tag over which the tag can be deleted
        self.buttonID_Counter = 0
        for i in range(1, len(list)-1):
            print(str(channel_input.get()) + str(list[i]).split(',')[0].replace('"',''))
            b = self.standardButton(self.tagWindow, str(channel_input.get()) + str(list[i]).split(',')[0].replace('"',''), self.mock, 0, self.buttonID_Counter)
            b['command'] = lambda instance=b: self.removeTag(instance)
            self.addedTags.insert(self.buttonID_Counter, b)
            self.buttonID_Counter += 1
            
        label = self.standardLabel(label_config[0], 'Eingelesen', label_config[2], label_config[3])
        label.config(fg = 'green')
        print('Tags loaded from ' + str(f.name))
        f.close()
            
     
    def testTags(self, opc, tagArray):
        """Try to read all tags independently from OPC Server to verify all are valid""" 
        
        badReads = ''
        faultyTags = []
        a = 0
        for i in range(0, len(tagArray)):
            try:
                r = opc.read(tagArray[i])
                #print(str(tagArray[i]) + '   - ' + str(r[1]) + ' - ')
            except Exception as e:
                self.writeError('Test-Tags: Reading failed | ' + str(e))
                #print('! Connection failed for tag: ' + str(tagArray[i]) + ' !')
                faultyTags.append(tagArray[i])
                badReads += str(tagArray[i]).split('.')[-1] + ', '
                if(len(badReads.split('\n')[-1]) > 40): badReads += '\n'
                
        #Remove last comma        
        if(len(badReads) > 1 and not badReads[-2] == ','): badReads = badReads[0:-3] + ' !'
        elif(len(badReads) > 1): badReads = badReads[0:-2] + ' !'
        return badReads, faultyTags
    
    
    def initConnection(self, opc, readArray):
        """Defining the opc read group to read all array values simultaneously""" 
        
        try:
            a = opc.read(readArray,group='group')
        except Exception as e:
            self.writeError('Init connection of group not possible | ' + str(e)) 
            
    def safeRecording(self, s, ext, label):
        """Opens a file dialog to chose to which file the recorded data is saved"""
        
        f = tkFile.asksaveasfile(mode='w', defaultextension=ext)
        if f is None:
            return -1
        f.write(s)
        label.config(text='Gespeichert')
        print('CSV saved to ' + str(f.name))
        f.close()
    
      
    def startRecording(self, duration_lab, scanInterval_lab, button, label_config, button_config, lab_tags, lab_server):
        """Read the values from OPC server and save them in a CSV string
        Parameter:
            Label which contains the duration
            Label which contains the scan interval
            Start button
            Label configuration to display message
            Button configuration for data saving
        Return:
            String containing the data in CSV format
        """  
    
        print('Initiating value recording')
        
        if(str(duration_lab.get()) == '' or str(scanInterval_lab.get()) == ''):
            self.writeError('Start-Recording: Felder sind leer')
            print('Empty field')
            return -1
        
        lab_aktiv = self.standardLabel(label_config[0], 'AUFNAHME AKTIV', label_config[2], label_config[3])
        lab_aktiv.config(fg='green')  
        button.config(state=DISABLED)
        
        #If scan-interval input is smaller than miniumum, set it to the minimum to prevent delays in reading
        if(int(scanInterval_lab.get()) > self.scanInterval_limit_ms*1000):
            self.scanInterval_s = float(scanInterval_lab.get())*0.001
        else:
            self.scanInterval_s = self.scanInterval_limit_ms
        print('Reading OPC values for ' + str(duration_lab.get()) + ' s with scan-interval: ' + str(self.scanInterval_s) + ' s')
        self.master.update()
        
        dbArray = self.readOPC_values(self.opc, duration_lab.get(), self.scanInterval_s, lab_aktiv, lab_tags, lab_server)
        self.opc.remove('group')
        if(len(dbArray) > 0):
            lab_aktiv.config(text='Aufnahme erfolgreich')
            print(len(dbArray))
        else:
            lab_aktiv.config(text='Aufnahme fehlgeschlagen', fg='red')
            return -1
        
        headLine = self.labelText.replace(',', ';') + '\n'
        
        #Convert array to CSV string. Format can be changed by converting array to different format
        csv = self.CSV_conversion(dbArray, headLine, self.scanInterval_s, self.addedTags)
        csv = str(csv).replace('.', ',')
        button_2 = self.standardButton(button_config[0], 'Speichern', self.mock, button_config[2], button_config[3])
        button_2['command'] = lambda s=csv, ext='.csv', label=lab_aktiv: self.safeRecording(s, ext,label)
        
        print('Recording successful: ')
        print(csv)
        
        now = datetime.datetime.now()
        self.writeToFile(csv, 'Aufnahme_' + str(now.day) + '.' + str(now.month) + '_' + str(now.hour) +
                          '-' + str(now.minute) + '-' + str(now.second) + '.csv')
        
        
        f = open('tmpSafe.csv', 'w')
        f.write(csv)
        f.close()
        
        try:
            self.displayPlot(csv)
        except:
            print('! Plotting not possible !')
        
    def exitProgram(self):
        'Exit the program'
        
        self.opc.close()
        sys.exit(0)
        
    def mock(self):
        'Mocki mack mock mock'
        
        pass
        
      
    def removeTag(self, instance):
        """Remove a Tag thats clicked on""" 
        
        print('Removing tag: ' + str(instance['text']))
        self.addedTags.remove(instance)
        self.buttonID_Counter -= 1
        if(len(self.addedTags) == 0):
            self.tagWindow.destroy()
            self.tagWindow = 0
            return 0
        instance.destroy()
     
              
    def stopRecording(self):
        """ Stops the recording of data if the "stop" button is pressed"""
        
        self.stopRec = 1
              
    
    def readOPC_values(self, opc, recordingTime_s, scanInterval_s, lab_aktiv, lab_tags, lab_server):
        """Read values over the initiated OPC connection""" 
        
        dataBank = []
        startTime = time.time()
        #Make it possible to change color of progressbar
        s = ttk.Style()
        s.theme_use('default')
        s.configure("Horizontal.TProgressbar", troughcolor = 'white', background='green')
        p = ttk.Progressbar(self.master, style="Horizontal.TProgressbar", orient="horizontal",
                                        length=200, mode="determinate")
        p.grid(column=1,row=6)
        permanent = 0
        countMax = 0
        stopButton = 0
        writeInterval = 3600
        #Process the input-field
        if(str(recordingTime_s.split('.')[0]) == 'u'):
            permanent = 1
            p.destroy()
            stopButton = self.standardButton(self.master, 'Aufnahme Stoppen', self.stopRecording, 1, 6)
            stopButton.config(fg='red')
            try: writeInterval = int(recordingTime_s.split('.')[1])
            except: pass
            try: 
                if(str(recordingTime_s.split('.')[2]) == 'c'):
                    self.folderName = tkFile.askdirectory() + '/'
            except: pass
        else:
            stopButton = self.standardButton(self.master, 'Aufnahme Stoppen', self.stopRecording, 0, 6)
            stopButton.config(fg='red')
            try: recordingTime_s = int(scanInterval_s) + int(recordingTime_s)
            except: return -1
            countMax = int(int(recordingTime_s) / scanInterval_s)
        count = 0
        
        print('Recieving data ...')
        exceptOccured = 0
        exceptCount = 0
        retryCount = 0
        retryNec = 0
        unique = 0
        while((count < countMax or permanent == 1) and self.stopRec == 0):
            #Loading bar
            if(permanent == 0): p.config(value=int(count/countMax*100))
            
            #If recording is indefinitely, write out file in writeInterval 
            elif(count > writeInterval/scanInterval_s): 
                now = datetime.datetime.now()
                self.writeToFile(self.CSV_conversion(dataBank, self.labelText.replace(',', ';') + '\n',  
                                                     scanInterval_s, self.addedTags), str(self.folderName) + 'Aufnahme_' + str(now.day) + 
                                                     '.' + str(now.month) + '_' + str(now.hour) + '-' + str(now.minute) +
                                                     '-' + str(now.second) + '.csv')
                count = 0
                dataBank.clear()
                self.recordingErrors.clear()
                startTime = time.time()
                print('Saved to file')
            self.master.update()
            
            try:
                reading = opc.read(group='group')
                
                #If not all tags are currently read, periodically try to re-read the excluded tags
                if(retryNec == 1):
                    retryCount += 1
                    if(retryCount > 30):
                        ret = self.analyseFaultyTags(opc, lab_tags)
                        #If now all tags could be read
                        if(ret == -1): 
                            retryNec = 0
                            print('Origin restored')
                            if(permanent== 0): s.configure("Horizontal.TProgressbar", background='green')
                            self.master.update()
                            excludedTags = self.recordingErrors.append((count, []))
                        else:
                            self.recordingErrors.append((count,excludedTags))
            
            #If one or more values could not be read
            except Exception as e:
                exceptCount += 1
                
                #Append empty field as no value was read if exception ocured
                dataBank.append([])
                
                #If exception occured for the first time
                if(exceptOccured == 0):
                    exceptOccured = 1
                    if(permanent== 0): s.configure("Horizontal.TProgressbar", background='orange')
                    self.master.update()
                    
                if(exceptCount == 2):
                    excludedTags = self.analyseFaultyTags(opc, lab_tags)
                    if(not excludedTags == -1):
                        self.recordingErrors.append((count,excludedTags))
                    retryNec = 1
                    exceptCount = 0
                    
                else:
                    try:
                        #Pause program to ensure scan-interval is kept
                        time.sleep(float(count) * scanInterval_s  - (time.time() - startTime))
                    except ValueError:
                        print('Transfer-Period to slow for Scan-Interval')
                        print('Offset: ' + str(float(count) * scanInterval_s  - (time.time() - startTime)) + ' [s]')
                count += 1
                continue
            
            if(not exceptOccured == 0):
                print('Exception corrected')
                exceptOccured = 0
                if(permanent== 0): 
                    try: s.configure("Horizontal.TProgressbar", background='green')
                    except: pass
                    
            dataBank.append(reading)
            count += 1
            
            try:
                #Pause program to ensure scan-interval is kept
                time.sleep(float(count) * scanInterval_s  - (time.time() - startTime))
            except ValueError:
                print('Transfer-Period to slow for Scan-Interval')
                print('Offset: ' + str(float(count) * scanInterval_s  - (time.time() - startTime)) + ' [s]')
                
        if(exceptOccured == 1): self.writeError('Some tags could not be read during recording: ')
        if(permanent == 0): p.config(value=100)
        else: stopButton.destroy()
        return dataBank
        
     
    def analyseFaultyTags(self, opc, lab_tags):
        '''This function finds faulty tags and removes them while adding tags that could previously not be read
        but are now reachable again'''
        
        try: self.opc.info()
        except:
            try: opc.close()
            except: pass
            try: opc.connect(self.serverName)
            except: pass
        _, faultyTags = self.testTags(self.opc, self.tagNames)
        if(len(faultyTags) == 0): 
            self.initConnection(opc, self.tagNames)
            lab_tags.config(text='[ ' + str(self.labelText_formated) + ' ]')
            return -1
        newTags = []
        newTags = self.tagNames.copy()
        for i in range(0, len(faultyTags)):
            newTags.remove(faultyTags[i])
            try:
                lab_tags.config(text=lab_tags['text'].replace((str(faultyTags[i].split('.')[-1]) + ','), ''))
                lab_tags.config(text=lab_tags['text'].replace((str(faultyTags[i].split('.')[-1])), ''))
            except:
                print('exc')
                pass
        opc.remove('group')
        #print('New tags: ' + str(newTags))
        self.master.update()
        self.initConnection(opc, newTags)
        return faultyTags
             
         
         
    def minimalScnaInterval(self, opc, cycles):
        """Read data over the opc connection to test its latency, including latency of array access
            Parameter:
            opc - OpenOPC object
            cycles - Number of data transfers conducted to find maximal latency
            Return: 
            Maximal measured latency * 3 to ensure a latency buffer"""  
            
        maxTime = 0.0
        dataBank = []
        for i in range (0,cycles):
            st = time.time()
            read = opc.read(group='group')
            dataBank.append(read)
            tmp = time.time() - st
            if(maxTime < tmp):
                maxTime = tmp
        print('Largest measured connection delay: ' + str(maxTime))
        #Return 3*maxTime to ensure a buffer
        return maxTime*3
    
    
    def arrayPrep(self, dataBank):
        """Prepares the recorded data array to be converted to CSV format
        Set a csvNode every time an error occurred or was corrected as 
        the length of the array changes on those cases"""
        
        tagInd = []
        csvNodes = []
        for i in range(0,len(self.tagNames)):
            tagInd.append(str(i))
        csvNodes.append((0,tagInd))
        
        for i in range(0, len(self.recordingErrors)):
            tagI = tagInd.copy()
            for j in range(0,len(self.recordingErrors[i][1])):
                tagI.remove(str(self.tagNames.index(self.recordingErrors[i][1][j])))
            csvNodes.append((self.recordingErrors[i][0], tagI))
        csvNodes.append((len(dataBank), tagInd))
        return csvNodes
        
    
    
    def CSV_conversion(self, dataBank, csvString, scanInterval_s, tagNames):
        """Convert data array to CSV format while replacing data points that could not be read with 0
        x is row, y is column, inside every cell is a tuple"""
        
        csvNodes = self.arrayPrep(dataBank)
        s = csvString
        counter = 0
        #Each csvNode contains information about which of the data points could not be read for n cycles.
        for i in range(0,len(csvNodes)-1):
            for x in range(csvNodes[i][0], csvNodes[i+1][0]):
                skipedRows = 0
                s += str(round(counter*scanInterval_s,2)) + ';'
                try:
                    for y in range(0, len(self.tagNames)):
                        #If only a single exception occurred, insert value of previous transition
                        if(len(dataBank[x]) == 0 and len(dataBank[x-1]) == len(self.tagNames) and x > 0):
                            s += str(dataBank[x-1][y][1]) + ';'
                            continue
                        elif(csvNodes[i][1].__contains__(str(y))):
                            try: 
                                if(int(dataBank[x][y-skipedRows][1]) > 4000000000):
                                    s += '-2;'
                                    continue
                            except: pass
                            s += str(dataBank[x][y-skipedRows][1]) + ';'
                        else:
                            skipedRows += 1
                            s += '-1;'
                    s = s[:-1] + '\n'
                except: pass
                counter += 1
        
        return s
    
    
    def writeToFile(self, csvString, fileName):
        """Write string in CSV format to external file"""
        
        f = open(fileName, 'w')
        f.write(csvString)
        f.close()
      
        
    def displayPlot(self, csv):
        """Displays the recorded OPC Data as a matplotlib plot, using csv string"""
        
        print('Displaying plot of data')
        rows = csv.replace(',', '.').split('\n')
        rows = rows[1:-1]
        colums = []
        for i in range (0,str(rows[0]).count(';') + 1):
            colums.append([])
        for i in range (0, len(colums)):
            colums[i] = []
        matrix = []
        floatMatrix = []
        
        #Creating Matrix from data
        for i in range (0, len(rows)):
            matrix.append([])
            floatMatrix.append([])
            tmp = str(rows[i]).split(';')
            for j in range (0, len(colums)):
                try:
                    colums[j].append(tmp[j])
                    #matrix[i][j] = float(tmp[j])
                    matrix[i].append(tmp[j])
                    floatMatrix[i].append(0.0)
                except:
                    print('A CSV FAULT (WRONG VALUE AMOUNT) OCCURED AT ROW ' + str(i) + ' COULUMN ' +str(j))
        
        #Create a matrix containing the float values
        for x in range (0, len(floatMatrix)):
            for y in range (0, len(floatMatrix[0])):
                try:
                    floatMatrix[x][y] = float(matrix[x][y])
                except:
                    continue
        
        npMatrix = np.array(floatMatrix)
        for i in range (0, len(npMatrix[0])-1):
            plt.plot(npMatrix[:,0], npMatrix[:,i+1])
        plt.xlabel('Zeit [s]')
        plt.ylabel('Wert')
        plt.title('OPC Data')
        plt.show()
    
    
    def writeError(self, error):
        """Write error message to external error-log file"""
        
        s = ''
        #If file exists, read it
        try:
            f = open('Error-log.txt' , 'r')
            s = str(f.read())
            s += str(error) + '\n'
            f.close()
        except:
            pass
        f = open('Error-log.txt' , 'w')
        f.write(s)
        f.close() 
    
        
    def find_in_grid(master, column, row):
        """Find an element (like a label) in master grid and return it"""  
        
        for child in master.children.values():
            info = child.grid_info()                                                                        
            if info['row'] == str(row) and info['column'] == str(column):
                return child
        return None
    
            
    def standardEntry(self, master, co, ro):
        """Define standard tkinter-Entry format"""
        
        entry = Entry(master, font=("MS Sans Serif", 12), width=25, borderwidth=2, relief="groove")
        entry.grid(column=co, row=ro)
        return entry
    
       
    def standardLabel(self, master, textField, co, ro):
        """Define standard tkinter-Label format"""
        
        lab = Label(master,bg="white", text=textField, font=('Arial', 12, 'bold'))
        lab.grid(column=co, row=ro)
        return lab
    
       
    def standardButton(self, master, textField, com, co, ro):
        """Define standard tkinter-Button format"""
        
        button = Button(master, text=textField, font=('Arial', 12), width=25, height=1,bg="white",borderwidth=4, relief="groove", command=com)
        button.grid(column=co, row=ro)
        return button
    
if __name__ == "__main__":
    'Main function of program'
    
    d = OPC_Reader()
    