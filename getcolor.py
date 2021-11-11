from PIL import Image, ImageDraw
import argparse
import sys

def get_colors(image_file, numcolors=30, resize=150):
	# Resize image to speed up processing
	img = Image.open(image_file)
	img = img.copy()
	img.thumbnail((resize, resize))

	# Reduce to palette
	paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)

	# Find dominant colors
	palette = paletted.getpalette()
	color_counts = sorted(paletted.getcolors(), reverse=True)
	colors = list()
	for i in range(numcolors):
		palette_index = color_counts[i][1]
		dominant_color = palette[palette_index*3:palette_index*3+3]
		colors.append(tuple(dominant_color))

	return colors

def save_palette(colors, swatchsize=20, outfile="palette.png" ):
	num_colors = len(colors)
	palette = Image.new('RGB', (swatchsize*num_colors, swatchsize))
	draw = ImageDraw.Draw(palette)

	posx = 0
	for color in colors:
		draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=color) 
		posx = posx + swatchsize

	del draw
	palette.save(outfile, "PNG")

def rgb_to_hex(rgb):
	return '%02x%02x%02x' % rgb

def get_palette(input_file, output_file, amount):
	colors = get_colors(input_file, numcolors=amount)
	save_palette(colors, outfile = output_file)
	palette = ""
	for color in colors:
		palette = palette + '#' + rgb_to_hex(color) + '\n'
	return palette
