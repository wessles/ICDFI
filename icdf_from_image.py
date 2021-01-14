usage = """
ICDFI - Inverse CDF for Images

Usage:
python3 icdf_of_image.py <image file> [grid | overlay | samples | cdf | cdf_x | cdf_y_given_x] <out file> [grid resolution | number of samples]

Options:
    grid - output an image with a grid representing the transformation of the U[0,1]^2 region CDF_inverse(<u,v>) -> <x,y>
    overlay - output the same distorted grid, but overlay it on top of the source image

    sampling - scatter dots in uv space, then transform with inverse CDF. Visualizes importance sampling.

    cdf - CDF of the image, with each pixel = p(x)p(y|x)
    cdf_x - CDF of the image, only considering p(x)
    cdf_y_given_x - CDF of the image, only considering p(y|x)

    grid resolution - optional, defaults to 20
    number of samples - optional, defaults to 20
"""

import sys
import math
import radical_inverse as rinv
from icdf_solver import *

def process(filename, mode, outfile, grid_resolution):
    pdf_img = Image.open(filename)
    pdf_img.convert('L')
    data = pdf_img.load()
    width, height = pdf_img.size

    PDF = lambda x, y: sum(data[x,y]) / len(data[x,y])
    PDF_uv = lambda u, v: PDF(int(math.floor(u*width)),int(math.floor(v*height)))

    inverse_cdf = InverseCDF((width, height), PDF_uv)

    if mode in ['cdf', 'cdf_x', 'cdf_y_given_x']:
        out_img = Image.new('L', (width, height))
        for x in range(0, width):
            for y in range(0, height):
                k = 0
                if mode == 'cdf':
                    k = inverse_cdf.cdf_x[x] * inverse_cdf.cdf_y_given_x[x][y]
                elif mode == 'cdf_x':
                    k = inverse_cdf.cdf_x[x]
                else:
                    k = inverse_cdf.cdf_y_given_x[x][y]
                out_img.putpixel((x,y), int(k*255))
        out_img.save(outfile)
    else:
        # prepare output image
        grid_img = None
        if mode == 'grid':
            grid_img = Image.new('RGB', (width, height))
        elif mode == 'overlay' or mode == 'sampling':
            grid_img = Image.open(filename)
            grid_img.convert('RGB')
        

        if mode == 'grid' or mode == 'overlay':
            # create distorted grid
            grid_points = [[(0) for i in range(grid_resolution+1)] for j in range(grid_resolution+1)]
            for gx in range(0, grid_resolution + 1):
                for gy in range(0, grid_resolution + 1):
                    u,  v   =   gx / grid_resolution, gy / grid_resolution
                    u2, v2  =   inverse_cdf.evaluate(u, v)
                    grid_points[gx][gy] = (u2 * width, v2 * height)
                
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
        elif mode == 'sampling':
            numSamples = grid_resolution
                
            # render grid on top
            grid_draw = ImageDraw.Draw(grid_img)
            r = 8
            w = 3
            def dot(x,y):
                grid_draw.ellipse((x-r,y-r,x+r,y+r), outline=(255,0,0), width=w)
            for i in range(0, numSamples):
                u, v = rinv.radical_inverse_2(i), rinv.radical_inverse(i,3)
                u2, v2 = inverse_cdf.evaluate(u, v)
                dot(u2*width, v2*height)

        grid_img.save(outfile)

if __name__ == "__main__":
    if len(sys.argv) <= 3 or len(sys.argv) >= 6:
        print(usage)
        exit(0)
    
    filename = sys.argv[1]
    mode = sys.argv[2]
    if mode not in ['grid', 'overlay', 'cdf', 'cdf_x', 'cdf_y_given_x', 'sampling']:
        print(usage)
        exit(0)

    outfile = sys.argv[3]
    resolution = 20
    if len(sys.argv) == 5:
        resolution = int(sys.argv[4])

    process(filename, mode, outfile, resolution)