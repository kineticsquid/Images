from PIL import Image, ImageDraw
import numpy
from numpy import asarray
import cv2
import print_image
from matplotlib import pyplot

# Colors less than this are made black (0), greater are made white (255)
hue_threshold = 128
black = 0
white = 255

# Percentage of pixels in a line that are black. If greater than this
# then we've found a line
# between .5 and .75
line_threshold = 0.7


def reduce_line_noise(lines):
    theta_margin_of_error = 0.05
    new_lines = []
    for entry in lines:
        line = entry[0]
        rho = line[0]
        theta = line[1]
        margin_of_error = numpy.pi * theta_margin_of_error
        if abs(theta) < margin_of_error or abs(theta - numpy.pi/2) < margin_of_error or abs(theta - numpy.pi) < margin_of_error or abs(theta - numpy.pi*3/2) < margin_of_error:
            new_lines.append(entry)
            print("Y\tRho: %s\tTheta: %s" % (rho, theta))
        else:
            print("N\tRho: %s\tTheta: %s" % (rho, theta))
    print(len(lines))
    print(len(new_lines))
    return new_lines


def find_lines_cv2(image_name):
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    
    image = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    pyplot.imshow(image)
    (thresh, blackAndWhiteImage) = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    pyplot.imshow(blackAndWhiteImage)
    # edges = cv2.Canny(blackAndWhiteImage, 50, 150, apertureSize=3)
    # print_image.print_image_edges(edges)
    blackAndWhiteImage2 = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    pyplot.imshow(blackAndWhiteImage2)
    blackAndWhiteImage3 = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    pyplot.imshow(blackAndWhiteImage3)

    image_height, image_width, color_depth = image.shape
    minLineLength = min(image_height, image_width) * .75
    maxLineGap = 10

    # linesP = cv2.HoughLinesP(edges, 1, numpy.pi / 180, 100, minLineLength, maxLineGap)
    # print_image_linesP(image_name, edges, linesP)

    lines = cv2.HoughLines(edges,1,numpy.pi/180, 100)
    print_image.print_image_lines(image_name, edges, lines)
    new_lines = reduce_line_noise(lines)
    print_image.print_image_lines(image_name, edges, new_lines)

    horizontal_lines = numpy.zeros(image_height)
    vertical_lines = numpy.zeros(image_width)

    return horizontal_lines, vertical_lines, image

def find_lines(image_name):
    image = Image.open(image_name)
    # First darken the image a bit to make the lines show up better
    image_mono = image.point(lambda p: p * 0.9)
    # Now make it monochrome
    image_mono = image_mono.convert('1', dither=Image.NONE)
    image_array = asarray(image_mono)
    image_height, image_width = image_array.shape
    vertical_line_pixels = numpy.sum(image_array, axis=0)
    horizontal_line_pixels = numpy.sum(image_array, axis=1)
    print("Vertical lines (x axis):")
    print("\tMax:\t%s" % numpy.max(vertical_line_pixels))
    print("\tMin:\t%s" % numpy.min(vertical_line_pixels))
    print("\tMean:\t%s" % numpy.mean(vertical_line_pixels))
    print("\tStd:\t%s" % numpy.std(vertical_line_pixels))
    print("Horizontal lines (y axis):")
    print("\tMax:\t%s" % numpy.max(horizontal_line_pixels))
    print("\tMin:\t%s" % numpy.min(horizontal_line_pixels))
    print("\tMean:\t%s" % numpy.mean(horizontal_line_pixels))
    print("\tStd:\t%s" % numpy.std(horizontal_line_pixels))

    horizontal_lines = numpy.zeros(image_height)
    vertical_lines = numpy.zeros(image_width)

    front_edge_of_line_found = False
    for x in range(image_width):
        if vertical_line_pixels[x] / image_height >= line_threshold:
            if not front_edge_of_line_found:
                front_edge_of_line_found = True
                front_edge_of_line = x
        else:
            if front_edge_of_line_found:
                vertical_lines.append((front_edge_of_line, x-1))
                front_edge_of_line_found = False
    if front_edge_of_line_found:
        vertical_lines.append((front_edge_of_line, x-1))
        front_edge_of_line_found = False

    for y in range(image_height):
        if horizontal_line_pixels[y] / image_width >= line_threshold:
            if not front_edge_of_line_found:
                front_edge_of_line_found = True
                front_edge_of_line = y
        else:
            if front_edge_of_line_found:
                horizontal_lines.append((front_edge_of_line, y-1))
                front_edge_of_line_found = False
    if front_edge_of_line_found:
        horizontal_lines.append((front_edge_of_line, y-1))
        front_edge_of_line_found = False

    return horizontal_lines, vertical_lines, image

