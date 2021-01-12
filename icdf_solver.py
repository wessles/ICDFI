# Code for finding the inverse CDF of a 2D matrix of numbers

from PIL import Image, ImageDraw

def get_cdf_x(width, height, F):
    # find PDF along x axis
    total_x = 0
    pdf_x = [0 for i in range(width)]
    for x in range(0, width):
        for y in range(0, height):
            value = float(F(x,y))
            pdf_x[x] += value
            total_x += value
    if total_x > 0.0:
        for x in range(0, width):
            pdf_x[x] = pdf_x[x] / total_x
    
    # integrate to CDF
    cdf_x = [0 for i in range(width)]
    for x in range(0, width):
        if x != 0:
            cdf_x[x] += cdf_x[x-1]
        cdf_x[x] += pdf_x[x]
    
    return cdf_x

def get_cdf_y_given_x(width, height, F):
    # find PDF along each column
    pdf_y_given_x = [[0 for i in range(height)] for j in range(width)] 
    for x in range(0, width):
        total_column = 0
        for y in range(0, height):
            value = float(F(x,y))
            pdf_y_given_x[x][y] = value
            total_column += value
        if total_column > 0:
            for y in range(0, height):
                pdf_y_given_x[x][y] /= total_column

    # integrate to CDF
    cdf_y_given_x = [[0 for i in range(height)] for j in range(width)]
    for x in range(0, width):
        for y in range(0, height):
            if y != 0:
                cdf_y_given_x[x][y] += cdf_y_given_x[x][y - 1]
            cdf_y_given_x[x][y] += pdf_y_given_x[x][y]

    return cdf_y_given_x

def inverse_cdf(u, v, width, height, cdf_x, cdf_y_given_x):
    # Could be optimized with a binary search, but this is fast enough for my needs right now
    
    x = 0
    for i in range(0, width):
        x = i
        if cdf_x[i] >= u:
            break
    
    y = 0
    for i in range(0, height):
        y = i
        if cdf_y_given_x[x][i] >= v:
            break
    
    return (x,y)

def render_grid(grid_img, grid_points, grid_resolution, width, height):
    grid_draw = ImageDraw.Draw(grid_img)
    def line(x,y,x2,y2):
        grid_draw.line((x,y,x2,y2), fill=255)
    for gx in range(0, grid_resolution+1):
        for gy in range(0, grid_resolution+1):
            p = grid_points[gx][gy]
            if gx != grid_resolution:
                right = grid_points[gx+1][gy]
                line(p[0], p[1], right[0], right[1])
            if gy != grid_resolution:
                down = grid_points[gx][gy+1]
                line(p[0], p[1], down[0], down[1])