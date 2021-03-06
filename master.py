"""
Execution: python master.py <image.jpg> <degredation>
    Image must be jpg
    Degredation values higher than 1 lead to significant runtime, particularly on large images
Dependencies:
    PIL
    numpy
    pandas
Note:
    Currently setup to run ten times for radius [1,9]. This can be modified
    Prints output to terminal. Pipe to text if you want a text file.
"""
from PIL import Image
from random import randint
import numpy as np
import sys
import pandas as pd
import math
################
tearColor = (255, 255, 255, 0)
#radius = 3
maxTearLength = 250
#percentage = float()
################


def main():
    #load input
    for rad in range(1,10):
        print "radius = ", rad
        for i in range(10):
            infile = sys.argv[1]
            percentage = float(sys.argv[2])
            im = Image.open(infile).convert("RGBA")
            pix = im.load() # Original Image

            #tear
            tornImg = im.copy()
            tornImg = tear(im, pix,percentage) #may need to do a deep copy or something
            tornPix = tornImg.load()

            outFile = infile.replace(".jpg", "Torn.jpg")
            tornImg.save(outFile, "JPEG", quality=95, optimize=True, progressive=True)

            width, height = im.size
            totalMissing = 0
            for x in range(width):
                for y in range(height):
                    if tornPix[x,y] == tearColor:
                        totalMissing += 1

            for x in range(width):
                for y in range(height):
                    if tornPix[x,y] == tearColor:
                        tornPix[x,y] = impute(tornImg, tornPix,rad, x, y)

            newMissing = 0
            for x in range(width):
                for y in range(height):
                    if tornPix[x,y] == tearColor:
                        newMissing += 1

            im = Image.open(infile).convert("RGBA")
            pix = im.load() # Original Image
            dist = 0.0
            for x in range(width):
                for y in range(height):
                    t1 = pix[x,y]
                    t2 = tornPix[x,y]
                    dist += math.sqrt( (t1[0]-t2[0])**2 + (t1[1]-t2[1])**2 + (t1[2]-t2[2])**2 )

            dist /= (totalMissing-newMissing)
            print round(dist,3)
            outFile = infile.replace(".jpg", "Fixed.jpg")
            tornImg.save(outFile, "JPEG", quality=95, optimize=True, progressive=True)


def impute(img, pix, radius, x, y):
    width, height = img.size
    neighbors = list()
    #gather neighbor pixel values
    for i in range(x-radius, x+radius+1): #upper bound is exclusive
        for j in range(y-radius, y+radius+1):
            if i < 0 or j < 0 or i >= width or j >= height: #check bound
                continue
            elif pix[i,j] == tearColor: #missing pixel
                continue
            else:
                neighbors.append(pix[i,j])
    #get modes
    listNeighbors = [list(x) for x in neighbors]
    rgbTable = pd.DataFrame(listNeighbors)
    rgbTable.columns = ["r", "g", "b", "a"]

    modes = rgbTable.mode()
    means = rgbTable.mean()
    if modes.empty:
        return tearColor
    values = modes.iloc[0].values
    pixelList = list()
    i = 0
    for v in values:
        if np.isnan(v):
            mean = int(means.iloc[i])
            pixelList.append(mean)
        else:
            pixelList.append(int(v))
        i += 1
    newPixel = tuple(pixelList)
    return newPixel


def tear(im, pix,percentage):
    width, height = im.size

    threshold = percentage * width * height
    length = 0

    while length < threshold:

        inter_length = 0
        start = randint(1,4) # 1-top   2-right   3-bottom   4-left

        if start == 1:
            x = randint(0, width-1)
            y = 0
        elif start == 2:
            x = width-1
            y = randint(0, height-1)
        elif start == 3:
            x = randint(0, width-1)
            y = height-1
        elif start == 4:
            x = 0
            y = randint(0, height-1)

        # print("{0} \t {1}".format(start_x,start_y))

        while ( inter_length != maxTearLength ) and ( length < threshold ):
            # print(length)
            pix[x,y] = tearColor

            while True:
                nextMove = randint(1, 5)

                if start == 1:# tear coming from top
                     # 1-left  2-down   3-right
                    ######edge cases############
                    if y == height-1:
                        break
                    if x >= width-1:
                        y += 1
                        x -= 1
                    elif x <= 0:
                        y += 1
                        x += 1
                    ##################################

                    elif nextMove == 1 or nextMove == 2:
                        y += 1
                        x -= 1
                    elif nextMove == 3:
                        y += 1
                    elif nextMove == 4 or nextMove == 5:
                        y += 1
                        x += 1

                elif start == 2: # tear coming from right
                    ######edge cases############
                    if x == 0:
                        break
                    if y >= height - 1:
                        y -= 1
                        x -= 1
                    elif y <= 0:
                        y += 1
                        x -= 1
                    ##################################

                     # 1-up  2-left   3-down
                    elif nextMove == 1 or nextMove == 2:
                        y -= 1
                        x -= 1
                    elif nextMove == 3:
                        x -= 1
                    elif nextMove == 4 or nextMove == 5:
                        y += 1
                        x -= 1

                elif start == 3: # tear coming from bottom
                      # 1-left  2-up   3-right
                    ######edge cases############
                    if y == 0:
                        break
                    if x >= width-1:
                        y -= 1
                        x -= 1
                    elif x <= 0:
                        y -= 1
                        x += 1
                    ##################################
                    elif nextMove == 1 or nextMove == 2:
                        y -= 1
                        x -= 1
                    elif nextMove == 3:
                        y -= 1
                    elif nextMove == 4 or nextMove == 5:
                        y -= 1
                        x += 1

                elif start == 4: # tear coming from left
                     # 1-up   2-right   3-down

                     ######edge cases############
                    if x == width-1:
                        break
                    if y >= height-1:
                        y -= 1
                        x += 1
                    elif y <= 0:
                        y += 1
                        x += 1
                    ##################################
                    elif nextMove == 1 or nextMove == 2:
                        y -= 1
                        x += 1
                    elif nextMove == 3:
                        x += 1
                    elif nextMove == 4 or nextMove == 5 :
                        y += 1
                        x += 1
                #print x, y, width, height
                if (0 <= x < width) and (0 <= y < height):
                    break

            length += 1
            inter_length += 1

    return im


if __name__ == "__main__":
    main()
