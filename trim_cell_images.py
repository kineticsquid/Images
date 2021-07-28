import numpy



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

