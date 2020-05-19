from PIL import Image, ImageDraw
import numpy
from numpy import asarray
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import canny
import cv2

# Colors less than this are made black (0), greater are made white (255)
hue_threshold = 128
black = 0
white = 255

# Percentage of pixels in a line that are black. If greater than this
# then we've found a line
# between .5 and .75
line_threshold = 0.7

def morph_array_to_size(from_array, to_size):
    from_size = len(from_array)
    to_array = numpy.zeros((to_size), dtype=float)

    if from_size >= to_size:
        # for f in range(from_size):
        #     to_array[f] = from_array[f]
        for f in range(from_size):
            starting_to_element = int(to_size / from_size * f)
            ending_to_element = int(to_size / from_size * (f + 1))
            if starting_to_element == ending_to_element or \
                    ending_to_element - to_size / from_size * (f + 1) == 0:
                to_array[starting_to_element] += from_array[f]
            else:
                amt1_pct = from_size / to_size * f - int(from_size / to_size * f)
                amt2_pct = 1 - amt1_pct
                to_array[starting_to_element] += from_array[f] * amt1_pct
                to_array[ending_to_element] += from_array[f] * amt2_pct
    else:
        for t in range(to_size):
            starting_from_element = int(from_size / to_size * t)
            ending_from_element = int(from_size / to_size * (t + 1))
            if starting_from_element == ending_from_element or \
                    ending_from_element - from_size / to_size * (t + 1) == 0:
                to_array[t] += from_array[starting_from_element] * from_size / to_size
            else:
                amt1_pct = int(from_size / to_size * t) + 1 - from_size / to_size * t
                amt2_pct = from_size / to_size * (t + 1) - int(from_size / to_size * (t + 1))
                to_array[t] += from_array[starting_from_element] * amt1_pct
                to_array[t] += from_array[ending_from_element] * amt2_pct

    return to_array

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

def diff_between_arrays(a1, a2):
    diff = 0
    for n in range(len(a1)):
        diff += (a1[n] - a2[n]) * (a1[n] - a2[n])
    return diff

def get_number_from_image(image, x_metrics, y_metrics):
    x_counts, y_counts = count_pixels(image)
    x_metrics_size = len(x_metrics["1"])
    y_metrics_size = len(y_metrics["1"])
    #normalize the size of the image arrays to match the metrics data
    x_histogram = morph_array_to_size(x_counts, x_metrics_size)
    y_histogram = morph_array_to_size(y_counts, y_metrics_size)
    # Now get percentages
    x_sum = sum(x_histogram)
    y_sum = sum(y_histogram)
    for n in range(x_histogram.size):
        x_histogram[n] = x_histogram[n]/x_sum
    for n in range(y_histogram.size):
        y_histogram[n] = y_histogram[n]/y_sum
    # Now calculate difference between x and y pixel distribution for this image and metrics data
    # the 1000 is there for readability
    x_distance = numpy.zeros((len(x_metrics)+1), dtype=float)
    for n in range(1, len(x_metrics)+1):
        x_distance[n] = diff_between_arrays(x_histogram, x_metrics[str(n)]) * 1000
    y_distance = numpy.zeros((len(y_metrics)+1), dtype=float)
    for n in range(1, len(y_metrics)+1):
        y_distance[n] = diff_between_arrays(y_histogram, y_metrics[str(n)]) * 1000

    # x_distance is an array that has the least squares distance between the x-axis histogram
    # of this image and the x-axis histograms of the training data [1..9]. y_distance is the
    # same thing along the y-axis. The algorithm to determine the digit in the image goes like this:
    # We first match using the y-axis histogram. Experiments have shown this is accurate for
    # everything except some confusion when a '1' is incorrectly recognized as a '2'. So,
    # when we see a '2', perform a second check using the x-axis to see which distance is less,
    # '1' or '2'.
    #
    # Other algorithms attempted:
    # - x_distance
    # - y_distance
    # - x_distance * y_distance
    for n in range(1, len(x_metrics)+1):
        print('n: %s. x_distance: %s, y_distance: %s' % (n, x_distance[n], y_distance[n]))
        if n == 1:
            current_y_distance_min = y_distance[n]
            number = n
        else:
            if y_distance[n] < current_y_distance_min:
                current_y_distance_min = y_distance[n]
                number = n
    if number == 2:
        if x_distance[1] < x_distance[2]:
            number = 1

    print('number: %s' % number)
    return number

def print_image(image, bounding_box):
    if bounding_box is None:
        width, height = image.size
        left = 0
        top = 0
        right = width - 1
        bottom = height - 1
    else:
        left, top, right, bottom = bounding_box
    print("Left: %s, Top: %s, Right: %s, Bottom: %s" % (left, top, right, bottom))
    print(' ', end='\t')
    for x in range(left, right + 1):
        print(x%10, end='')
    print(end='\n')
    for y in range(top, bottom+1):
        print(y, end='\t')
        for x in range(left, right+1):
            if image.getpixel((x, y)) == black:
                print("X", end='')
            else:
                print(".", end='')
        print(end='\n')

def print_image_edges(image_array):
    edge_image = Image.fromarray(image_array)
    edge_image.show()
    return

def print_image_linesP(image_name, edges, lines):
    img = Image.open(image_name)
    edge_img = Image.fromarray(edges).convert('RGB')
    d_img = ImageDraw.Draw(img)
    d_edge_img = ImageDraw.Draw(edge_img)
    line_color = (255, 0, 255)
    line_width = 3
    for line in lines:
        d_img.line((line[0][0], line[0][1], line[0][2], line[0][3]), width=line_width, fill=line_color)
        d_edge_img.line((line[0][0], line[0][1], line[0][2], line[0][3]), width=line_width, fill=line_color)

    img.show()
    edge_img.show()
    return

def print_image_lines(image_name, edges, lines):
    img = Image.open(image_name)
    edge_img = Image.fromarray(edges).convert('RGB')
    d_img = ImageDraw.Draw(img)
    d_edge_img = ImageDraw.Draw(edge_img)
    line_color = (255, 0, 255)
    line_width = 3
    image_height, image_width = img.size
    max_image_dimension = max(image_width, image_height)
    for line in lines:
        for rho, theta in line:
            # cos pi/2 = 0, cos 0 = 1
            a = numpy.cos(theta)
            # sin pi/2 = 1, sin 0 = 0
            b = numpy.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + max_image_dimension * (-b))
            y1 = int(y0 + max_image_dimension * (a))
            x2 = int(x0 - max_image_dimension * (-b))
            y2 = int(y0 - max_image_dimension * (a))
            d_img.line((x1, y1, x2, y2), width=line_width, fill=line_color)
            d_edge_img.line((x1, y1, x2, y2), width=line_width, fill=line_color)

    img.show()
    edge_img.show()
    return


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
    image = cv2.imread(image_name)
    (thresh, blackAndWhiteImage) = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(blackAndWhiteImage, 50, 150, apertureSize=3)
    print_image_edges(edges)
    image_height, image_width, color_depth = image.shape
    minLineLength = min(image_height, image_width) * .75
    maxLineGap = 10
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    # linesP = cv2.HoughLin?esP(edges, 1, numpy.pi / 180, 100, minLineLength, maxLineGap)
    # print_image_linesP(image_name, edges, linesP)

    lines = cv2.HoughLines(edges,1,numpy.pi/180, 100)
    print_image_lines(image_name, edges, lines)
    new_lines = reduce_line_noise(lines)
    print_image_lines(image_name, edges, new_lines)

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


def get_cell_image_boundaries(horizontal_lines, vertical_lines):

    cell_images_boundaries = numpy.zeros((len(horizontal_lines)-1,
                                          len(vertical_lines)-1), dtype=object)
    for row in range(len(horizontal_lines) - 1):
        for column in range(len(vertical_lines) - 1):
            cell_images_boundaries[row, column] = (vertical_lines[column][1]+1,
                horizontal_lines[row][1]+1,
                vertical_lines[column+1][0]-1,
                horizontal_lines[row+1][0]-1)
    return cell_images_boundaries

def black_pixel_in_column(image, column, top_start, bottom_stop):
    x = column
    for y in range(top_start, bottom_stop + 1):
        if image.getpixel((x, y)) == black:
            return True
    return False

def black_pixel_in_row(image, row, left_start, right_stop):
    y = row
    for x in range(left_start, right_stop + 1):
        if image.getpixel((x, y)) == black:
            return True
    return False

def black_pixel_in_image(image, left_start, top_start, right_stop, bottom_stop):
    for y in range(top_start, bottom_stop + 1):
        for x in range(left_start, right_stop + 1):
            if image.getpixel((x, y)) == black:
                return True
    return False

def trim_cell_images(image, cell_image_boundaries):

    rows, columns = cell_image_boundaries.shape
    for row in range(rows):
        for column in range(columns):
            new_left = cell_image_boundaries[row][column][0]
            new_top = cell_image_boundaries[row][column][1]
            new_right = cell_image_boundaries[row][column][2]
            new_bottom = cell_image_boundaries[row][column][3]

            # First get rid of any black around the edges
            done = False
            while not done:
                done = True
                if black_pixel_in_column(image, new_left, new_top, new_bottom):
                    new_left += 1
                    done = False
                if black_pixel_in_row(image, new_top, new_left, new_right):
                    new_top += 1
                    done = False
                if black_pixel_in_column(image, new_right, new_top, new_bottom):
                    new_right -= 1
                    done = False
                if black_pixel_in_row(image, new_bottom, new_left, new_right):
                    new_bottom -= 1
                    done = False

            # Now, get rid of the white space around the number. First make sure it's not a blank cell.
            if black_pixel_in_image(image, new_left, new_top, new_right, new_bottom):
                # print_image(image, (new_left, new_top, new_right, new_bottom))
                done = False
                while not done:
                    done = True
                    if not black_pixel_in_column(image, new_left, new_top, new_bottom):
                        new_left += 1
                        done = False
                    if not black_pixel_in_row(image, new_top, new_left, new_right):
                        new_top += 1
                        done = False
                    if not black_pixel_in_column(image, new_right, new_top, new_bottom):
                        new_right -= 1
                        done = False
                    if not black_pixel_in_row(image, new_bottom, new_left, new_right):
                        new_bottom -= 1
                        done = False
            else:
                # This means a blank cell so set coordinates to indicate so
                new_left = 0
                new_top = 0
                new_right = 0
                new_bottom = 0
            cell_image_boundaries[row][column] = (new_left, new_top, new_right, new_bottom)

