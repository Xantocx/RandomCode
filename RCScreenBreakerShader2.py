import wx
import pygame
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
from ctypes import sizeof, c_float, c_void_p
import os

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

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = vec4(texture(tex, uv).xy, 0.0, 1.0);
}
"""


def takeScreenshot(name):
    screen = wx.ScreenDC()
    size = screen.GetSize()

    bmp = wx.Bitmap(size[0], size[1])
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
    del mem
    bmp.SaveFile(name, wx.BITMAP_TYPE_PNG)

    image = pygame.image.load(name)
    os.remove(name)
    return image

def renderImage(image):
    global vertexShaderSource, fragmentShaderSource

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
    glVertexAttribPointer(uvAttributeLocation, 2, GL_FLOAT, GL_FALSE, sizeof(c_float)*4, c_void_p(sizeof(c_float) * 2))
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

    glUseProgram(shaderProgram)

    glDrawArrays(GL_TRIANGLES, 0, 3)

def main():
    global running

    imageName = 'screenshot.png'

    image = takeScreenshot(imageName)
    original = image.copy()

    #image = pygame.image.load("Background.jpg")

    width = image.get_width()
    height = image.get_height()

    glViewport(0, 0, width, height)

    #renderImage(image)
    #pygame.display.flip()

    while running:

        renderImage(image)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # or event.unicode == 'q':
                    running = False

    pygame.quit()


main()