from PIL import Image, ImageDraw
import numpy

hue_threshold = 128
black = 0
white = 255

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
