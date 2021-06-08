# ltspice4-2-svg
Python code which make ltspice circuits into stylized SVG.

The only dependency is svgwrite (and my code uses os and sys).
The code runs with python 3.7, and ltspice with files that contain the text "Version 4" as the first line.

Both of the following programs import the config.py file where settings for the output file may be set.
First the file spice2prim.py is run with:

    python3.7 spice2prim.py

which takes a .asc file in the current working directory and produces the file "netlist.txt".
Secondly the file prim2svg.py is run with:

    python3.7 prim2svg.py

which takes the file "netlist.txt" and produces the file "test.svg".

My code doesn't try to resolve system paths, compatibility or anything. If it works it works :d

Github doesn't seem to be able to display the SVG. Perhaps the format is incorrect (something that the writesvg module might have function calls to remedy), but firefox is able to display this SVG. 

Before:

![alt text](/first.PNG)

After (pardon the hideous font):

![alt text](/second.PNG)
