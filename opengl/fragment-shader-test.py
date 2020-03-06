# -*- coding: utf-8 -*-
# from https://youtu.be/8GoRPDXHq_Y

# pip install PyOpenGL-3.1.5-cp38-cp38-win32.whl
# pip install PyOpenGL_accelerate-3.1.5-cp38-cp38-win32.whl

import logging
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *

settings = {
	"logging": {
		"level": logging.DEBUG,
		"format": "%(asctime)s - %(levelname)s : %(message)s",
		"datefmt": "%Y-%m-%d %H:%M:%S",
	},
}

time = 0.0
log = None
shaderHolder = None


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
	shaderHolder.update_uniform_time((time, ))
	glRecti(-1, -1, 1, 1)
	glutSwapBuffers()


def main():
	logging.basicConfig(**settings['logging'])

	global log
	log = logging.getLogger(__name__)

	glutInit()
	w, h = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
	glutInitWindowSize(w//2, h//2)
	glutInitWindowPosition(w//4, h//4)
	glutCreateWindow(b"PyOpenGL")
	glutDisplayFunc(draw)
	glutIdleFunc(draw)
	glutTimerFunc(100, timer, 0)

	global shaderHolder
	shaderHolder = ShaderHolder(
		logger=log,
		shader_type=GL_FRAGMENT_SHADER,
		shader_file="fragment-shader-test.shader",
		time_value=(0.0, ),
		resolution=(w/2, h/2)
	)

	glutMainLoop()


class ShaderUniformHolder(object):
	def __init__(self, gl_program, uniform_name, gl_uniform_function, init_value):
		self._gl_program = gl_program
		self.name = uniform_name
		self.gl_location = glGetUniformLocation(self._gl_program, self.name)
		self.gl_func = gl_uniform_function
		self.value = init_value
		self.update(self.value)

	def update(self, new_value):
		self.gl_func(self.gl_location, *new_value)
		self.value = new_value


class ShaderHolder(object):
	def __init__(self, logger, shader_type, shader_file, time_value, resolution):
		self._logger = logger
		self._type = shader_type
		self._file = shader_file
		self._file_content = None
		self.gl_program = glCreateProgram()
		self.shader = None
		self.uniform_time = None
		self.uniform_resolution = None
		self._loc_time = None
		self._loc_res = None
		self.refresh_file(time_value, resolution)

	def refresh_file(self, time_value, resolution):
		if self._has_file_changed(new_source := self._file_load()):
			if (new_shader := self._create_shader(new_source)) is not None:
				# delete old shader (if present)
				if self.shader is not None:
					glDeleteShader(self.shader)
					self.shader = None
					self.uniform_time = None
					self.uniform_resolution = None

				glAttachShader(self.gl_program, new_shader)
				glLinkProgram(self.gl_program)
				# new_uniform_time = ShaderUniformHolder(self.gl_program, "time", glUniform1f, time_value)
				new_uniform_time = None
				# new_uniform_resolution = ShaderUniformHolder(self.gl_program, "resolution", glUniform2f, resolution)
				new_uniform_resolution = None
				glUseProgram(self.gl_program)

				self._file_content = new_source
				self.shader = new_shader
				self.uniform_time = new_uniform_time
				self.uniform_resolution = new_uniform_resolution

				# debug
				self._loc_time = glGetUniformLocation(self.gl_program, "time")
				self._loc_res = glGetUniformLocation(self.gl_program, "resolution")

				self.update_uniform_time(time_value)
				self.update_uniform_resolution(resolution)

	def update_uniform_time(self, new_time):
		self._logger.debug(f"{new_time=}")

		# if self.uniform_time is not None:
		# 	self.uniform_time.update(new_time)

		glUniform1f(self._loc_time, *new_time)

	def update_uniform_resolution(self, new_resolution):
		self._logger.debug(f"{new_resolution=}")

		glUniform2f(self._loc_res, *new_resolution)

	def _file_load(self):
		with open(self._file, "r") as fh:
			return fh.read()

	def _has_file_changed(self, new_file_content):
		return self._file_content is None or self._file_content != new_file_content

	def _create_shader(self, shader_source):
		try:
			return shaders.compileShader(shader_source, self._type)
		except shaders.ShaderCompilationError as e:
			error_message, shader_source, shader_type = e.args
			self._logger.error(f"ShaderCompilationError({error_message=})")
		return None


if __name__ == "__main__":
	main()
