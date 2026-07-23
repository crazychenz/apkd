from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
import io

class BufferOutput:
    """Custom output object that writes to a StringIO buffer."""
    def __init__(self):
        self.buffer = io.StringIO()

    def write(self, data):
        self.buffer.write(data)

    def flush(self):
        pass

    def get_value(self):
        return self.buffer.getvalue()


class SimpleREPL:
    def __init__(self):
        self.pipe_input = create_pipe_input()
        self.buffer_output = BufferOutput()
        self.session = PromptSession(
            input=pipe_input,
            output=buffer_output,
            history=InMemoryHistory()
        )
        self.running = True

        # Register commands
        self.commands = {
            "help": self.cmd_help,
            "echo": self.cmd_echo,
            "quit": self.cmd_quit,
            "exit": self.cmd_quit,
        }

    def run(self):
        print("Welcome to SimpleREPL. Type 'help' for available commands.")
        while self.running:
            try:
                text = self.session.prompt("> ")
                self.handle_command(text)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting REPL.")
                break

    def handle_command(self, text: str):
        if not text.strip():
            return
        parts = text.strip().split()
        cmd, args = parts[0], parts[1:]

        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def cmd_help(self, args):
        print("Available commands:")
        for name in self.commands:
            print(f"  {name}")

    def cmd_echo(self, args):
        print(" ".join(args))

    def cmd_quit(self, args):
        print("Goodbye!")
        self.running = False


if __name__ == "__main__":
    repl = SimpleREPL()
    repl.run()