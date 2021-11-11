# kolor-generator

![Screenshot](screenshot.png)

This script generates a KDE Plasma color scheme from an image. It automatically generates a color palette and inserts it into a new color scheme. It also outputs a String to be pasted into your terminator config.

Requires [Python 3](https://www.python.org/).

# Basic usage

Clone this repository in a directory of your choice.

Then **run the command**:

`python generator.py generate-all IMAGE_DIR RESOLUTION`

The `IMAGE_DIR` is the directory containing all the Imgaes you wish to create color schemes for. The `RESOLUTION`is the number of probes to take from the Image. The higher the resolution, the closer the color scheme will be to the templates.
This will generate a Plasma color theme for each image located inside the specified directory and will place them in `~/.local/share/color-schemes/`. It will also output a String for each Image, to be pasted in `~/.config/terminator/config`. Now you just need to go to *System Settings -> Colors* to select the color scheme just created.

If you want to generate the color scheme **just for one specific Image**, run:

`python generator.py generate PATH_TO_FILE RESOLUTION`

If you want to generate a **light color scheme**, put `-l` at the end of the command:

`python generator.py generate-all IMAGE_DIR RESOLUTION -l`

# How does it (simply) work

The script uses the two files "template-dark" and "template-light" to generate respectively dark and light schemes. For terminator schemes the default shell colors are used as reference.

It does so by replacing each color with the closest color from the palette obtained from the Image.

This means that the colors in the template affect the final result, which depends also on the number and variety of colors in the Image palette.
