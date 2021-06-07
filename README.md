# ltspice4-2-svg
Python code which make ltspice circuits into stylized SVG.

The only dependency is svgwrite (and my code uses os and sys).
The code runs with python 3.7.

First the file spice2prim.py is run with:

    python3.7 spice2prim.py

which takes a .asc file in the current working directory and produces the file "netlist.txt".
Secondly the file prim2svg.py is run with:

      python3.7 prim2svg.py

which takes the file "netlist.txt" and produces the file "test.svg".

My code doesn't try to resolve system paths, compatibility or anything. If it works it works :d


TODO:
Add support for aconfig file as to make the output of the programs more predictable/controlled
