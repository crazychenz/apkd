#!/usr/bin/env python3

from prompt_toolkit import PromptSession
from prompt_toolkit.input.base import Input
from prompt_toolkit.output.base import Output
import io

class StringIOInput(Input):
    """
    Feeds pre-defined lines to the prompt, or could be extended
    to interactively read input manually.
    """
    def __init__(self):
        self._buffer = []

    def raw_mode(self):
        # context manager for raw mode (no-op)
        from contextlib import contextmanager
        @contextmanager
        def noop():
            yield
        return noop()

    def readline(self):
        if self._buffer:
            return self._buffer.pop(0)
        # Fallback to normal input
        return input()

class StringIOOutput(Output):
    """
    Capture all output that the session would write to the terminal.
    """
    def __init__(self):
        self.buf = io.StringIO()

    @property
    def encoding(self):
        return "utf-8"

    def write(self, data):
        self.buf.write(data)

    def write_raw(self, data):
        self.buf.write(data)

    def flush(self):
        self.buf.flush()

    def fileno(self): return 1
    def get_size(self): return (80, 24)

    # Stubs for abstract methods
    def set_title(self, title): pass
    def clear_title(self): pass
    def enter_alternate_screen(self): pass
    def quit_alternate_screen(self): pass
    def hide_cursor(self): pass
    def show_cursor(self): pass
    def enable_mouse_support(self): pass
    def disable_mouse_support(self): pass
    def enable_autowrap(self): pass
    def disable_autowrap(self): pass
    def set_cursor_shape(self, cursor_shape): pass
    def reset_cursor_shape(self): pass
    def set_attributes(self, attrs): pass
    def reset_attributes(self): pass
    def erase_screen(self): pass
    def erase_down(self): pass
    def erase_end_of_line(self): pass
    def cursor_goto(self, x, y): pass
    def cursor_up(self, count=1): pass
    def cursor_down(self, count=1): pass
    def cursor_forward(self, count=1): pass
    def cursor_backward(self, count=1): pass
    def get_default_color_depth(self): return None

# Create the custom output object
capture_output = StringIOOutput()

# PromptSession using custom output
session = PromptSession(output=capture_output)

# Run interactive prompt
text = session.prompt("Say something: ")

# Everything written by the prompt is captured
print("Captured session output:")
print(capture_output.buf.getvalue())
print("Returned input:", text)




