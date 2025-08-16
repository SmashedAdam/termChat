import typer
import importlib
from modules.ollama_client import ollama_client
from modules.render_utils import renderingEngine


# bootstrap Typer application
app = typer.Typer(no_args_is_help=True)


@app.command()
def version():
    """Show version info."""
    try:
        print(importlib.metadata.version("termchat"))
    except importlib.metadata.PackageNotFoundError:
        print("Version not found (package not installed)")

@app.command()
def test():
    """Test function."""
    ola = ollama_client(host="http://100.64.60.10:11434")
    renderer = renderingEngine()
    print(ola.models)
    model = input("model:")
    stream = ola.generate(model, "Hello i am adam. who are you?")
    renderer.renderStream(stream)


if __name__ == "__main__":
    app()