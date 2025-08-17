"""This module is use to handle terminal rendering, such as Markdown in terminal and stream handling."""

from rich import print as rprint
import rich.console
import rich.markdown


class renderingEngine:
    def __init__(self): # need to spawn a console object for rendering markdown
        self.console = rich.console.Console()
        
    def renderMarkdown(self, markdown):
        # wait for full response and render it

        return

    def renderStream(self, stream):
        # directly print every word from model.
        for chunk in stream:
            rprint(chunk, end="")
        return
