# SPDX-FileCopyrightText: 2023 Jim McKeown
# SPDX-License-Identifier: MIT

"""
This example shows the basic functionality to:
Show the devices fingerprint slots that have fingerprints enrolled.
Enroll a fingerprint in an existing or new fingerprint slot.
Try to find a fingerprint in the existing list of enrolled fingerprints.
Delete an enrolled fingerprint.
View the image of a fingerprint.
Preview the image of a fingerprint and then try to find the fingerprint
in the existing list of enrolled fingerprints.

Please note that this example only works on single board computers
with the use of Blinka.

This example is based on fingerprint_simpletest.py
"""

import time
import numpy as np
from matplotlib import pyplot as plt
import serial
import yubiyomi

# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT

# This has not been tested:
# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
# Edit ttyACM0 to your USB/serial port
uart = serial.Serial("COM4", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = yubiyomi.Yubiyomi(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != yubiyomi.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != yubiyomi.OK:
        return False
    print("Searching...")
    if finger.finger_search() != yubiyomi.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == yubiyomi.OK:
        print("Image taken")
    else:
        if i == yubiyomi.NOFINGER:
            print("No finger detected")
        elif i == yubiyomi.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == yubiyomi.OK:
        print("Templated")
    else:
        if i == yubiyomi.IMAGEMESS:
            print("Image too messy")
        elif i == yubiyomi.FEATUREFAIL:
            print("Could not identify features")
        elif i == yubiyomi.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == yubiyomi.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == yubiyomi.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


def get_fingerprint_photo():
    """Get and show fingerprint image"""
    print("Waiting for image...")
    while finger.get_image() != yubiyomi.OK:
        pass
    print("Got image...Transferring image data...")
    imgList = finger.get_fpdata("image", 2)
    imgArray = np.zeros(73728, np.uint8)
    for i, val in enumerate(imgList):
        imgArray[(i * 2)] = val & 240
        imgArray[(i * 2) + 1] = (val & 15) * 16
    imgArray = np.reshape(imgArray, (288, 256))
    plt.title("Fingerprint Image")
    plt.imshow(imgArray)
    plt.show(block=False)


def get_fingerprint_preview():
    """Get a finger print image, show it, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != yubiyomi.OK:
        pass
    print("Got image...Transferring image data...")
    imgList = finger.get_fpdata("image", 2)
    imgArray = np.zeros(73728, np.uint8)
    for i, val in enumerate(imgList):
        imgArray[(i * 2)] = val & 240
        imgArray[(i * 2) + 1] = (val & 15) * 16
    imgArray = np.reshape(imgArray, (288, 256))
    plt.title("Fingerprint Image")
    plt.imshow(imgArray)
    plt.show(block=False)
    print("Templating...")
    if finger.image_2_tz(1) != yubiyomi.OK:
        return False
    print("Searching...")
    if finger.finger_search() != yubiyomi.OK:
        return False
    return True


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == yubiyomi.OK:
                print("Image taken")
                break
            if i == yubiyomi.NOFINGER:
                print(".", end="")
            elif i == yubiyomi.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == yubiyomi.OK:
            print("Templated")
        else:
            if i == yubiyomi.IMAGEMESS:
                print("Image too messy")
            elif i == yubiyomi.FEATUREFAIL:
                print("Could not identify features")
            elif i == yubiyomi.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            #print("Remove finger")
            print("Taking second image soon")
            time.sleep(1)
            #while i != yubiyomi.NOFINGER:
            #    i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == yubiyomi.OK:
        print("Created")
    else:
        if i == yubiyomi.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == yubiyomi.OK:
        print("Stored")
    else:
        if i == yubiyomi.BADLOCATION:
            print("Bad storage location")
        elif i == yubiyomi.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != yubiyomi.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("v) view print")
    print("p) preview and find print")
    print("----------------")
    c = input("> ")

    if c == "e":
        m = max(finger.templates)
        enrostart = m + 1
        enroend = m + 6
        print(f"Max is {m} -> Enrolling 5 prints -> {enrostart} : {enroend}")
        for i in range(enrostart, enroend + 1):
            while not enroll_finger(i):
                pass
        print("enrolled finger 5 times")
    if c == "f":
        found = False
        for i in range(1, 11):
            if get_fingerprint():
                print(i, " Detected #", finger.finger_id, "with confidence", finger.confidence)
                found = True
                break
        if not found:
            print("Finger not found")
    if c == "d":
        if finger.delete_model(get_num()) == yubiyomi.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
    if c == "v":
        get_fingerprint_photo()
    if c == "p":
        if get_fingerprint_preview():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger not found")