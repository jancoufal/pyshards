#!/bin/env python3

import colorsys
import turtle

def main():
	colors = [
		"#FF5B00",
		"#FFFF00",
		"#2AFF00",
		"#01FFFF",
		"#00C6FF"
	]

	light_amount = 0.2
	lighten_colors = {c: lighten_rgb(c, light_amount) for c in colors}

	padding = 2
	square_size = 10
	turtle_init(turtle, padding, square_size, len(lighten_colors), 2)

	for y, light in enumerate([x * 0.1 for x in range(5)]):
		for x, c in enumerate(colors):
			lc = lighten_rgb(c, light)

			print(f"{light:0.1f}: {c!s} -> {lc!s}")

			turtle_draw_square(turtle, lc, padding + x * (square_size + padding), y * (padding + square_size), square_size)


	turtle.getscreen()._root.mainloop()


def turtle_init(t, padding, square_size, x_square_count, y_square_count):
	t.setup(
		width=10 * (padding + x_square_count * (square_size + padding)),
		height=10 * (padding + y_square_count * (square_size + padding)),
		startx=padding,
		starty=padding
	)
	t.setworldcoordinates(
		-padding,
		-padding,
		x_square_count * (square_size + padding),
		y_square_count * (square_size + padding),
	)
	t.penup()
	t.speed(0)
	t.reset()
	t.degrees()
	t.setheading(0)


def turtle_draw_square(t, color, x, y, size):
	t.goto(x, y)
	t.pencolor("#000000")
	t.fillcolor(color)
	t.pendown()
	t.begin_fill()
	for _ in range(4):
		t.forward(size)
		t.right(90)
	t.end_fill()
	t.penup()


def lighten_rgb(hexcode, light_amount):
	c = hex_to_byte_rbg(hexcode)
	c = normalize_byte_to_float(c)
	c = colorsys.rgb_to_hls(*c)
	c = truncate_values(c)
	c[1] += light_amount
	c = colorsys.hls_to_rgb(*c)
	c = truncate_values(c)
	c = normalize_float_to_byte(c)
	c = byte_rgb_to_hex(c)
	return c


def hex_to_byte_rbg(hexcode):
	return int(hexcode[1:3], 16), int(hexcode[3:5], 16), int(hexcode[5:7], 16)


def byte_rgb_to_hex(rgb):
	return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def normalize_byte_to_float(bytes):
	return list(map(lambda b: b / 255.0, bytes))


def normalize_float_to_byte(floats):
	return list(map(lambda f: int(f * 255), floats))


def truncate_values(values):
	factor = 1000
	return list(map(lambda v: int(v * factor) / factor, values))

if __name__ == '__main__':
	main()
