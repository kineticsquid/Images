import morph_array_to_size
import count_pixels
import numpy

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