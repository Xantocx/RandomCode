from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

from ctypes import *
from math import *
import pygame
import random
import time
import numpy
import wx
from PIL import Image

app = wx.App()

vertexShaderSource = [
"#version 330 core\n\n",

"layout(location=0) in vec2 in_vertex; ",

"out vec2 v_vertex; ",

"void main() { ",
"	gl_Position = vec4(in_vertex, 0.0, 1.0); "
"	v_vertex = in_vertex; "
"} "
]

fragmentShaderSource = [
"#version 330 core\n\n",

"uniform sampler2D texture; "

"in vec2 v_vertex; ",

"layout(location = 0) out vec3 out_color; ",

"void main(void) { ",
	"out_color = vec3(vec3(texture2D(texture, v_vertex)).xy, 0.0); ",
"}"
]

running = True
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.OPENGL|pygame.DOUBLEBUF|pygame.FULLSCREEN)

glClearColor(0.0, 0.0, 0.0, 1.0)
glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def createShader(shaderType, shaderSource):
	shader = glCreateShader(shaderType)
	# PyOpenGL bug ? He's waiting for a list of string, not a string
	# on some card, it failed :)
	if isinstance(shaderSource, str):
		source = [shaderSource]
	glShaderSource(shader, shaderSource)
	glCompileShader(shader)

	message =  glGetShaderInfoLog(shader)
	print('Shader: shader message: %s' % message)

	return shader


def main():
	global running
	
	screen = wx.ScreenDC()
	size = screen.GetSize()

	bmp = wx.Bitmap(size[0], size[1])
	mem = wx.MemoryDC(bmp)
	mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
	del mem
	screendata = bmp.ConvertToImage().GetData()

	screenbuffer = glGenFramebuffers(1)
	glBindFramebuffer(GL_FRAMEBUFFER, screenbuffer)
	glDrawBuffer(GL_COLOR_ATTACHMENT0)

	screentexture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, screentexture)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_FLOAT, screentexture)
	glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, texture, 0)

	glBindFramebuffer(GL_FRAMEBUFFER, screenbuffer)

	screenshot = glReadPixels(0, 0, size[0], size[1], GL_RGBA, GL_UNSIGNED_BYTE)
	Image.frombuffer("RGBA", (size[0], size[1]), screenshot, "raw", "RGBA", 0, 0).show()

	#create framebuffer
	fbo = glGenFramebuffers(1)
	glBindFramebuffer(GL_FRAMEBUFFER, fbo)
	glDrawBuffer(GL_COLOR_ATTACHMENT0)

	texture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texture)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_FLOAT, screenshot)

	glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
	glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
	glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, texture, 0)

	#build shaders
	vertexShader = createShader(GL_VERTEX_SHADER, vertexShaderSource)
	fragmentShader = createShader(GL_FRAGMENT_SHADER, fragmentShaderSource)

	#build program
	program = glCreateProgram()
	glAttachShader(program, vertexShader)
	glAttachShader(program, fragmentShader)
	glBindAttribLocation(program, 0, b"in_vertex")
	glLinkProgram(program)

	locationTexture = glGetUniformLocation(program, "texture");

	glUniform1i(locationTexture, fbo) # 0 should be refference for framebuffer

	try:
		glUseProgram(program)
	except OpenGL.error.GLError:
		print(glGetProgramInfoLog(program))
		raise

	#mainloop
	while running:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: # or event.unicode == 'q':
					running = False

	pygame.quit()

main()