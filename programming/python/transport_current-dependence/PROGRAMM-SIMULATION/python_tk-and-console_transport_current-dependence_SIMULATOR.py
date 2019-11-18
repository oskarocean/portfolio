
# based on:
# https://www.quora.com/How-do-I-create-a-real-time-plot-with-matplotlib-and-Tkinter
# https://learn.sparkfun.com/tutorials/graph-sensor-data-with-python-and-matplotlib/update-a-graph-in-real-time

from tkinter import * # library for a simple window widget
# import visa # library for instrument communication

### libraries for time and "scheduling"
import time
import threading

### import plot library and extras for realtime plotting with TK widget
import matplotlib.pyplot as plt
import matplotlib.animation as animation # nessecary for continious plotting
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import math
import random

################################################################################
################# Function definition ##########################################
################################################################################

def removeNumbersWithToSmallStepInBetween(n): # remove voltage values which can not be resolved by Lock-in
    remover=1
    removed=0

    while remover <=len(voltageLOGARRAY):
        if voltageLOGARRAY[remover]-voltageLOGARRAY[remover-1]<n:
            voltageLOGARRAY.pop(remover)
            remover+=1
        else:
            remover+=1

        if remover+removed==len(voltageLOGARRAY):
            break

def LockinSetVoltage(): # set the ac output voltage of Lock-in for current generation
    global voltageLOGARRAY
    global voltageCOUNTER
    currentVOLTAGE=voltageLOGARRAY[voltageCOUNTER-1]# ask for the current ac output voltage
    if currentVOLTAGE==voltageLOGARRAY[voltageCOUNTER]: # fail safe: if current voltage already equals the voltage which has to be set
        print("Voltage already set!\n") # user information: voltage already valid
        if voltageCOUNTER!=len(voltageLOGARRAY): # if not the last voltage value to be set
            voltageCOUNTER+=1 # advance the preset for the next voltage set cycle (but do not set the new voltage!)
    else: # if current voltage does not equal to voltage which has to be set
        print("Set new voltage...")# user information: going to set new voltage
        while currentVOLTAGE!=voltageLOGARRAY[voltageCOUNTER]: # As long as current voltage does not equal target
            currentVOLTAGETESTER=voltageLOGARRAY[voltageCOUNTER-1]# check current voltage
            if currentVOLTAGETESTER<voltageLOGARRAY[voltageCOUNTER]: # if current voltage is lower
                helperVOLTAGE=currentVOLTAGETESTER+0.002 # add to new output voltage preset
            if currentVOLTAGETESTER>voltageLOGARRAY[voltageCOUNTER]: # if current voltage is higher
                helperVOLTAGE=currentVOLTAGETESTER-0.002 # substract from new output voltage preset
            currentVOLTAGETESTER=voltageLOGARRAY[voltageCOUNTER] # check output voltage again
            if float(currentVOLTAGETESTER)==float(voltageLOGARRAY[voltageCOUNTER]): # if current voltage equals target voltage
                if voltageCOUNTER!=len(voltageLOGARRAY):# and more voltages to apply
                    if voltageCOUNTER<len(voltageLOGARRAY)-1: # if not the penultimate voltage to measure
                        voltageCOUNTER+=1 # advance voltage preset (but do not go to new voltage!); user info with remark for next voltage
                        print("New voltage set! Paramters: voltageCOUNTER: ",voltageCOUNTER,", Voltage (current): ",currentVOLTAGETESTER,"V, Voltage (target): ", voltageLOGARRAY[voltageCOUNTER-1],"V, Voltage (next): ", voltageLOGARRAY[voltageCOUNTER]," V")
                    else: # if last voltage to measure
                        voltageCOUNTER+=1 # advance voltage preset (but do not go to new voltage!); user info with remark that this is the last voltage
                        print("New voltage set! \n Paramters: voltageCOUNTER: ",voltageCOUNTER,", Voltage (current): ",currentVOLTAGETESTER,"V, Voltage (target): ", voltageLOGARRAY[voltageCOUNTER-1],"V, no new voltage (last voltage of set!)")
                    break
                else: # if current voltage is the last one to measure
                    print("Reached last value!\n")# user info: last value to measure
                    break # quit while loop
            else: # if current voltage does not equal target voltage
                continue # run through the loop another time

def DataAcquisition(): # print user information about data acquisition and aquire/save data
    global voltageLOGARRAY
    global voltageCOUNTER
    global lockin1valueARRAY
    global lockin2valueARRAY
    global lockin3valueARRAY
    global lockin1
    global lockin2
    global lockin3
    global timestamp
    global timestr

    print("measuring...")

    # aquire data
    lockin1valueARRAY=[random.randrange(0,10),random.randrange(0,20),random.randrange(0,30),random.randrange(0,40)]
    lockin2valueARRAY=[random.randrange(0,10),random.randrange(0,20),random.randrange(0,30),random.randrange(0,40)]
    lockin3valueARRAY=[random.randrange(0,10),random.randrange(0,20),random.randrange(0,30),random.randrange(0,40)]

    # open file, write values to file, close file
    fobj_out = open("Lock-in-values_"+timestr+".vpp","a") # open the file where data should be saved
    fobj_out.write(
                    str(timestamp/20)
                    +'\t'+
                    str(voltageLOGARRAY[voltageCOUNTER])
                    +'\t'+
                    str(lockin1valueARRAY[0])
                    +'\t'+
                    str(lockin1valueARRAY[1])
                    +'\t'+
                    str(lockin1valueARRAY[2])
                    +'\t'+
                    str(lockin1valueARRAY[3])
                    +'\t'+
                    str(lockin2valueARRAY[0])
                    +'\t'+
                    str(lockin2valueARRAY[1])
                    +'\t'+
                    str(lockin2valueARRAY[2])
                    +'\t'+
                    str(lockin2valueARRAY[3])
                    +'\t'+
                    str(lockin3valueARRAY[0])
                    +'\t'+
                    str(lockin3valueARRAY[1])
                    +'\t'+
                    str(lockin3valueARRAY[2])
                    +'\t'+
                    str(lockin3valueARRAY[3])
                    +'\n'
                    ) # write timestamp and Lock in values separated by tab
    fobj_out.close() # close the file (security measure: if program crashes, less likely that rest of file is destroyed)
    print("Sucessfully measured and appended to file: ",voltageLOGARRAY[voltageCOUNTER-1]," V\n")

################################################################################
############### important variables for measuring ##############################
################################################################################

voltageMAX=1
stepPerDecade=10
ramptime=300

################################################################################
################# Initialize voltage array  ####################################
################################################################################



step=100 # defines the time between animation frames and therefor the measurement point density
timestamp=0


global timestr
timestr = time.strftime("%Y%m%d-%H%M%S") # get actual system time

# set safety parameters to prevent exceeding critical values/limits of Lock-in
if voltageMAX>5:
    maxvalue=5
else:
    maxvalue=voltageMAX

voltageCOUNTER=0 # counter for current position in voltageARRAY; allwos to chose next frequency
voltageLOGHELPERARRAY1=np.logspace(0,1, num=stepPerDecade) # generate log distance

voltageLOGHELPERARRAY2=[0.01,0.1,1] # use these values as a starting point

voltageLOGARRAY=[] # array to store voltage values

for i in range(0,len(voltageLOGHELPERARRAY2)): # multiply the two helper arrays to get all the voltage values that have to be measured
    for j in range(0,len(voltageLOGHELPERARRAY1)):
        if voltageLOGHELPERARRAY2[i]*voltageLOGHELPERARRAY1[j]<=maxvalue: # and append them to array if they are smaller then 5.000
            voltageLOGARRAY.append(round(voltageLOGHELPERARRAY2[i]*voltageLOGHELPERARRAY1[j],3))

removeNumbersWithToSmallStepInBetween(0.002)# remove numbers with too small step
removeNumbersWithToSmallStepInBetween(0.002)# two times, to be sure nothing is left over

# round voltage values to fit steps/possible values of Lock-in
for i in range(0, len(voltageLOGARRAY)):
    if (voltageLOGARRAY[i]*1000)%2!=0:
        voltageLOGARRAY[i]+=0.001
    voltageLOGARRAY[i]=round(voltageLOGARRAY[i],3)

lockin1valueARRAY=[]
lockin2valueARRAY=[]
lockin3valueARRAY=[]

################################################################################
################# Initialize instruments #######################################
################################################################################

lockin1=0
lockin2=0
lockin3=0

################################################################################
################# Begin of class and function declaration ######################
################################################################################

# function definition of the application
def app():
    # initialise a window.
    root = Tk()
    root.title("Locknar RampDatResistance V.0.0.1 - Record a current characteristic with SRS830's (Lock-in 1,2,3 @ Laser 7)")
    root.config(background='white')

    # print user information and initalize Lock-ins
    print("This is Locknar RampDatResistance V.0.0.1 Script: Record a current characteristic with SRS830's (Lock-in 1,2,3 @ Laser 7)")
    print("There will be ",len(voltageLOGARRAY)," points measured:\n", voltageLOGARRAY,"\n\n")
    print("Initialize...")
    print("Lock-ins are now set to GPIB-Operation!\n\n")

    # nessecary settings for saving the data
##    timestr = time.strftime("%Y%m%d-%H%M%S") # get actual date/time
    print("Create blank output file...")
    fobj_out = open("Lock-in-values_"+timestr+".vpp","a") # open file in append mode with name Lock-in-values_DATEANDTIME.txt
    fobj_out.write("time (s)\t SineVoltage "
                   +"\t Loc.1:X \t Loc.1:Y \t Loc.1:R \t Loc.1:Theta \t Loc.2:X \t Loc.2:Y \t Loc.2:R \t Loc.2:Theta \t Loc.3:X \t Loc.3:Y \t Loc.3:R \t Loc.3:Theta \n") # append header with measurement details to file
    fobj_out.close() # close file
    print("Output file created!\n\n")

    fig = Figure() #initialise main plot construct
    fig,ax1 = plt.subplots() # allow subplots
    ax2 = ax1.twinx() # initalise second, independ axis with shared x-axis in fig

    # initialise arrays for plot value storage
    xs = []
    y1s = []
    y2s = []
    zs = []

##    # define function for plot animation/measurement point acquisition
    def animate(
                    i,
                    xs,
                    y1s,
                    y2s,
                    zs,
                    lockin1,
                    lockin2,
                    lockin3
            ):
        global voltageCOUNTER
        global voltageLOGARRAY
        global lockin1valueARRAY
        global lockin2valueARRAY
        global lockin3valueARRAY
        global timestamp

        ########################################################################
        ## clock divider to ensure proper waiting time between measurements ####
        ########################################################################
        if timestamp==0: # if no inital measurement performed
            LockinSetVoltage()# set the Lock-in output voltage
        else:
            if math.fmod(timestamp,20)==0:
                time.sleep(1.5*ramptime/2000)

                if (voltageCOUNTER!=len(voltageLOGARRAY)):
                    DataAcquisition()# start to record data

                # clear old data from plot axis
                ax1.clear()
                ax2.clear()

                # append measured values to plot arrays
                xs.append(i)
                y1s.append(lockin2valueARRAY[0])
                y2s.append(lockin3valueARRAY[0])
                zs.append(lockin1valueARRAY[0])

                ax2.plot(xs, y1s, 'blue', zorder=10) # plot the data
                ax2.plot(xs, y2s, 'cyan', zorder=1) # plot the data
                ax2.set_ylabel('voltage', color='b') # set the frequency label and its color

                ax1.plot(xs, zs,'#f87a43', zorder=1) # plot the absolute value of signal (Lock-in R)
                ax1.set_ylabel('current', color='#f87a43') # set the absolute value of signal (Lock-in R) label and its color
                ax1.set_xlabel('time (s)') # set x-axis label

                # Format plot
                plt.xticks(rotation=90, ha='right')

                ################################################################
                ########## logic for proceeding/aborting measurement ###########
                ################################################################
                if voltageCOUNTER!=len(voltageLOGARRAY): # if not last voltage entry
                    time.sleep(ramptime/3000) # wait
                    LockinSetVoltage() # set new driving voltage (converted to current by external resistor)
                    time.sleep(4*ramptime/3000)# wait
                else: # if no more voltage entries left to measure
                    # print user information and add safety delay
                    print("Measurement finished sucessfully!\n")
                    time.sleep(ramptime/3000)
                    print("Starting ramp down")
                    time.sleep(ramptime/3000)
                    print("Ramping... Please wait ...\n\n")
                    currentVOLTAGE=voltageLOGARRAY[len(voltageLOGARRAY)-1]
                    while True: # starting voltage rampdown
                        print("Voltage now at minimum. Script will now terminate. Bye!")# print user information
                        exit()


        timestamp+=1# progress program timestamp


    graph = FigureCanvasTkAgg(fig, master=root) # set up the graph in the window
    graph.get_tk_widget().pack(side="top",fill='both',expand=True) # define the position and behavior of the graph

    ani = animation.FuncAnimation(
                                  fig,
                                  animate,
                                  fargs=(
                                            xs,
                                            y1s,
                                            y2s,
                                            zs,
                                            lockin1,
                                            lockin2,
                                            lockin3
                                        ),
                                  interval=step
                                  ) # start the plot animation and therewith the measurement
    fig.tight_layout() # activate space saving layout for plot

    root.mainloop() # go into the tkinter mainloop

################################################################################
################# End of class and function declaration ########################
################################################################################

# start the graphical application
if __name__ == '__main__':
    app()
