from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal

class LineSelectionApp(App):
    def __init__(self):
        super().__init__()
        self.text_content = "\n".join([f"Line {i}: Sample content {i}" for i in range(1, 11)])
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.text_content, id="text-display"),
            Horizontal(
                Button("Select Line 3", id="select-3"),
                Button("Select Line 7", id="select-7"),
                Button("Clear Selection", id="clear"),
            )
        )
    
    def on_mount(self):
        static = self.query_one("#text-display", Static)
        static.can_focus = True
    
    def on_button_pressed(self, event):
        static = self.query_one("#text-display", Static)
        
        if event.button.id == "select-3":
            self.select_line(static, 2)
        elif event.button.id == "select-7":
            self.select_line(static, 6)
        elif event.button.id == "clear":
            self.clear_selection(static)
    
    def select_line(self, static_widget, line_number):
        """Select a specific line by line number (0-indexed)"""
        lines = self.text_content.split('\n')
        
        if 0 <= line_number < len(lines):
            start_pos = sum(len(line) + 1 for line in lines[:line_number])
            end_pos = start_pos + len(lines[line_number])
            
            # Try to set selection (may not be supported in all versions)
            try:
                static_widget.selection = (start_pos, end_pos)
                static_widget.focus()
            except AttributeError:
                self.notify(f"Selected line {line_number + 1}: {lines[line_number]}")
    
    def clear_selection(self, static_widget):
        try:
            static_widget.selection = (0, 0)
        except AttributeError:
            self.notify("Selection cleared")

if __name__ == "__main__":
    LineSelectionApp().run()