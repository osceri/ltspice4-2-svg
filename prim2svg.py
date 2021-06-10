#!/usr/bin/env python
# -*- coding: ascii -*-
import svgwrite
from config import *

def main():
    # Create output file. Make sure that the size in this file is
    # equal to the parameters in the other file. WILL fix
    dwg = svgwrite.Drawing("test.svg", size=(svg_file_width, svg_file_height))
    
    # The style of the schematic is derived from the css file
    dwg.add_stylesheet('style.css', title="Circuit style")
    
    # One may define seperate styles/classes for every primitive
    # Therefore these groups are created
    nodes = dwg.g(class_="line")
    lines = dwg.g(class_="line")
    rects = dwg.g(class_="line")
    circles = dwg.g(class_="line")
    arcs = dwg.g(class_="line")
    texts = dwg.g(class_="text")
    comments = dwg.g(class_="comment")
    
    # The netlist file in the local directory is opened, and the primitives are added
    # to their corresponding groups
    with open("netlist.txt", "r", encoding='ISO-8859-1') as netlist:
        for line in netlist:
            if "node " == line[:5]:
                _, x, y, rx, ry = line.split()
                x, y, rx, ry = map(float, [x, y, rx, ry])
                nodes.add(dwg.ellipse(center=(x, y), r=(rx, ry)))
            if "line " == line[:5]:
                _, x0, y0, x1, y1 = line.split()
                x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
                lines.add(dwg.line(start=(x0, y0), end=(x1, y1)))
            if "rect " == line[:5]:
                _, x0, y0, x1, y1 = line.split()
                x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
                lines.add(dwg.line(start=(x0, y0), end=(x1, y0)))
                lines.add(dwg.line(start=(x0, y0), end=(x0, y1)))
                lines.add(dwg.line(start=(x1, y1), end=(x1, y0)))
                lines.add(dwg.line(start=(x1, y1), end=(x0, y1)))
            if "circle " == line[:7]:
                _, px, py, rx, ry = line.split()
                px, py, rx, ry = map(float, [px, py, rx, ry])
                circles.add(dwg.ellipse(center=(px, py), r=(rx, ry), style="fill:none"))
            if "arc " == line[:4]:
                _, x0, y0, x1, y1, rx, ry, angle, large_arc, angle_dir = line.split()
                x0, y0, x1, y1, rx, ry, angle = map(float, [x0, y0, x1, y1, rx, ry, angle])
                large_arc = (large_arc == "True")
                path = svgwrite.path.Path(d=("M", x0, y0), stroke="black", fill="none")
                path.push_arc(target=(x1, y1), r=(rx, ry), rotation=angle, large_arc=large_arc, angle_dir=angle_dir, absolute=True)
                arcs.add(path)
            # Text needs extra attention because anchoring, rotation and position is tricky
            if "text " == line[:5]:
                words = line.split()
                _, x, y, align, size = words[:5]
                text = " ".join(words[5:])
                is_comment = ("!" == text[0])
                text = text[1:]

                x, y = map(float, [x, y])
                size = round(10*float(size))

                x_offset = 0
                y_offset = 0
                vertical = False
    
                # The align-flag may have any number of direction/orientation-tokens preceding the
                # Bottom and Top don't exist. They're just offset Center
                align = align.replace('Bottom', 'uuCenter')
                align = align.replace('Top', 'ddCenter')

                # actual alignment.
                while True:
                    token = align[0]
                    if token == "u":
                        y_offset -= size // 4
                    elif token == "d":
                        y_offset += size // 4
                    elif token == "l":
                        x_offset -= size // 4
                    elif token == "r":
                        x_offset += size // 4
                    elif token == "V":
                        vertical = True
                    else:
                        break
                    align = align[1:]
    
                align = {"Center":"middle", "Left":"start", "Right":"end"}[align]
    
                # This is added simply to make alignment slightly better
                if vertical:
                    x_offset += size // 4
                else:
                    y_offset += size // 4
    
                x += x_offset
                y += y_offset
    
                if is_comment:
                    comments.add(dwg.text(text, insert=(x, y), style=f"text-anchor:{align};font-size:{size}px", transform=f"rotate({-90 if vertical else 0},{x},{y})"))
                else:
                    texts.add(dwg.text(text, insert=(x, y), style=f"text-anchor:{align};font-size:{size}px", transform=f"rotate({-90 if vertical else 0},{x},{y})"))
    
    
    # The primitive groups are added to the SVG
    dwg.add(lines)
    dwg.add(rects)
    dwg.add(arcs)
    if display_text:
        dwg.add(texts)
        if display_comments:
            dwg.add(comments)
    dwg.add(circles)
    if display_nodes:
        dwg.add(nodes)
    
    # The SVG file is saved!
    dwg.save()

main()
