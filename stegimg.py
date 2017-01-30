from steg import LSBSteg
import cv
import sys
str = open('/image/shake.txt', 'r').read()
carrier = cv.LoadImage("cat1.jpg")
steg = LSBSteg(carrier)
steg.hideText(str)
steg.saveImage("encryptimg.png") #Image that contain datas
