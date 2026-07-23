import asyncio
from thirdparty.python.repl import start_socket_client

if __name__ == "__main__":
    try:
        asyncio.run(start_socket_client(socket_path="/tmp/asyncrepl.sock"))
    except KeyboardInterrupt:
        print("\nTCP Client exiting")