# requires python 3.7.1  or higher

import asyncio


async def test_task(loops, delay, message, exception_message=None):
	if exception_message is not None:
		raise RuntimeError(exception_message)

	for _ in range(loops):
		print(message, end='')
		await asyncio.sleep(delay=delay)

	return loops


async def test1():
	task1 = asyncio.create_task(test_task(10, 1, "A"))
	task2 = asyncio.create_task(test_task(15, 0.75, "B", "Stop! Hammer time."))
	task3 = asyncio.create_task(test_task(18, 0.6, "C"))

	await task1
	await task2
	await task3


async def test2():
	result = await asyncio.gather(
		test_task(10, 1, "A"),
		test_task(15, 0.75, "B", "Stop! Hammer time."),
		test_task(18, 0.6, "C"),
	)

	print()
	print(repr(result))


async def main():
	await test2()


if __name__ == "__main__":
	asyncio.run(main())
