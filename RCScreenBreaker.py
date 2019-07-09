import sys
if sys.version_info[0] == 2:
    import Tkinter
    tkinter = Tkinter
else:
    import tkinter

import wx
from PIL import Image, ImageTk
from msvcrt import getch
from random import randint
import os

app = wx.App()

def takeScreenshot(name):
	screen = wx.ScreenDC()
	size = screen.GetSize()
	bmp = wx.Bitmap(size[0], size[1])
	mem = wx.MemoryDC(bmp)
	mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
	del mem
	bmp.SaveFile(name, wx.BITMAP_TYPE_PNG)

def callback(event):
	#not working...
	sys.exit(0)

def createRoot():
	root = tkinter.Tk()
	w, h = root.winfo_screenwidth(), root.winfo_screenheight()
	root.overrideredirect(1)
	root.geometry("%dx%d+0+0" % (w, h))
	root.focus_set()    
	root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
	#root.bind("<Escape>", callback)

	return root

def createCanvas(root):
	w, h = root.winfo_screenwidth(), root.winfo_screenheight()
	canvas = tkinter.Canvas(root, width=w, height=h)
	canvas.pack()
	canvas.configure(background='black')

	return canvas

def showPIL(root, canvas, pilImage):
	w, h = root.winfo_screenwidth(), root.winfo_screenheight()
	imgWidth, imgHeight = pilImage.size

	if imgWidth > w or imgHeight > h:
		ratio = min(w / imgWidth, h / imgHeight)
		imgWidth = int(imgWidth * ratio)
		imgHeight = int(imgHeight * ratio)
		pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)

	image = ImageTk.PhotoImage(pilImage)
	return image, canvas.create_image(w / 2, h / 2, image=image)

def processImageBreakingDown(image, lastColVal):
	pixels = image.load()

	maxColOffset = randint(15, 30)
	numCols = maxColOffset * 2 + 1 
	colValue = (lastColVal + maxColOffset) % (image.size[0] - 1)
	shift = randint(0, 100)

	if lastColVal % 2 == 1:
		shift = shift - maxColOffset
	else:
		shift = shift + maxColOffset

	for col in range(colValue - maxColOffset, colValue + maxColOffset):
		col = col % (image.size[0] - 1)
		for row in range(image.size[1] - 1, 0, -1):
			pixels[col, row] = pixels[col, (row - shift) % (image.size[1] - 1)]

		if lastColVal % 2 == 1:
			if col <= colValue:
				shift = shift + 1
			else:
				shift = shift - 1
		else:
			if col <= colValue:
				shift = shift - 1
			else:
				shift = shift + 1

	return image, colValue

def processImageVortex(image, step):
	pixels = image.load()

	backupImage = image.copy()
	backupPixels = backupImage.load()
	midCol = int(image.size[0] / 2)
	midRow = int(image.size[1] / 2)

	minCol = 0
	maxCol = 0
	minRow = 0
	maxRow = 0

	if step == 0:
		minCol = int(2 * midCol / 3) % (image.size[0] - 1)
		maxCol = (minCol + int(2 * midCol / 3)) % (image.size[0] - 1)
		minRow = int(2 * midRow / 3) % (image.size[1] - 1)
		maxRow = (minRow + int(2 * midRow / 3)) % (image.size[1] - 1)
		vortex(image, pixels, backupPixels, minCol, midCol, maxCol, minRow, midRow, maxRow, 3)

		step = 1
	elif step == 1:
		minCol = int(midCol / 3) % (image.size[0] - 1)
		maxCol = (minCol + int(2 * midCol / 3)) % (image.size[0] - 1)
		minRow = int(midRow / 3) % (image.size[1] - 1)
		maxRow = (minRow + int(4 * midRow / 3)) % (image.size[1] - 1)
		vortex(image, pixels, backupPixels, minCol, midCol, maxCol, minRow, midRow, maxRow, 3)

		minCol = int(4 * midCol / 3) % (image.size[0] - 1)
		maxCol = (minCol + int(2 * midCol / 3)) % (image.size[0] - 1)
		minRow = int(4 * midRow / 3) % (image.size[1] - 1)
		maxRow = (minRow + int(4 * midRow / 3)) % (image.size[1] - 1)
		vortex(image, pixels, backupPixels, minCol, midCol, maxCol, minRow, midRow, maxRow, 3)

		step = 0

	return image, step

def vortex(image, pixels, backupPixels, minCol, midCol, maxCol, minRow, midRow, maxRow, factor):
	rand = randint(-5, 5)
	factor = factor + rand

	for col in range(minCol, maxCol):
		for row in range(minRow, maxRow):
			if col <= midCol and row <= midRow:
				pixels[col, row] = backupPixels[(col + 2 * factor) % (image.size[0] - 1), (row - factor) % (image.size[1] - 1)]
			elif col > midCol and row <= midRow:
				pixels[col, row] = backupPixels[(col + 2 * factor) % (image.size[0] - 1), (row + factor) % (image.size[1] - 1)]
			elif col > midCol and row > midRow:
				pixels[col, row] = backupPixels[(col - 2 * factor) % (image.size[0] - 1), (row + factor) % (image.size[1] - 1)]
			else:
				pixels[col, row] = backupPixels[(col - 2 * factor) % (image.size[0] - 1), (row - factor) % (image.size[1] - 1)]

def processImageRandom(image):
	pixels = image.load()

	for col in range(image.size[0]):
		for row in range(int(image.size[1] / 10) + randint(0, int(9 * image.size[1] / 10)) - randint(0, 100)):
			#print(pixels[col, row])
			pixels[col, row] = (randint(0, 50), randint(150, 255), randint(0, 50))

	return image


#---> Add your image processor here as the ones above. Use this as as a starting point: <---#

def yourImageProcessor(image):
	pixels = image.load()

	#do stuff with the pixels 
	#2D array: pixels[column, row] = (r, g, b)
	#size: number of columns = pixels.size[0]; number of rows = pixels.size[1]

	return image

#-------------------------------------------------------------------------------------------#

def update(root):
	root.update_idletasks()
	root.update()

def main():
	imageName = 'screenshot.png'
	index = 0

	root = createRoot()
	canvas = createCanvas(root)

	takeScreenshot(imageName)
	pilImage = Image.open(imageName)

	image = pilImage.copy()
	pilImage.close()
	os.remove(imageName)
	pilImage = image.copy()
	original = image.copy()

	image, imagesprite = showPIL(root, canvas, pilImage)

	update(root)

	while True:

		#---> Add your image processor here and comment out all others <---#

		pilImage, index = processImageBreakingDown(pilImage, index)

		#pilImage, index = processImageVortex(pilImage, index)
		
		#pilImage = processImageRandom(original.copy())
		#pilImage = processImageRandom(pilImage)

		#------------------------------------------------------------------#

		image2 = ImageTk.PhotoImage(pilImage)
		canvas.itemconfig(imagesprite, image=image2)
		image = image2

		update(root)

main()