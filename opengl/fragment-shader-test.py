# -*- coding: utf-8 -*-
# from https://youtu.be/8GoRPDXHq_Y

# pip install PyOpenGL-3.1.5-cp38-cp38-win32.whl
# pip install PyOpenGL_accelerate-3.1.5-cp38-cp38-win32.whl

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *

time = .0
timeLocation = None


def create_shader(shader_type, source):
	shader = glCreateShader(shader_type)
	glShaderSource(shader, source)
	glCompileShader(shader)

	# for error hunting
	# shaders.compileShader(source, shader_type)

	return shader


def timer(value):
	global time
	if time > 100.0:
		time = .0
	else:
		time += 0.1

	glutPostRedisplay()
	glutTimerFunc(10, timer, 0)


def draw():
	glClear(GL_COLOR_BUFFER_BIT)
	glUniform1f(timeLocation, time)
	glRecti(-1, -1, 1, 1)
	glutSwapBuffers()


def main():
	global timeLocation

	glutInit()
	w, h = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
	glutInitWindowSize(w//2, h//2)
	glutInitWindowPosition(w//4, h//4)
	glutCreateWindow(b"PyOpenGL")
	glutDisplayFunc(draw)
	glutIdleFunc(draw)

	with open("fragment-shader-test.shader", "r") as fh:
		fragment = create_shader(GL_FRAGMENT_SHADER, fh.read())

	program = glCreateProgram()
	glAttachShader(program, fragment)
	glLinkProgram(program)
	glutTimerFunc(100, timer, 0)
	timeLocation = glGetUniformLocation(program, "time")
	resolution = glGetUniformLocation(program, "resolution")
	glUseProgram(program)
	glUniform2f(resolution, w/2, h/2)
	glutMainLoop()


if __name__ == "__main__":
	main()
