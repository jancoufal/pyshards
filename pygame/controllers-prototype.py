import pygame
from controllers.GameLoopState import GameLoopState
from controllers.Base import ControllerStaticValue
from controllers.Manager import ControllersManager
from controllers.Input import *
from controllers.Logic import *
from controllers.Function import *
from controllers.Filter import *
from controllers.Generator import *
from controllers.Trigger import *


def main():

	pygame.init()
	pygame.display.set_caption("minimal program")
	screen_rect = pygame.Rect(0, 0, 800, 600)
	screen_color = pygame.Color("#00000000")
	screen = pygame.display.set_mode(screen_rect.bottomright)

	hint_font = pygame.font.Font(pygame.font.get_default_font(), 32)
	hint_surface = hint_font.render("Press UP and DOWN arrows ('q' to quit).", False, pygame.Color("#ffffff00"))
	screen.blit(hint_surface, (10, 10))

	game_loop = GameLoopState()

	ctrl_mgr = ControllersManager()

	keys_pressed = ctrl_mgr.add(ControllerKeysPressed)

	key_quit = ctrl_mgr.add(ControllerKeyValue, (pygame.K_q,))
	key_quit_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_quit))

	key_forward = ctrl_mgr.add(ControllerKeyValue, (pygame.K_UP,))
	key_forward_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_forward))

	key_backward = ctrl_mgr.add(ControllerKeyValue, (pygame.K_DOWN,))
	key_backward_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_backward))

	time_ticks = ctrl_mgr.add(ControllerGeneratorTimeTicks)
	time_delta = ctrl_mgr.add(ControllerGeneratorTimeDelta, (time_ticks,))

	zero_value = ctrl_mgr.add(ControllerStaticValue, (0,))
	accelerate = ctrl_mgr.add(ControllerSwitch, (key_forward_pressed, zero_value, time_delta))

	time_delta_minus = ctrl_mgr.add(ControllerMinus, (time_delta,))
	decelerate = ctrl_mgr.add(ControllerSwitch, (key_backward_pressed, zero_value, time_delta_minus))

	speed_delta = ctrl_mgr.add(ControllerSum, (accelerate, decelerate))

	# print(ctrl_mgr)

	event_type_handlers = {
		pygame.QUIT: lambda e: game_loop.stop(),
		pygame.KEYDOWN: lambda e: keys_pressed.key_pressed(e.key),
		pygame.KEYUP: lambda e: keys_pressed.key_released(e.key),
	}

	gen_init = ctrl_mgr.add(ControllerStaticValue, (0,))
	gen_step = ctrl_mgr.add(ControllerStaticValue, (1,))
	gen_incr = ctrl_mgr.add(ControllerGeneratorIncrement, (gen_step, gen_init))
	gen_decr = ctrl_mgr.add(ControllerGeneratorDecrement, (gen_step, gen_init))

	fil_hi_lim = ctrl_mgr.add(ControllerStaticValue, (10,))
	fil_hi_stop = ctrl_mgr.add(ControllerFilterHighLimit, (gen_incr, fil_hi_lim))

	fil_lo_lim = ctrl_mgr.add(ControllerStaticValue, (-10,))
	fil_lo_stop = ctrl_mgr.add(ControllerFilterLowLimit, (gen_decr, fil_lo_lim), back_write=(gen_decr,))

	fil_band_stop = ctrl_mgr.add(ControllerFilterBandLimit, (gen_incr, fil_lo_lim, fil_hi_lim))

	trig_hi = ctrl_mgr.add(ControllerTriggerHigh, (gen_incr, fil_hi_lim))
	trig_lo = ctrl_mgr.add(ControllerTriggerLow, (gen_incr, fil_hi_lim))

	for loop in range(20):
		ctrl_mgr.update()

		print(f"loop: {loop}, step: {gen_step}, ", end="")
		print(f"incr: {gen_incr}, hi stop: {fil_hi_stop}, ", end="")
		print(f"decr: {gen_decr}, lo stop: {fil_lo_stop}, ", end="")
		print(f"hi trigg: {trig_hi}, lo trigg: {trig_lo}, ", end="")
		print()

	line_speed_diff = LinesBuffer(screen, screen_rect, "#ffff0000")
	line_acc = LinesBuffer(screen, screen_rect, "#00ff0000")
	line_dec = LinesBuffer(screen, screen_rect, "#ff000000")

	game_loop.start()
	while game_loop.active:
		for event in pygame.event.get():

			print(event)
			print(game_loop)

			if event.type in event_type_handlers.keys():
				event_type_handlers[event.type](event)

			ctrl_mgr.update()

			if key_quit_pressed.value:
				game_loop.stop()

			# print(f"forward: {key_forward_pressed}, backward: {key_backward_pressed}")
			# print(f"time ticks: {time_ticks}, time delta: {time_delta}")
			print(f"speed delta: {speed_delta}")

		speed_x = time_ticks.value * 150
		speed_y_factor = 10000
		line_speed_diff.append_point(speed_x, - speed_delta.value * speed_y_factor)
		line_acc.append_point(speed_x, - accelerate.value * speed_y_factor - screen_rect.centery // 2)
		line_dec.append_point(speed_x, - decelerate.value * speed_y_factor + screen_rect.centery // 2)

		line_speed_diff.draw()
		line_acc.draw()
		line_dec.draw()

		ctrl_mgr.update()
		game_loop.update()

		# debug
		if (speed_x % screen_rect.width) > screen_rect.width - 1:
			line_speed_diff.reset()
			line_acc.reset()
			line_dec.reset()
			screen.fill(screen_color)
			screen.blit(hint_surface, (10, 10))

		pygame.display.update()
		pygame.time.wait(1)


class LinesBuffer(object):
	def __init__(self, surface, surface_rect, color_string):
		self._surface = surface
		self._surface_rect = surface_rect
		self._color = pygame.Color(color_string)
		self._points = []

	def append_point(self, x, y):
		_x = (x + self._surface_rect.left) % self._surface_rect.width
		_y = y + self._surface_rect.centery
		self._points.append((_x, _y))

	def reset(self):
		self._points = []

	def draw(self):
		if len(self._points) > 1:
			pygame.draw.lines(self._surface, self._color, False, self._points, 1)


if __name__ == "__main__":
	main()
