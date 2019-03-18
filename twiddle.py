#!/usr/bin/python3

# imports
import _thread
import spidev
import time as time
from array import *
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import atexit

# Define Variables
log = []
direction = []
Progress = True
SW1 = 11
L1 = 13
L2 = 15
RED = True
GREEN = False
# Create SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000  # setting the maximum frequency of the spi


GPIO.setmode(GPIO.BOARD)
def exit_handler():
    print("Cleaning up")
    GPIO.cleanup()


atexit.register(exit_handler)



def readadc(adcnum):
    # read SPI data from the MCP3008, 8 channels in total
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


def evaluateDirection(initpotvalue, secondarypotvalue):
    if secondarypotvalue < initpotvalue:
        d = 'L'
    elif secondarypotvalue > initpotvalue:
        d = 'R'
    return d

def readCombination():
    global Progress
    Potvalue = readPot()
    knobTimeStart = 0
    direction = ""
    i = 0
    # _thread.start_new_thread(stop,())
    while Progress:
        global_time = time.time()
        while (sameValue(Potvalue, readPot()) and i == 0):
            if (time.time() - global_time >= 3):
                print("3 sec over")
                return
        newTempPotValue = readPot()
        if not (sameValue(Potvalue, newTempPotValue)) and i == 0:
            print("Time Started")
            knobTimeStart = time.time()
            direction = evaluateDirection(Potvalue, newTempPotValue)
            i = i + 1
            # print(direction)
        elif sameValue(Potvalue, newTempPotValue):
            time_start = time.time()
            while (sameValue(Potvalue, readPot())):
                # you know combination is to be recorded
                time_current = time.time()
                delta_t = time_current - time_start
                if (delta_t >= 2):
                    duration = time.time() - delta_t - knobTimeStart
                    recordData(direction, duration)
                    i = 0
                    print("Value is recorded")
                    # print (direction + str(duration))
                    break
        Potvalue = readPot()


def sameValue(initpotvalue, secondarypotvalue):
    same = False
    for i in range(-10, 10):
        if secondarypotvalue + i == initpotvalue:
            same = True
            break
    return same


def recordData(direct, time):
    global log
    global direction
    log.append(time)
    direction.append(direct)
    # print(direct+str(time))


def printData():
    global log
    global direction
    for i in range(len(log)):
        print(direction[i] + str(log[i]))


def sort(arr):
    for i in range(len(arr)):
        min = arr[i];
        minindex = i;
        for j in range(i + 1, len(arr)):
            if arr[j] < min:
                min = arr[j]
                minindex = j
        temp = arr[i];
        arr[i] = min;
        arr[minindex] = temp;


def evaluateCombination(mode, ComboDir, ComboDuration):
    global log
    global direction
    if len(log) != len(ComboDuration):
        print("Wrong Password")
        return False
    Correct = True
    # secureMode
    if (mode == 1):
        for i in range(len(log)):
            if not (direction[i] == ComboDir[i] and durationEquality(log[i], ComboDuration[i])):
                print("Wrong Password")
                Correct = False
                break
        if Correct:
            print("Code Correct")
            SwapLED()
    # UnsecureMode
    else:
        sort(log)
        sort(ComboDuration)
        print(log)
        print(ComboDuration)
        for i in range(len(log)):
            if not (durationEquality(log[i], ComboDuration[i])):
                print("Wrong Password")
                Correct = False
                break
        if Correct:
            print("Code Correct")
            SwapLED()


def durationEquality(recorded, expected):
    TLevel = 1
    if (expected - TLevel < recorded < expected + TLevel):
        return True
    else:
        return False


def readPot():
    pot_reading = readadc(0)
    delay()
    return pot_reading


def ResetValue():
    global log
    global direction
    log = []
    direction = []


def SwitchGreenLED():
    global L2
    global L1
    GPIO.output(L2, GPIO.HIGH)
    GPIO.output(L1, GPIO.LOW)


def SwitchRedLED():
    global L2
    global L1
    GPIO.output(L1, GPIO.HIGH)
    GPIO.output(L2, GPIO.LOW)


def SwapLED():
    global RED
    global GREEN
    if RED:
        SwitchGreenLED()
    else:
        SwitchRedLED()


def main():
    global log
    global direction
    global SW1
    global L1
    global L2
    global RED
    global GREEN
    GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    comboDir = ["L", "R"]
    comboLog = [2, 2]
    SwitchRedLED()
    while True:
        print("Waiting PushButton S")
        while (GPIO.input(SW1)):
            pass
        print("pressed")
        readCombination()
        evaluateCombination(1, comboDir, comboLog)
        print("Combo Direction")
        print(comboDir)
        print("Recorded Direction")
        print(direction)
        print("Combo Duration")
        print(comboLog)
        print("Recorded Duration")
        print(log)
        print()
        print()
        ResetValue()
        # print(readPot())
if __name__ == "__main__": main()
