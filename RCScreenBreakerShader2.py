import wx
import pygame
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
from ctypes import sizeof, c_float, c_void_p
from random import randint
import time

#setup pygame
pygame.init()
pygame.display.set_mode((0, 0), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)

#setup wx
app = wx.App()

#global variables
running = True


vertexShaderSource = """
#version 330

layout(location = 0) in vec2 pos;
layout(location = 1) in vec2 uvIn;

out vec2 uv;

void main() {
	gl_Position = vec4(pos, 0, 1);
	uv = uvIn;
}
"""

fragmentShaderSource = """
#version 330

uniform sampler2D tex;
uniform float colPos;
uniform float colOffset;
uniform float rowOffset;
uniform vec2 size;

in vec2 uv;

out vec4 fragColor;

void main() {
	if (uv.x >= colPos / size.x && uv.x < (colPos + colOffset) / size.x) {
		fragColor = texture(tex, vec2(uv.x, mod(uv.y + (rowOffset / size.y), size.y)));
		//fragColor = vec4(1.0);
	} else {
		fragColor = texture(tex, uv);
		//fragColor = vec4(0.0);
	}
}
"""


def takeScreenshot():
	screen = wx.ScreenDC()
	size = screen.GetSize()

	bmp = wx.Bitmap(size[0], size[1])
	mem = wx.MemoryDC(bmp)
	mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
	del mem

	image = pygame.image.frombuffer(bmp.ConvertToImage().GetData(), size, "RGB")

	return image

def createProgram(image, vertexShaderSource, fragmentShaderSource):

	width = image.get_width()
	height = image.get_height()
	imageData = pygame.image.tostring(image, "RGBA", True)
	
	vertexPositionAttributeLocation = 0
	uvAttributeLocation = 1
	mipMapLevel = 0

	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)

	vertexData = np.array([-1, -1, 0, 0,  -1, 1, 0, 1,  1, 1, 1, 1,  -1, -1, 0, 0,  1, 1, 1, 1,  1, -1, 1, 0], np.float32)
	glBufferData(GL_ARRAY_BUFFER, vertexData, GL_STATIC_DRAW)

	glVertexAttribPointer(vertexPositionAttributeLocation, 2, GL_FLOAT, GL_FALSE, sizeof(c_float) * 4, c_void_p(0))
	glEnableVertexAttribArray(0)
	glVertexAttribPointer(uvAttributeLocation, 2, GL_FLOAT, GL_FALSE, sizeof(c_float) * 4, c_void_p(sizeof(c_float) * 2))
	glEnableVertexAttribArray(1)

	imageTexture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, imageTexture)

	glTexImage2D(GL_TEXTURE_2D, mipMapLevel, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imageData)

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

	vertexShader = shaders.compileShader(vertexShaderSource, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragmentShaderSource, GL_FRAGMENT_SHADER)

	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)

	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	return shaderProgram, imageTexture

def render(program, args):
	glUseProgram(program)

	colPosPos = glGetUniformLocation(program, "colPos")
	colOffsetPos = glGetUniformLocation(program, "colOffset")
	rowOffsetPos = glGetUniformLocation(program, "rowOffset")
	sizePos = glGetUniformLocation(program, "size")

	glUniform1f(colPosPos, args[0])
	glUniform1f(colOffsetPos, args[1])
	glUniform1f(rowOffsetPos, args[2])
	glUniform2f(sizePos, args[3], args[4])

	glDrawArrays(GL_TRIANGLES, 0, 6)

def renderBuffer(program, buf, size, args):
	mipMapLevel = 0

	texPos = glGetUniformLocation(program, "tex")

	imageTexture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, imageTexture)

	glTexImage2D(GL_TEXTURE_2D, mipMapLevel, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, buf)

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

	glUniform1i(texPos, 0)

	render(program, args)

	glDeleteTextures(imageTexture)

def renderImage(program, image, args):
	size = (image.get_width(), image.get_height())
	buf = pygame.image.tostring(image, "RGBA", True)

	renderBuffer(program, buf, size, args)	

def mainloop(identifier, args, size, buf=None):
	global running

	width = size[0]
	height = size[1]
	usesBuffer = buf is not None

	possibles = globals().copy()
	possibles.update(locals())
	loop = possibles.get(identifier)
	if not loop:
		raise NotImplementedError("Method %s not implemented" % loop)

	timeArray = []

	while running:

		t1 = time.perf_counter()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: # or event.unicode == 'q':
					running = False

		if usesBuffer:
			loop(buf, args)
			buf = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
			#buf = pygame.display.get_surface().get_buffer().raw #may be a faster option, currently doesn't work
		else:
			loop(args)
		pygame.display.flip()

		t2 = time.perf_counter()
		timeArray.append(t2 - t1)

	tAll = 0
	for t in timeArray:
		tAll= tAll + t
	print()
	print(str(len(timeArray)) + " runs")
	print("average time per run: " + str(tAll / len(timeArray)))

	running = True

def demo1(args):
	program = args[0]
	size = args[1]
	image = args[2]
	values = args[3]

	values[0] = (values[0] + values[1]) % size[0]
	values[1] = randint(30, 50)
	values[2] = randint(50, 100)

	renderImage(program, image, values)
	#time.sleep(0.15)

def demo2(buf, args):
	program = args[0]
	size = args[1]
	values = args[2]

	values[0] = (values[0] + values[1]) % size[0]
	values[1] = randint(30, 50)
	values[2] = randint(50, 100)

	renderBuffer(program, buf, size, values)
	#time.sleep(0.15)

def static(args):
	program = args[0]
	size = args[1]
	values = args[2]

	values[0] = (values[0] + values[1]) % size[0]
	values[1] = randint(30, 50)
	values[2] = randint(50, 100)

	render(program, values)
	#time.sleep(0.15)

def refreshing(buf, args):
	program = args[0]
	size = args[1]
	values = args[2]

	values[0] = (values[0] + values[1]) % size[0]
	values[1] = randint(30, 50)
	values[2] = randint(50, 100)

	renderBuffer(program, buf, size, values)
	#time.sleep(0.15)

def main():
	global running, vertexShaderSource, fragmentShaderSource

	image = takeScreenshot()
	buf = pygame.image.tostring(image, "RGBA", True)
	
	backup = pygame.image.load("Background.jpg")
	backupBuf = pygame.image.tostring(backup, "RGBA", True)

	width = image.get_width()
	height = image.get_height()
	size = (width, height)

	args = [0, 0, 0, width, height] #column number, column offset, row offset, width, height

	glViewport(0, 0, width, height)

	program, texture = createProgram(image, vertexShaderSource, fragmentShaderSource)
	render(program, args)

	mainloop("demo1", (program, size, backup, args), size)
	mainloop("demo2", (program, size, args), size, backupBuf)
	#mainloop("static", (program, size, args), size)
	#mainloop("refreshing", (program, size, args), size, buf)

	glDeleteProgram(program)
	glDeleteTextures(texture)
	pygame.quit()


main()