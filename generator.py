import re
import sys
import os
import getcolor
from math import sqrt

COLOR_SCHEME_DIR = os.path.expanduser('~') + '/.local/share/color-schemes/'

class Color:
	def __init__(self, col):
		if re.match('.+,.+,.+', col):
			rgb = [int(c) for c in col.split(',')]
		else:
			rgb = [int(col[i:i+2], 16) for i in range(0, 6, 2)]
		self.r, self.g, self.b = rgb

	def distance(self, other):
		return sqrt((self.r-other.r)**2 + (self.g-other.g)**2 + (self.b-other.b)**2)

	def closest(self, palette):
		closest_distance = None
		closest_color = None
		for color in palette.colors:
			distance = self.distance(color)
			if closest_distance is None or distance < closest_distance:
				closest_distance = distance
				closest_color = color
		return closest_color

	def get_text(self, hex=False):
		if hex:
			return '#{:0>6}'.format(format(self.r*16**4 + self.g*16**2 + self.b, 'x'))
		else:
			return '{},{},{}'.format(self.r, self.g, self.b)


class Palette:
	def __init__(self, xres):
		self.colors = []
		for line in xres.splitlines():
			if re.match('#.*', line):
				self.colors.append(Color(line.split('#')[1]))


class Line:
	def __init__(self, text):
		if re.match('.*=.*', text) and re.match('.+,.+,.+', text.split('=')[1]):
			self.prefix = text.split('=')[0] + '='
			self.color = Color(text.split('=')[1])
		elif re.match('.*#[0-9A-Fa-f]{6}.*', text):
			self.prefix = text.split('#')[0]
			self.color = Color(text.split('#')[1])
		elif re.match('#[0-9A-Fa-f]{6}', text):
			self.prefix = text.split('#')[0]
			self.color = Color(text.split('#')[1])
		else:
			self.prefix = text
			self.color = None

	def matches(self, regexp):
		return re.match(regexp, self.prefix)

	def change_val(self, new):
		self.prefix = self.prefix.split('=')[0] + '=' + new

	def set_palette(self, palette):
		if self.color is not None:
			self.color = self.color.closest(palette)

	def get_text(self, hex=False):
		return self.prefix if self.color is None else self.prefix + self.color.get_text(hex)


class Document:
	def __init__(self, text):
		self.lines = [Line(line) for line in text.splitlines()]

	def get_document(self, hex=False):
		return '\n'.join([line.get_text(hex) for line in self.lines])

	def change_theme_name(self, name):
		for line in self.lines:
			if line.matches('ColorScheme=.*') or line.matches('Name=.*'):
				line.change_val(name)

	def set_palette(self, palette):
		for line in self.lines:
			line.set_palette(palette)

	def to_file(self, path, hex=True):
		with open(path, 'w') as f:
			f.write(self.get_document(hex))


op = sys.argv[1]

# python generator.py generate-all dir resolution (opt -l)
if op == 'generate-all':
	try:
		light = sys.argv[4] == '-l'
	except:
		light = False
	template_name = 'template-light' if light else 'template-dark'
	with open(template_name, 'r') as f:
		template = f.read()
	with open('terminator.template', 'r') as f:
		terminator = f.read()
	with open('st.template', 'r') as f:
		st = f.read()
	for file_name in os.listdir(sys.argv[2]):
		if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
			theme_name = re.sub('\\.[a-z]*', '', file_name)
			doc = Document(template)
			pal = Palette(getcolor.get_palette(sys.argv[2] + file_name, theme_name + ".png", int(sys.argv[3])))
			doc.set_palette(pal)
			suffix = ' light' if light else ' dark'
			doc.change_theme_name(theme_name + suffix)
			doc.to_file(COLOR_SCHEME_DIR + theme_name + suffix + '.colors')
			#set Terminal themes
			doc = Document(st)
			doc.set_palette(pal)
			suffix = ' light' if light else ' dark'
			with open(theme_name + suffix + '.st.template', 'w') as f:
				f.write(re.sub(',\n}', '\n}', re.sub(r'(#[0-9A-Fa-f]{6})(\n)', r'\1",\2', doc.get_document(hex))))
			doc = Document(terminator)
			doc.set_palette(pal)
			print('Terminator String (paste in ~/.config/terminator/config):')
			print('palette = \"' + re.sub('\n', ':', doc.get_document(hex)) + '\"')
	print('Done')

# python generator.py generate image-path resolution (opt -l)
if op == 'generate':
	try:
		light = sys.argv[4] == '-l'
	except:
		light = False
	template_name = 'template-light' if light else 'template-dark'
	image_name = re.sub('\\.[a-z]*', '', re.sub('.*/', '', sys.argv[2]))
	palette = Palette(getcolor.get_palette(sys.argv[2], image_name + ".png", int(sys.argv[3])))
	with open(template_name, 'r') as f:
		doc = Document(f.read())
	doc.set_palette(palette)
	suffix = ' light' if light else ' dark'
	doc.change_theme_name(image_name + suffix)
	doc.to_file(COLOR_SCHEME_DIR + image_name + suffix + '.colors')
	with open('st.template', 'r') as f:
		doc = Document(f.read())
	doc.set_palette(palette)
	suffix = ' light' if light else ' dark'
	with open(image_name + suffix + '.st.template', 'w') as f:
		f.write(re.sub(',\n}', '\n}', re.sub(r'(#[0-9A-Fa-f]{6})(\n)', r'\1",\2', doc.get_document(hex))))
	with open('terminator.template', 'r') as f:
		doc = Document(f.read())
	doc.set_palette(palette)
	print('Terminator String (paste in ~/.config/terminator/config):')
	print('palette = \"' + re.sub('\n', ':', doc.get_document(hex)) + '\"')
	print('Done')

# python scheme-generator.py copy-hex theme
if op == 'copy-hex':
	name = sys.argv[2]
	path = name + '.colors'
	with open(path, 'r') as f:
		doc = Document(f.read())
	doc.to_file(name + '-hex', hex=True)
	print('Done')

# python generator.py hex2theme theme
if op == 'hex2theme':
	name = sys.argv[2]
	path = name + '-hex'
	with open(path, 'r') as f:
		doc = Document(f.read())
	doc.to_file(name + '.colors')
	print('Done')
