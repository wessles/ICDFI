# ICDFF - Inverse CDF for Functions
# This is just a demo of using the icdf_solver on non-image inputs.
# In this case, it's just a 2D gaussian function.

import math
from icdf_solver import *

def process():
    width, height = 1024, 1024

    sigma = width * 10
    mu = width / 2
    gauss = lambda x: (1.0 / math.sqrt(2 * math.pi * sigma**2)) * math.exp((-1/(2*sigma)) * math.pow(x - mu, 2))
    G = lambda x, y: gauss(x) * gauss(y)

    cdf_x = get_cdf_x(width,height,G)
    cdf_y_given_x = get_cdf_y_given_x(width,height,G)

    grid_resolution = 20

    # distort the grid before drawing again
    grid_points = [[(j*width/grid_resolution, i*height/grid_resolution) for i in range(grid_resolution+1)] for j in range(grid_resolution+1)]
    for gx in range(0, grid_resolution+1):
        for gy in range(0, grid_resolution+1):
            grid_points[gx][gy] = inverse_cdf(gx/(grid_resolution),gy/(grid_resolution), width,height,cdf_x,cdf_y_given_x)

    # draw distorted grid
    grid_img = Image.new('L', (width, height))
    render_grid(grid_img, grid_points, grid_resolution, width, height)
    grid_img.save('out.png')

if __name__ == "__main__":
    process()