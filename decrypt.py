from steg import LSBSteg
import cv

im = cv.LoadImage("/image/encryptimg.png")
steg = LSBSteg(im)
print "Text value:",steg.unhideText()
