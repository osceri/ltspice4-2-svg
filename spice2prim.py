#!/usr/bin/env python
# -*- coding: ascii -*-
import os
import sys
from math import *
from config import *

# Output buffers.
text_output = ""

# Handles program output text
def fprint(msg):
    global text_output
    text_output += str(msg) + "\n"
def fclear():
    global text_output
    text_output = ""

# Mathematical functions on vectors, fairly self-explanatory
def mul_vec(s, x):
    s1, s2 = s
    x1, x2 = x
    return [ s1*x1, s2*x2 ]
def add_vec(x, y):
    x1, x2 = x
    y1, y2 = y
    return [ x1+y1, x2+y2 ]
def sub_vec(x, y):
    x1, x2 = x
    y1, y2 = y
    return [ x1-y1, x2-y2 ]
def rot_vec(p, x):
    x1, x2 = x
    return [ x1*cos(p) - x2*sin(p), x1*sin(p) + x2*cos(p) ]
def dot_vec(x, y):
    x1, x2 = x
    y1, y2 = y
    return x1*y1 + x2*y2
def comb_vec(f, x, y):
    x1, x2 = x
    y1, y2 = y
    return [ f*x[0] + (1-f)*y[0], f*x[1] + (1-f)*y[1] ]
def norm(x):
    x1, x2 = x
    return sqrt(x1*x1+x2*x2)
def arg(x):
    x1, x2 = x
    return atan2(x2, x1)
def mirror_vec(m, x):
    x1, x2 = x
    if m:
        return [-x1, x2]
    else:
        return [x1, x2]


# This function makes sure that flags are oriented correctly, given how 
# they are placed in relation to wire junctions/wires. 
# I don't understand why ltspice doesn't already handle this xd
def hnode_dir(hnode, pwires):
    # The junction compass rose
    left = False
    right = False
    up = False
    down = False

    # Sometimes equating tuples of floats doesn't work,
    # this is less discriminatory
    closen = lambda x, y: norm(sub_vec(x, y)) < 0.01

    for index in range(len(pwires)//2):
        index *= 2
        x = 0
        y = 0
        
        # Depending on wether the starting node och ending node
        # of the line is the half-node, these must be reordered
        # If the point is not either node of the line, then the
        # line is ignored.
        if closen(pwires[index], hnode):
            y = pwires[index+1]
            x = pwires[index]
        elif closen(pwires[index+1], hnode):
            y = pwires[index]
            x = pwires[index+1]
        else:
            continue

        dx, dy = sub_vec(x, y)
        if abs(dx) > abs(dy):
            if dx > 0:
                right = True
            else:
                left = True
        else:
            if dy > 0:
                up = True
            else:
                down = True

    # There are 16 different cases that need to be handled
    case = left + 2*(right + 2*(up + 2*down))

    # If only there was an appropriate syntax to handle different cases
    if case == 0:
        return "R0", "uCenter"
    if case == 1:
        return "R90", "lRight"
    if case == 2:
        return "R270", "rLeft"
    if case == 3:
        return "R0", "uuCenter"
    if case == 4:
        return "R0", "dVRight"
    if case == 5:
        return "R0", "ddCenter"
    if case == 6:
        return "R0", "ddCenter"
    if case == 7:
        return "R0", "ddCenter"
    if case == 8:
        return "R180", "uVLeft"
    if case == 9:
        return "R90", "uuCenter"
    if case == 10:
        return "R270", "uuCenter"
    if case == 11:
        return "R180", "uuCenter"
    if case == 12:
        return "R270", "llVCenter"
    if case == 13:
        return "R90", "lRight"
    if case == 14:
        return "R270", "rLeft"
    if case == 15:
        return "R0", "uurLeft"

# These bounds may be used to normalize the size of the schematic 
lower_x = 0
upper_x = 0
lower_y = 0
upper_y = 0


def main():
    # The following code finds an asc-file in the current working directory
    # It then opens it, otherwise it will quit
    cwd = os.getcwd()
    os.chdir(cwd)
    asc_file = ""
    for pfile in os.listdir():
        filename, dot, extension = pfile.partition(".")
        if extension == "asc":
            asc_file = f"{cwd}/{pfile}"

    if asc_file == "":
        ferror("No asc file!")
        return -1 # quit


    # Any time a point is added to the schematic, this function should be called
    # for normalization
    def update_bounds(x, y):
        global lower_x, lower_y, upper_x, upper_y
        if x < lower_x:
            lower_x = x
        if upper_x < x:
            upper_x = x
        if y < lower_y:
            lower_y = y
        if upper_y < y:
            upper_y = y

    # This may be called to adjust the size of the schematic,
    # to avoid clipping
    def adjust_bounds():
        global lower_x, lower_y, upper_x, upper_y
        lower_x -= svg_content_border
        lower_y -= svg_content_border
        upper_x += svg_content_border
        upper_y += svg_content_border

    # Every wire (tuple of floats) will be placed here
    pwires = []


    with open(asc_file, "r", encoding='ISO-8859-1') as fstream:
        lines = []
        # Cleanup all text lines
        for line in fstream:
            lines += [ line.replace("_", "\\_").replace("\n", "") ]

        # Parser:

        # Add all wires, and split wires at half-nodes
        for line in [ line for line in lines if "WIRE " == line[:5] ]:
            _, ux, uy, vx, vy = line.split()
            ux, uy, vx, vy = map(float, [ux, uy, vx, vy])
            u = (ux, uy)
            v = (vx, vy)

            pwires += [u, v]

            update_bounds(ux, uy)
            update_bounds(vx, vy)
            fprint(f"line {ux} {uy} {vx} {vy}")

        # Add all nodes
        for unique_node in set(pwires):
            count = pwires.count(unique_node)
            if 2 < count:
                fprint(f"node {unique_node[0]} {unique_node[1]} {2} {2}")

        # The rest of the functionality
        for line in lines:
            # Add all flags
            if "FLAG " == line[:5]:
                _, x, y, flag = line.split()
                x, y = map(float, [x, y])

                update_bounds(x, y)

                if flag == "0":
                    R, _ = hnode_dir([x, y], pwires)
                    lines += [f"SYMBOL ground {x} {y} {R}"]
                else:
                    _, T = hnode_dir([x, y], pwires)
                    if display_flags:
                        fprint(f"text {x} {y} {T} {2} ;{flag}")

            # Add all the text
            if "TEXT " == line[:5]:
                words = line.split()
                _, x, y, align, size = words[:5]
                text = " ".join(words[5:])
                x, y, sizef = map(float, [x, y, size])

                bottom_alignment = ("Bottom" in align) # Special case
                if '\\n' in text:
                    prefix = text[0]
                    text = text[1:]
                    text_lines = text.split('\\n')
                    K = len(text_lines)
                    for k, text_line in enumerate(text_lines):
                        if bottom_alignment:
                            k = k - K + 1
                        lines.append(f"TEXT {x} {y+k*15*sizef} {align} {size} {prefix+text_line}")
                else:
                    update_bounds(x, y)
                    fprint(f"text {x} {y} {align} {size} {text}")

            if "SYMATTR " == line[:8]:
                words = line.split()
                attribute = words[1]
                value = " ".join(words[2:])

                if attribute == "Value" and display_component_values:
                    if value_size != 0:
                        update_bounds(value_x, value_y)
                        fprint(f"text {value_x} {value_y} {value_align} {value_size} ;{value}")
                        value_x, value_y, value_align, value_size = 0, 0, "", 0

                if attribute == "InstName" and display_component_InstName:
                    if prefix_size != 0:
                        update_bounds(prefix_x, prefix_y)
                        fprint(f"text {prefix_x} {prefix_y} {prefix_align} {prefix_size} ;{value}")
                        prefix_x, prefix_y, prefix_align, prefix_size = 0, 0, "", 0


            # For every symbol, offset, rotate and align the lines and text within
            # Add these to the output
            if "SYMBOL " == line[:7]:
                _, symbol, x, y, rot = line.split()
                x_offset, y_offset = map(float, [x, y])
                symbol_x, symbol_y = x_offset, y_offset
                mirror = (rot[0] == "M")
                phi = pi/180*float(rot[1:])

                symbol = '/'.join(symbol.split('\\\\'))

                asy_file = f"{lib_filepath}sym/{symbol}.asy"

                # Further attributes may have to be added
                value_x, value_y, value_align, value_size = 0, 0, "", 0
                prefix_x, prefix_y, prefix_align, prefix_size = 0, 0, "", 0
                symbol_x, symbol_y = 0, 0

                affine = lambda p: add_vec(mirror_vec(mirror, rot_vec(phi, p)), [x_offset, y_offset])

                # Every type of primitive handled with dense but obvious code.
                # WINDOW/SYMATTR are dealt with over several cycles, which is
                # confusing and not obvious :D
                with open(asy_file, "r", encoding='ISO-8859-1') as f2stream:
                    for sline in f2stream:
                        if "WINDOW " == sline[:7]:
                            _, index, x, y, align, size = sline.split()
                            x, y = map(float, [x, y])
                            x, y = affine([x, y])

                            if mirror ^ (rot[1:] == "180"):
                                align = {"Left":"Right", "Right":"Left"}[align]
                            if (rot[1:] == "90"):
                                align = "VRight"
                            if (rot[1:] == "270"):
                                align = "VLeft"

                            if index == "0":
                                value_x = x
                                value_y = y
                                value_align = align
                                value_size = size
                            if index == "3":
                                prefix_x = x
                                prefix_y = y
                                prefix_align = align
                                prefix_size = size

                        if "LINE " == sline[:5]:
                            _, linetype, x0, y0, x1, y1 = sline.split()
                            x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
                            x0, y0 = affine([x0, y0])
                            x1, y1 = affine([x1, y1])
                            update_bounds(x0, y0)
                            update_bounds(x1, y1)
                            fprint(f"line {x0} {y0} {x1} {y1}")

                        if "RECT " == sline[:5]:
                            _, linetype, x0, y0, x1, y1 = sline.split()
                            x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
                            x0, y0 = affine([x0, y0])
                            x1, y1 = affine([x1, y1])
                            update_bounds(x0, y0)
                            update_bounds(x1, y1)
                            fprint(f"rect {x0} {y0} {x1} {y1}")

                        if "CIRCLE " == sline[:7]:
                            _, linetype, x0, y0, x1, y1 = sline.split()
                            x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
                            x0, y0 = affine([x0, y0])
                            x1, y1 = affine([x1, y1])
                            px = 0.5*(x0+x1)
                            py = 0.5*(y0+y1)
                            rx = abs(0.5*(x0-x1))
                            ry = abs(0.5*(y0-y1))

                            update_bounds(x0, y0)
                            update_bounds(x1, y1)
                            fprint(f"circle {px} {py} {rx} {ry}")

                        if "ARC " == sline[:4]:
                            _, linetype, x0, y0, x1, y1, x2, y2, x3, y3 = sline.split()
                            x0, y0, x1, y1, x2, y2, x3, y3 = map(float, [x0, y0, x1, y1, x2, y2, x3, y3])
                            x0, y0 = affine([x0, y0])
                            x1, y1 = affine([x1, y1])
                            x2, y2 = affine([x2, y2])
                            x3, y3 = affine([x3, y3])
                            px = 0.5*(x0+x1)
                            py = 0.5*(y0+y1)
                            rx = abs(0.5*(x0-x1))
                            ry = abs(0.5*(y0-y1))
                            a1 = arg(sub_vec([x2, y2], [px, py]))
                            a2 = arg(sub_vec([x3, y3], [px, py]))

                            x0 = px + rx*sin(a1)
                            y0 = py + ry*cos(a1)
                            x1 = px + rx*sin(a2)
                            y1 = py + ry*cos(a2)

                            angle = 180/pi*(a2 - a1)

                            angle_dir = '+' if mirror else '-'
                            large_arc = True

                            update_bounds(x0, y0)
                            update_bounds(x1, y1)
                            update_bounds(x2, y2)
                            update_bounds(x3, y3)
                            fprint(f"arc {x2} {y2} {x3} {y3} {rx} {ry} {angle} {large_arc} {angle_dir}")

    # The text output buffer will be reset, and normalized
    lines = text_output.split("\n")
    fclear()

    adjust_bounds() # To avoid clipping

    # Always normalizes the same in every direction,
    # makes every detail fit (often)
    if (upper_y - lower_y) < (upper_x - lower_x):
        d = (svg_file_width - 2*svg_content_border)/(upper_x - lower_x)
    else:
        d = (svg_file_height - 2*svg_content_border)/(upper_y - lower_y)

    # Reserve seperate scaling factors for the x  and y dimensions
    dx = d
    dy = d

    # Define the affine transformation which normalizes the schematic
    affine = lambda q: [dx*(q[0]-lower_x), dy*(q[1]-lower_y)]

    # Add every type of primitive to the output buffer, in order of complexity
    for line in lines:
        if "node " == line[:5]:
            _, x, y, rx, ry = line.split()
            x, y, rx, ry = map(float, [x, y, rx, ry])
            x, y = affine([x, y])
            rx *= dx
            ry *= dy
            fprint(f"node {x} {y} {rx} {ry}")
    for line in lines:
        if "line " == line[:5]:
            _, x0, y0, x1, y1 = line.split()
            x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
            x0, y0 = affine([x0, y0])
            x1, y1 = affine([x1, y1])
            fprint(f"line {x0} {y0} {x1} {y1}")
    for line in lines:
        if "rect " == line[:5]:
            _, x0, y0, x1, y1 = line.split()
            x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
            x0, y0 = affine([x0, y0])
            x1, y1 = affine([x1, y1])
            fprint(f"rect {x0} {y0} {x1} {y1}")
    for line in lines:
        if "circle " == line[:7]:
            _, px, py, rx, ry = line.split()
            px, py, rx, ry = map(float, [px, py, rx, ry])
            px, py = affine([px, py])
            rx *= dx
            ry *= dy
            fprint(f"circle {px} {py} {rx} {ry}")
    for line in lines:
        if "arc " == line[:4]:
            _, x0, y0, x1, y1, rx, ry, angle, large_arc, angle_dir = line.split()
            px, py, rx, ry = map(float, [px, py, rx, ry])
            x0, y0, x1, y1, rx, ry, angle = map(float, [x0, y0, x1, y1, rx, ry, angle])
            x0, y0 = affine([x0, y0])
            x1, y1 = affine([x1, y1])
            rx *= dx
            ry *= dy
            fprint(f"arc {x0} {y0} {x1} {y1} {rx} {ry} {angle} {large_arc} {angle_dir}")
    for line in lines:
        if "text " == line[:5]:
            words = line.split()
            _, x, y, align, size = words[:5]
            text = " ".join(words[5:])
            x, y, size = map(float, [x, y, size])
            x, y = affine([x, y])
            size = size*dy*font_scale
            fprint(f"text {x} {y} {align} {size} {text}")

    # Write to file
    with open("netlist.txt", "w", encoding='ISO-8859-1') as ostream:
        ostream.write(text_output)

main()
