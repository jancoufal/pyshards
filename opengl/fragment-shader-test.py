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
	shaderHolder.update_uniform("time", (time, ))
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
		uniform_descriptors=(
			ShaderUniformValueDescriptor("time", glUniform1f, (0.0, )),
			ShaderUniformValueDescriptor("resolution", glUniform2f, (w/2, h/2)),
		)
	)

	glutMainLoop()


class ShaderUniformValueDescriptor(object):
	def __init__(self, uniform_name, gl_uniform_function, value):
		self.name = uniform_name
		self.gl_func = gl_uniform_function
		self.init_value = value


class ShaderUniformHolder(object):
	def __init__(self, gl_location, value_descriptor):
		self._gl_location = gl_location
		self._descriptor = value_descriptor
		self.value = self._descriptor.init_value

	def update(self, new_value=None):
		self._descriptor.gl_func(self._gl_location, *(self.value if new_value is None else new_value))
		self.value = new_value


class ShaderHolder(object):
	def __init__(self, logger, shader_type, shader_file, uniform_descriptors):
		self._logger = logger
		self._type = shader_type
		self._file = shader_file
		self._file_content = None
		self.gl_program = glCreateProgram()
		self.shader = None
		self._uniform_descriptors = uniform_descriptors
		self._uniform_holders = dict()
		self.refresh_file()

	def refresh_file(self):
		if self._has_file_changed(new_source := self._file_load()):
			if (new_shader := self._create_shader(new_source)) is not None:
				# delete old shader (if present)
				if self.shader is not None:
					self._uniform_holders = list()
					glDeleteShader(self.shader)
					self.shader = None

				glAttachShader(self.gl_program, new_shader)
				glLinkProgram(self.gl_program)
				new_uniform_holders = {
					d.name: ShaderUniformHolder(glGetUniformLocation(self.gl_program, d.name), d)
					for d in self._uniform_descriptors
				}
				glUseProgram(self.gl_program)

				# init uniforms
				for h in new_uniform_holders.values():
					h.update()

				self._file_content = new_source
				self.shader = new_shader
				self._uniform_holders = new_uniform_holders

	def update_uniform(self, uniform_name, new_value):
		if uniform_name in self._uniform_holders.keys():
			self._uniform_holders[uniform_name].update(new_value)

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
