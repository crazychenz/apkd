import asyncio
import aioconsole

async def main():
    while True:
        cmd = await aioconsole.ainput(">>> ")
        try:
            result = eval(cmd)
            if asyncio.iscoroutine(result):
                result = await result
            print(repr(result))
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(main())
