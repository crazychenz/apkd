import asyncio
import sys
import termios
import tty

async def read_input(prompt=""):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    line = []
    
    try:
        tty.setraw(fd)  # Put terminal in raw mode
        while True:
            ch = sys.stdin.read(1)  # read one character at a time
            if ch == '\x1b':
                sys.exit(0)
            if ch in ("\r", "\n"):  # Enter pressed
                break
            line.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    sys.stdout.write("\n")
    sys.stdout.flush()
    return ''.join(line)

async def main():
    while True:
        single_line = await read_input()
        print(f"Processed: {single_line!r}")

if __name__ == "__main__":
    asyncio.run(main())
