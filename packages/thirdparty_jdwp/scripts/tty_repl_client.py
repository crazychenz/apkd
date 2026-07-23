#!/usr/bin/env python3

import asyncio
from thirdparty.python.repl import start_raw_tty_repl_client

if __name__ == "__main__":
    try:
        asyncio.run(start_raw_tty_repl_client(socket_path="/tmp/asyncrepl.sock"))
    except KeyboardInterrupt:
        print("\nTTY Client exiting")