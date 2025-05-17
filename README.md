# LINUS
“Linus” is a 2D-drawing machine which uses a marker to draw inputted images in the one-line-drawing art style!  
  
[Project Website](https://sidharthmrao.github.io/LINUS/index.html)  
  
### Directory Structure
#### cad
Contains CAD step files.

#### docs
Contains files for the project website.

#### exp
Contains experimentation files for image processing and pathfinding.

#### input
Contains input images

#### lib
 - graph.py - Contains graph datastructures and algorithms
 - render.py - Tools for Pygame rendering
 - serial_com.py - UART communication between Host device and microcontroller
 - skeleton.py - Image processing and skeletonization
 - slicer.py - Optimal path construction

#### pico
 - Contains files to run on the Raspberry Pi Pico for printer control and communication

#### config.py
 - Configuration file, select input image, activate debug mode, etc.

### Running Locally
To run locally, create a Python 3.13 environment using the `requirements.txt`.  
Edit `config.py` as necessary.   
Source it and then run `main.py`.