from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

class SimpleApp:
    def __init__(self):
        # Create output area
        self.output_area = TextArea(
            text="Welcome to the application!\nType 'help' for available commands.\n",
            multiline=True,
            read_only=True,
            scrollbar=True,
            wrap_lines=True
        )
        
        # Create input area with PromptSession-like behavior
        self.input_area = TextArea(
            height=1,
            multiline=False,
            wrap_lines=False,
            prompt='> ',
            completer=WordCompleter(['help', 'echo'], ignore_case=True),
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        # Create layout
        self.layout = self.create_layout()
        
        # Create key bindings
        self.key_bindings = self.create_key_bindings()
        
        # Create application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            full_screen=True,
            mouse_support=True
        )
    
    def create_layout(self):
        """Create the layout"""
        # Top status bar
        status_bar = TextArea(
            text="Multi-Frame App - Press Ctrl-Q to quit",
            height=1,
            read_only=True
        )
        
        # Create frames
        status_frame = Frame(status_bar, title="Status")
        output_frame = Frame(self.output_area, title="Output")
        input_frame = Frame(self.input_area, title="Input")
        
        # Combine into layout
        container = HSplit([
            status_frame,
            output_frame,
            input_frame
        ])
        
        return Layout(container, focused_element=self.input_area)
    
    def create_key_bindings(self):
        """Create key bindings"""
        kb = KeyBindings()
        
        @kb.add('c-q')
        def quit_app(event):
            """Exit with Ctrl-Q"""
            event.app.exit()
        
        @kb.add('enter')
        def handle_enter(event):
            """Handle Enter key - process command"""
            command = self.input_area.text.strip()
            if command:
                # Add command to output
                self.output_area.text += f"> {command}\n"
                
                # Process command
                self.process_command(command)
                
                # Clear input
                self.input_area.text = ""
        
        return kb
    
    def process_command(self, command):
        """Process a command"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == 'help':
            help_text = """Available commands:
- help: Show this help
- echo <text>: Echo the text
- Ctrl-Q: Exit application
"""
            self.output_area.text += help_text
        
        elif cmd == 'echo':
            if args:
                text = ' '.join(args)
                self.output_area.text += f"Echo: {text}\n"
            else:
                self.output_area.text += "Echo: (no text provided)\n"
        
        else:
            self.output_area.text += f"Unknown command: {cmd}\n"
            self.output_area.text += "Type 'help' for available commands.\n"
    
    def run(self):
        """Run the application"""
        self.app.run()

def main():
    app = SimpleApp()
    app.run()

if __name__ == "__main__":
    main()