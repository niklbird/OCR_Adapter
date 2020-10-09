
**OCR Adapter**
-----------------
This software presents a small code framework to ease the reading of data from an OPC server. 
It is based on the library OpenOPC (<http://openopc.sourceforge.net/>).
The software has multiple settings regarding the reading of data, including an adjustable data rate.
Furthermore it is able to record data received over OPC for a set amount of time and save it locally as a CSV file.

The program was developed as an addition to the software KEPServerEX 6, however using it with other OPC servers should be possible.

KEPServer does not offer the feature of saving data in an easy and fast way. 
This software solves this problem by using KEPServer as middleware to receive the data and then saving it in CSV format.

It was used to read data from Programmable Logic Controllers by Siemens and Omron. 
In this use case KEPServerEX 6 was used to communicate with the PLCs, simultaneously running the adapter software to read the data directly from KEPServer and saving it locally.
It is not intended for long term data capturing but rather to record short batch processes. 

**Installation**
Python is required to run the software which can be installed from <https://www.python.org/downloads/>.
Furthermore some python libraries are required:
- OpenOPC: pip install OpenOPC 
- Numpy: pip install numpy
- Matplotlib: pip install matplotlib
- OpenCV: pip install opencv-python

The software does not work with Python 3 yet since the OpenOPC library is not yet fully functional with Python 3.

If the software is intended to be used to read data from a PLC, KEPServerEx 6 can be used to communicate with the PLC: <https://www.kepware.com/de-de/products/kepserverex/version-6/>
KEPServer has a free version that can be used for a proof of concept.

**Running the program**
The usage of the software should be straight forward. 
Start the OPC server you want to read data from, then click "Search Server". 
The server should now show up and you can click on it to chose it.
You can now add the Tags that should be read from the server. 
A pattern can be used, as well as manually putting in the entire name.
The Tag list can be stored / loaded.
If a Tag has been misspelled it can be removed by clicking on it.

Now "Next" can be clicked.
The program will try to read all input Tags and display an error message if a tag could not be read.
The user can now input a duration and a scan-intervall for the tags.
To set the duration to infinity (Record until stopped) input a "u" in the field.
A write-out intervall can also be set. 
To set a write-out intervall put a point after the u, followed by the time in seconds.
E.g. to write out data once a minute, input u.60 into the field.
Additionally a write-out location can be chosen by adding a .c to the field.
E.g. u.60.c
While the connection is active, values are continuously read by the software.
If a tag can not be read for a while, it disappears from the tag list. 
After the reading is possible again, it appears again.
The loading bar will change color if one or more reading errors occurred.
After the recording is finished the values can be saved into a CSV file.

TIPP: KEPServer will not refresh the tags if they are read by external software, i.e. a manually input scan-intervall is required for each tag.

**Disclaimer**
The Software was developed as a fast solution to collect data from Programmable Logic Controllers.
I do not take any responsibility about the correctness of the collected data. 
The programm is intended to be used as a tool to create a proof of concept / read some values from an OPC server without large effort. 
Since I developed it during an internship I do not have the resources to test for bugs in context of PLCs anymore. 
However if a bug in the general working of the program is found I will try my best to fix it.

At last I want to thank the Umicore AG Hanau and the department I worked at for allowing me to make the program open-source.  


