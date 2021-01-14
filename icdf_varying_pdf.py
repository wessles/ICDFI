usage = """
ICDF w/ Varying PDF Animation
- This could take around 20 minutes with default settings. To make it faster, lower the resolution or decrease the frame count
- Feel free to edit the PDF function in this script; it's arbitrary.

Usage:
python3 icdf_varying_pdf.py <video_output_path>.avi
"""
###
# CONSTANTS:

width,height = 1280,720
width,height = 200 ,100
framerate = 60
grid_resolution = 32

# frames of CDF animation
N = 240

# beginning pause frames
context_pause = 120

# ending pause frames
end_pause = 120

###

import cv2
import numpy as np
import random
import time
import math
import sys
import threading
from icdf_solver import *

###
# PDF(x,y,t) function

def gauss(x,y,px,py,scale):
    x -= px
    y -= py
    x /= scale
    y /= scale
    return math.exp(-(x*x) - (y*y))

def PDF_t(x,y,t):
    x -= .5
    y -= .5

    t*=0.005
    k=0
    k += gauss(x,y, 0.9*math.sin(t*3), 0.9*math.cos(t*3), 0.2+(0.1 * math.sin(t * 1.0)))
    k += gauss(x,y, 0.1*math.sin(t*2), 0.1*math.cos(t*2), 0.2+(0.1 * math.cos(t * 1.2)))
    k += gauss(x,y, 0.4*math.sin(t*5), 0.4*math.cos(t*5), 0.2+(0.1 * math.cos(t * 1.2)))
    k += gauss(x,y, 0.5,0.5, 1)/4.0
    return k

###

def smoothstep(t):
    return t * t * (3 - 2*t)

def process(outfile):
    # Begin Process
    img_array = [None] * N

    start_time = time.time()

    # calculate all frames in t = [t0, t1]
    def calculate_frames(t0, t1):
        for k in range(t0, t1 + 1):
            t = t0 + smoothstep((k-t0) / (t1-t0)) * (t1-t0)
            PDF = lambda x,y: PDF_t(x,y,t)
            inverse_cdf = InverseCDF((width, height), PDF)
            
            grid_points = [[(0) for i in range(grid_resolution+1)] for j in range(grid_resolution+1)]

            for gx in range(0, grid_resolution + 1):
                for gy in range(0, grid_resolution + 1):
                    u,  v   =   gx / grid_resolution, gy / grid_resolution
                    u2, v2  =   inverse_cdf.evaluate(u, v)
                    grid_points[gx][gy] = (u2 * width, v2 * height)

            # create image of PDF
            grid_img = Image.new('RGB', (width, height))
            for x in range(0,width):
                for y in range(0,height):
                    v = int(255 * PDF(x / width, y / height))
                    grid_img.putpixel((x,y), (v,v,v))
            
            # render grid on top
            grid_draw = ImageDraw.Draw(grid_img)
            def line(x,y,x2,y2):
                grid_draw.line((x,y,x2,y2), fill=(0,0,255))
            for gx in range(0, grid_resolution+1):
                for gy in range(0, grid_resolution+1):
                    p = grid_points[gx][gy]
                    if gx != grid_resolution:
                        right = grid_points[gx+1][gy]
                        line(p[0], p[1], right[0], right[1])
                    if gy != grid_resolution:
                        down = grid_points[gx][gy+1]
                        line(p[0], p[1], down[0], down[1])

            img_array[k] = np.array(grid_img)

            elapsed = time.time() - start_time
            total_estimate = (N * elapsed / (k+1))
            remaining = total_estimate-elapsed
            print(('%.1f' % elapsed) + "s / " + ('%.1f' % remaining) + "s\t" + ('%.3f' % (100 * (k+1)/N))+"% done")
    
    calculate_frames(0,N-1)
    
    print(str((time.time() - start_time) / N))

    first_img = img_array[0]
    img_array = [first_img] * context_pause + img_array

    last_img = img_array[-1]
    img_array += [last_img] * end_pause

    out = cv2.VideoWriter(outfile,cv2.VideoWriter_fourcc(*'DIVX'), framerate, (width,height))
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(usage)
        exit(0)
    
    filename = sys.argv[1]

    process(filename)