def l_system(iterations, system_description):
	def _l_system_impl(iteration, axiom, alphabet, rules, constants):
		if iteration < 1:
			return

		if axiom in alphabet:
			for a in rules[axiom]:
				if a in constants:
					yield a
				if a in alphabet:
					yield from _l_system_impl(iteration - 1, a, alphabet, rules, constants)

	yield from _l_system_impl(
		iterations,
		system_description['axiom'],
		system_description['alphabet'],
		system_description['rules'],
		system_description['constants']
	)


# l system description
l_system_hilbert_curve = {
	# l system
	'alphabet': 'ab',
	'constants': 'f+-',
	'axiom': 'a',
	'rules': {
		'a': '-bf+afa+fb-',
		'b': '+af-bfb-fa+'
	},

	# characteristics
	'line_segment_count': lambda iterations: 4 ** iterations - 1,
	'fractal_width_in_fragments': lambda iterations: 2 ** iterations - 1,

	# draw settings
	'segment_length': 3,
	'rotate_angle': 90,
}

l_system_koch_curve = {
	# l system
	'alphabet': 'f',
	'constants': 'f+-',
	'axiom': 'f',
	'rules': {
		'f': 'f+f-f-f+f',
	},

	# characteristics
	'line_segment_count': lambda iterations: iterations * 0,
	'fractal_width_in_fragments': lambda iterations: iterations * 0,

	# draw settings
	'segment_length': 3,
	'rotate_angle': 90,
}


class SimpleCommand(object):
	def __init__(self, fn, *args, **kwargs):
		self._fn = fn
		self._args = args
		self._kwargs = kwargs

	def execute(self):
		return self._fn(*self._args, **self._kwargs)


if __name__ == '__main__':

	import turtle

	# deepness
	iterations = 2

	# l system
	lsys = l_system_hilbert_curve
	# lsys = l_system_koch_curve

	# center the drawing
	half_width = lsys['fractal_width_in_fragments'](iterations) * lsys['segment_length'] / 2
	turtle.penup()
	turtle.setposition(-half_width, -half_width)
	turtle.pendown()

	# speed up the drawing & other settings
	turtle.speed('fastest')
	turtle.hideturtle()
	turtle.pencolor('black')

	# available commands
	commands = {
		'-': SimpleCommand(turtle.left, (lsys['rotate_angle'])),
		'+': SimpleCommand(turtle.right, (lsys['rotate_angle'])),
		'f': SimpleCommand(turtle.forward, (lsys['segment_length'])),
	}

	print_commands = {
		'-': SimpleCommand(print, ('-'), **{'end': ''}),
		'+': SimpleCommand(print, ('+'), **{'end': ''}),
		'f': SimpleCommand(print, ('f'), **{'end': ''}),
	}

	# read the command stream and execute
	for c in l_system(iterations, lsys):
		commands[c].execute()

	turtle.getscreen()._root.mainloop()
