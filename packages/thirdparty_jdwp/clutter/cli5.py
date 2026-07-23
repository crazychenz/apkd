from __future__ import annotations

import string
import code
import sys
import io
from typing import Callable

from textual.app import App
from textual.scroll_view import ScrollView
from textual.widgets import Header
from textual.message_pump import MessagePump
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget
from textual.keys import Keys
from textual.message import Message

import rich.repr

from rich.markdown import Markdown
from rich.console import RenderableType
from rich.text import Text
from rich import box
from rich.panel import Panel
from rich.syntax import Syntax


class AsyncConsole(code.InteractiveConsole):
    def __init__(self, handler, locals: dict = None, filename="<console>"):
        super().__init__(locals, filename)
        self.handler = handler
        self.filename = filename
        self.output = io.StringIO()
        self.prompt1 = ">>> "
        self.prompt2 = "... "
        self.prompt = self.prompt1
        self.is_async = False

    async def runcode(self, code):
        orighook, sys.displayhook = sys.displayhook, self.displayhook
        try:
            origout, sys.stdout = sys.stdout, self.output
            try:
                exec(code, self.locals)
                if self.is_async:
                    coro = self.locals["_"]
                    obj = await coro
                    self.locals["_"] = obj
                    if obj is not None:
                        self.write(repr(obj))
            except SystemExit:
                raise
            except Exception:
                self.showtraceback()
            finally:
                sys.stdout = origout
        finally:
            sys.displayhook = orighook

    def displayhook(self, obj):
        self.locals["_"] = obj
        if obj is not None and not self.is_async:
            self.write(repr(obj))

    def write(self, data):
        self.output.write(data)

    async def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        await self.runcode(code)
        return False

    async def push(self, line):
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = await self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more

    async def interact(self, line):
        self.is_async = line.startswith("await ")
        self.output = io.StringIO()
        self.output.write(f"{self.prompt}{line}\n")
        if self.is_async:
            line = line[6:]
        r = await self.push(line)
        self.prompt = self.prompt2 if r else self.prompt1
        if not r and "_" in self.locals and self.locals["_"]:
            self.output.write("\n")
        self.handler(self.output.getvalue())
        return self.prompt


class TextPrompt:
    def __init__(
        self,
        prompt: str = "? ",
        prompt_style: str = "default",
        bell: Callable[[], None] = None,
    ):
        self.prompt = prompt
        self.prompt_style = prompt_style
        self.bell = bell if bell else lambda x: None
        self.buffer = ""
        self.cursor = 0
        self.saved_buffer = ""
        self.history = []
        self.history_cur = 0

    def update_prompt(self, prompt):
        self.prompt = prompt

    def render(self) -> RenderableType:
        text = Text()
        text.append(self.prompt, style=self.prompt_style)
        text.append(self.buffer)
        text.append(" ")
        offset = self.cursor + len(self.prompt)
        text.stylize("reverse", offset, offset + 1)
        return text

    def on_key(self, event):
        if event.key == Keys.Return or event.key == Keys.Enter:
            event.stop()
            self.history.append(self.buffer)
            self.buffer = ""
            self.cursor = 0
            self.history_cur = 0
            return self.history[-1]
        elif event.key == Keys.Home:
            event.stop()
            self.cursor = 0
            return
        elif event.key == Keys.End:
            event.stop()
            self.cursor = len(self.buffer)
            return
        elif event.key == Keys.Backspace or event.key == "ctrl+h":
            event.stop()
            if self.cursor == 0:
                self.bell()
            else:
                new_buff = self.buffer[: self.cursor - 1] + self.buffer[self.cursor :]
                self.buffer = new_buff
                self.cursor -= 1
            return
        elif event.key == Keys.Up or event.key == Keys.Down:
            event.stop()
            delta = -1 if event.key == Keys.Up else 1
            new_loc = self.history_cur + delta
            if new_loc < -len(self.history) or new_loc > 0:
                self.bell()
            else:
                if self.history_cur == 0:
                    self.buffer = self.saved_buffer
                self.history_cur = new_loc
                if self.history_cur == 0:
                    self.saved_buffer = self.buffer
                else:
                    self.buffer = self.history[self.history_cur]
                self.cursor = len(self.buffer)
            return
        elif event.key == Keys.Left or event.key == Keys.Right:
            event.stop()
            delta = -1 if event.key == Keys.Left else +1
            new_loc = self.cursor + delta
            if new_loc < 0 or new_loc > len(self.buffer):
                self.bell()
            else:
                self.cursor = new_loc
            return
        elif event.key in string.printable:
            event.stop()
            new_buff = (
                self.buffer[: self.cursor] + event.key + self.buffer[self.cursor :]
            )
            self.buffer = new_buff
            self.cursor += 1
            self.history_cur = 0
            return


@rich.repr.auto
class TextInputCommand(Message, bubble=True):
    def __init__(self, sender: MessagePump, line: str) -> None:
        super().__init__(sender)
        self.line = line


@rich.repr.auto
class UpdatePrompt(Message, bubble=True):
    def __init__(self, sender: MessagePump, prompt: str) -> None:
        super().__init__(sender)
        self.prompt = prompt


@rich.repr.auto
class TextInput(Widget):
    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")
    output: Reactive[str] = Reactive("")

    def __init__(
        self,
        prompt=">>>",
        tall_height=20,
        style="gold1 on grey11",
        syntax_theme: str = "ansi_dark",
        lexer_name: str = "pycon",
    ) -> None:
        super().__init__()
        self.layout_size = 3
        self.layout_sizes = (3, 20, 40, 60, 40, 20)
        self.layout_size_idx = 0
        self.style = style
        self.prompt = TextPrompt(prompt, "dark_orange", "^")
        self.syntax = Syntax("", lexer_name, theme=syntax_theme, word_wrap=True)

    def render(self) -> RenderableType:
        if self.layout_size > 3 and self.output:
            lines = self.output.split("\n")[-self.layout_size + 4 :]
            t_output = "\n".join(lines)
            text = self.syntax.highlight(t_output) + self.prompt.render()
        else:
            text = self.prompt.render()
        return Panel(
            text,
            title="Console",
            border_style="dark_orange" if self.mouse_over else "grey30",
            box=box.SQUARE if self.has_focus else box.ROUNDED,
            style=self.style,
            height=self.layout_size,
        )

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

    async def on_key(self, event):
        if event.key == Keys.Escape:
            self.visible = False
            self.has_focus = False
        elif event.key == Keys.ShiftDown:
            self.animate("layout_offset_y", 0)
        elif event.key == Keys.ShiftUp:
            y = self.console.size.height - self.size.height
            self.animate("layout_offset_y", -y)
        else:
            value = self.prompt.on_key(event)
            if value is not None:
                await self.emit(TextInputCommand(self, value))
        self.refresh()

    async def on_click(self, event: events.Click) -> None:
        self.layout_size_idx = (self.layout_size_idx + 1) % len(self.layout_sizes)
        self.layout_size = self.layout_sizes[self.layout_size_idx]

    def handle_output(self, new_output):
        self.output = self.output + new_output
        self.refresh()

    def update_prompt(self, prompt) -> None:
        self.log(f"handling UpdatePrompt: {prompt}")
        self.prompt.update_prompt(prompt)


class CmdRunner(App):
    """App that runs a command"""

    async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering app mode)"""
        #await self.bind("q", "quit", "Quit")
        pass

    def compose(self):
        self.header = Header()
        # A scrollview to contain the markdown file
        self.body = ScrollView()#gutter=1)

        self.manhole_panel = TextInput(">>> ")
        self.manhole_panel.visible = False

        # Header / footer / dock
        yield self.header
        yield self.manhole_panel
        yield self.body

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""

        
        #await self.view.dock(self.header, edge="top")
        #await self.view.dock(self.manhole_panel, z=1, edge="bottom")

        # Dock the body in the remaining space
        #await self.view.dock(self.body, edge="left")

        # async def get_markdown(filename: str) -> None:
        #     with open(filename, "rt") as fh:
        #         readme = Markdown(fh.read(), hyperlinks=True)
        #     await self.body.update(readme)

        #await self.call_later(get_markdown, "richreadme.md")

        # self.manhole = AsyncConsole(
        #     self.manhole_panel.handle_output,
        #     {"app": self, "get_markdown": get_markdown},
        # )
        pass

    async def on_key(self, event):
        if event.key == "~":
            self.manhole_panel.visible = not self.manhole_panel.visible
            event.stop()
            return

    async def handle_text_input_command(self, message: TextInputCommand) -> None:
        assert isinstance(message.sender, TextInput)
        if message.line == "quit":
            await self.action_quit()
        prompt = await self.manhole.interact(message.line)
        message.stop()
        self.log(f"after interact: UpdatePrompt: {prompt}")
        self.manhole_panel.update_prompt(prompt)


CmdRunner().run()#title="Command Runner", log="textual.log")
