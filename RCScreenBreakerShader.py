from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *

from ctypes import *
from math import *
import pygame
import random
import time
import numpy

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
	"out_color = vec3(texture2D(texture, v_vertex)); ",
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
	
	vertexShader = createShader(GL_VERTEX_SHADER, vertexShaderSource)
	fragmentShader = createShader(GL_FRAGMENT_SHADER, fragmentShaderSource)

	program = glCreateProgram()
	glAttachShader(program, vertexShader)
	glAttachShader(program, fragmentShader)
	glLinkProgram(program)

	locationTexture = glGetUniformLocation(program,"texture");

	try:
		glUseProgram(program)
	except OpenGL.error.GLError:
		print(glGetProgramInfoLog(program))
		raise

	#bind vertex buffer in variable with glBindAttribLocation?

	#create framebuffer containing image and bind it

	glUniform1i(locationTexture, 0) #0 should be refference for framebuffer

	while running:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: # or event.unicode == 'q':
					running = False

	pygame.quit()

main()