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

	shaders.compileShader(source, shader_type)

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
	glUniform1f(timeLocation,time)
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
	fragment = create_shader(GL_FRAGMENT_SHADER, """
uniform float time;
uniform vec2 resolution;
// based on https://www.shadertoy.com/view/MtBGDW
#define FIELD 5.0
#define CHANNEL bvec3(true, true, true)
#define TONE vec3(0.299,0.587,0.114)

vec2 pieuvreEQ(vec3 p,float t){
	vec2 fx = p.xy;
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x*=fx.x*0.1;
	return fx;}

vec3 computeColor(vec2 fx) {
	vec3 color = vec3(CHANNEL) * TONE;
	color -= fx.x;
	color.b += color.g*1.5;
	return clamp(color,0.0,1.0);
}

void main(void) {
	float ratio = resolution.y / resolution.x;
	gl_FragCoord.y *= ratio;
	vec2 position = (gl_FragCoord.xy / resolution.xy) - vec2(0.5, 0.6 * ratio);
	vec3 p = position.xyx * FIELD;
	vec3 color = vec3(0.0, 0.0, 0.2);
	
	color += computeColor(pieuvreEQ(p * 2.5, time));
	gl_FragColor = vec4(color, 1.0);
}
	""")
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
