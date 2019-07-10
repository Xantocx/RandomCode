import wx
import pygame
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
from ctypes import sizeof, c_float, c_void_p
import time
from PIL import Image

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
uniform float zValue;

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = vec4(texture(tex, uv).xy, zValue, 1.0);
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

def pygame2PIL(image):
    imageData = pygame.image.tostring(image, "RGBA", True)
    return Image.frombytes("RGBA", image.get_width(), image.get_height(), imageData)

def createProgram(image):
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

    return shaderProgram

def render(program, values):
    glUseProgram(program)

    zValuePos = glGetUniformLocation(program, "zValue")
    glUniform1f(zValuePos, values[0])

    glDrawArrays(GL_TRIANGLES, 0, 6)

def renderImage(program, image, values):
    width = image.get_width()
    height = image.get_height()
    mipMapLevel = 0

    imageData = pygame.image.tostring(image, "RGBA", True)

    texPos = glGetUniformLocation(program, "tex")

    imageTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, imageTexture)

    glTexImage2D(GL_TEXTURE_2D, mipMapLevel, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imageData)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glUniform1i(texPos, 0)

    render(program, values)

def main():
    global running

    image = takeScreenshot()
    currentImage = image
    backup = pygame.image.load("Background.jpg")

    width = image.get_width()
    height = image.get_height()
    size = (width, height)

    glViewport(0, 0, width, height)

    program = createProgram(image)

    values = [0]

    render(program, values)

    timeArray = []

    while running:
        t1 = time.perf_counter()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # or event.unicode == 'q':
                    running = False

        if values[0] < 0.2:
            render(program, values)
        else:
            renderImage(program, backup, values)

        #renderImage(program, currentImage, values)

        surface = pygame.display.get_surface()
        currentImage = pygame.image.frombuffer(surface.get_buffer(), surface.get_size(), "RGBA") #different thread, so I cannot contol it
        
        #currentScreen = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        #currentPILImage = Image.frombuffer("RGBA", size, currentScreen, "raw", "RGBA", 0, 0).rotate(180)
        #currentImage = pygame.image.frombuffer(currentPILImage.getdata(), size, "RGBA", True)

        pygame.display.flip()

        values[0] = values[0] + 0.001

        t2 = time.perf_counter()
        timeArray.append(t2 - t1)

    tAll = 0
    for t in timeArray:
        tAll= tAll + t
    print()
    print(tAll / len(timeArray))

    pygame.quit()


main()