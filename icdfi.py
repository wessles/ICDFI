# ICDFI - Inverse CDF for Images

usage = """
ICDFI - Inverse CDF for Images

Usage:
python3 icdf_of_image.py <image file> [grid|overlay|cdf|cdf_x|cdf_y_given_x] <out file> [grid resolution]

Options:
grid - output an image with a grid representing the transformation of the U[0,1]^2 region CDF_inverse(<u,v>) -> <x,y>
overlay - output the same distorted grid, but overlay it on top of the source image
cdf - CDF of the image, with each pixel = p(x)p(y|x)
cdf_x - CDF of the image, only considering p(x)
cdf_y_given_x - CDF of the image, only considering p(y|x)

grid resolution - optional, defaults to 20
"""

import sys
from icdf_solver import *

def process(filename, mode, outfile, grid_resolution):
    pdf_img = Image.open(filename)
    pdf_img.convert('L')
    data = pdf_img.load()
    width, height = pdf_img.size

    F = lambda x,y: sum(data[x,y]) / len(data[x,y])

    cdf_x = get_cdf_x(width,height,F)
    cdf_y_given_x = get_cdf_y_given_x(width,height,F)

    if mode in ['cdf', 'cdf_x', 'cdf_y_given_x']:
        out_img = Image.new('L', (width, height))
        for x in range(0, width):
            for y in range(0, height):
                k = 0
                if mode == 'cdf':
                    k = cdf_x[x] * cdf_y_given_x[x][y]
                elif mode == 'cdf_x':
                    k = cdf_x[x]
                else:
                    k = cdf_y_given_x[x][y]
                out_img.putpixel((x,y), int(k*255))
        out_img.save(outfile)
    else:
        grid_points = [[(j*width/grid_resolution, i*height/grid_resolution) for i in range(grid_resolution+1)] for j in range(grid_resolution+1)]

        # distort the grid before drawing again
        for gx in range(0, grid_resolution+1):
            for gy in range(0, grid_resolution+1):
                grid_points[gx][gy] = inverse_cdf(gx/(grid_resolution),gy/(grid_resolution), width,height,cdf_x,cdf_y_given_x)

        # draw distorted grid
        grid_img = None
        if mode == 'grid':
            grid_img = Image.new('L', (width, height))
        elif mode == 'overlay':
            grid_img = Image.open(filename)
        render_grid(grid_img, grid_points, grid_resolution, width, height)
        grid_img.save(outfile)

if __name__ == "__main__":
    if len(sys.argv) <= 3 or len(sys.argv) >= 6:
        print(usage)
        exit(0)
    
    filename = sys.argv[1]
    mode = sys.argv[2]
    if mode not in ['grid', 'overlay', 'cdf', 'cdf_x', 'cdf_y_given_x']:
        print(usage)
        exit(0)

    outfile = sys.argv[3]
    resolution = 20
    if len(sys.argv) == 5:
        resolution = int(sys.argv[4])

    process(filename, mode, outfile, resolution)