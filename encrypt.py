#!/usr/bin/env python
# coding=UTF-8
import cv
import sys

class SteganographyException(Exception):
    pass

class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.width = im.width
        self.height = im.height
        self.size = self.width * self.height
        self.nbchannels = im.channels

        self.maskONEValues = [1,2,4,8,16,32,64,128]
        self.maskONE = self.maskONEValues.pop(0)

        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        self.maskZERO = self.maskZEROValues.pop(0)

        self.curwidth = 0 #Current width position
        self.curheight = 0 #Current height position
        self.curchan = 0 #Current channel position


    def saveImage(self,filename):
        cv.SaveImage(filename, self.image)


    def putBinaryValue(self, bits):
        for c in bits:
            val = list(self.image[self.curheight,self.curwidth])
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO

            self.image[self.curheight,self.curwidth] = tuple(val)
            self.nextSpace()

    def nextSpace(self):
        if self.curchan == self.nbchannels-1:
            self.curchan = 0
            if self.curwidth == self.width-1:
                self.curwidth = 0
                if self.curheight == self.height-1:
                    self.curheight = 0
                    if self.maskONE == 128:
                        raise SteganographyException, "Image filled"
                    else:
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1
            else:
                self.curwidth +=1
        else:
            self.curchan +=1

    def readBit(self):
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.nextSpace()
        if val > 0:
            return "1"
        else:
            return "0"

    def readByte(self):
        return self.readBits(8)

    def readBits(self, nb):
        bits = ""
        for i in range(nb):
            bits += self.readBit()
        return bits

    def byteValue(self, val):
        return self.binValue(val, 8)

    def binValue(self, val, bitsize):
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException, "binary value larger than the expected size"
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval

    def hideText(self, txt):
        l = len(txt)
        binl = self.binValue(l, 16)
        self.putBinaryValue(binl)
        for char in txt:
            c = ord(char)
            self.putBinaryValue(self.byteValue(c))

    def unhideText(self):
        ls = self.readBits(16)
        l = int(ls,2)
        i = 0
        unhideTxt = ""
        while i < l:
            tmp = self.readByte()
            i += 1
            unhideTxt += chr(int(tmp,2))
        return unhideTxt

    def hideImage(self, imtohide):
        w = imtohide.width
        h = imtohide.height
        if self.width*self.height*self.nbchannels < w*h*imtohide.channels:
            raise SteganographyException, "Carrier image not big enough to hold all the datas to steganography"
        binw = self.binValue(w, 16)
        binh = self.binValue(h, 16)
        self.putBinaryValue(binw)
        self.putBinaryValue(binh)
        for h in range(imtohide.height):
            for w in range(imtohide.width):
                for chan in range(imtohide.channels):
                    val = imtohide[h,w][chan]
                    self.putBinaryValue(self.byteValue(int(val)))


    def unhideImage(self):
        width = int(self.readBits(16),2)
        height = int(self.readBits(16),2)
        unhideimg = cv.CreateImage((width,height), 8, 3)
        for h in range(height):
            for w in range(width):
                for chan in range(unhideimg.channels):
                    val = list(unhideimg[h,w])
                    val[chan] = int(self.readByte(),2)
                    unhideimg[h,w] = tuple(val)
        return unhideimg

    def hideBin(self, filename):
        f = open(filename,'rb')
        bin = f.read()
        l = len(bin)
        if self.width*self.height*self.nbchannels < l+64:
            raise SteganographyException, "Carrier image not big enough to hold all the datas to steganography"
        self.putBinaryValue(self.binValue(l, 64))
        for byte in bin:
            self.putBinaryValue(self.byteValue(ord(byte)))

    def unhideBin(self):
        l = int(self.readBits(64),2)
        output = ""
        for i in range(l):
            output += chr(int(self.readByte(),2))
        return output

def binary_steg_hide(image, binary, result):
    carrier = cv.LoadImage(image)
    steg = LSBSteg(carrier)
    steg.hideBin(binary)
    steg.saveImage(result)

def binary_steg_reveal(steg_image, out):
    inp = cv.LoadImage(steg_image)
    steg = LSBSteg(inp)
    bin = steg.unhideBin()
    f = open(out, "wb")
    f.write(bin)
    f.close()

import argparse

parser = argparse.ArgumentParser(description='This python program applies LSB Steganography to an image and some type of input')

def main(av):
    bgroup = parser. add_argument_group("Hide binary with steg")
    bgroup.add_argument('-image', help='Provide the original image')
    bgroup.add_argument('-binary', help='The binary file to be obfuscated in the image')
    bgroup.add_argument('-steg-out', help='The resulting steganographic image')

    bgroup = parser.add_argument_group("Reveal binary")
    bgroup.add_argument('-steg-image', help='The steganographic image')
    bgroup.add_argument('-out', help='The original binary')

    args = parser.parse_args(av[1:])

    if len(av) == 7:
	binary_steg_hide(args.image, args.binary, args.steg_out)
    elif len(av) == 5:
        binary_steg_reveal(args.steg_image, args.out)
    else:
        print "Usage: '", av[0], "-h' for help", "\n", args

if __name__=="__main__":
    from sys import argv as av
    main(av)
