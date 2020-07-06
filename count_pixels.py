import numpy

black = 0
white = 255

def count_pixels(image):
    width, height = image.size
    # arrays to hold the x and y axis totals for this image
    x_histogram = numpy.zeros((width), dtype=int)
    y_histogram = numpy.zeros((height), dtype=int)
    # scan the image and count
    for y in range(height):
        for x in range(width):
            if image.getpixel((x, y)) == black:
                x_histogram[x] += 1
                y_histogram[y] += 1
    return x_histogram, y_histogram
