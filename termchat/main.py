import importlib.metadata
import typer
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
import ollama
import yaml
import os
import getpass
from typing_extensions import Annotated
import importlib


# get shell username
username = getpass.getuser()

host = "localhost:11434"  # it's set to http://localhost:11434 for local ollama instance

# spawns a rich console object and a rich markdown object
console = Console()


def get_ollama_models(host):
    """
    Retrieves a list of local Ollama model names using the API.

    Returns:
        list: A list of model names.
    """

    client = ollama.Client(host=host)
    try:
        model_names = []
        response = client.list()
        for item in response["models"]:
            model_names.append(item["model"])
        return model_names
    except ConnectionError as e:
        rprint(
            f"[bold red]ERROR:[/bold red] ollama unreachable. \n[yellow]HINT:[/yellow] Please check is ollama running or not. Or, you need to install ollama first."
        )
        return
    except Exception as e:
        rprint(f"[bold red]ERROR:[/bold red] {e}")
        return


def chat_request(prompt, model, md_mode, host):
    models = get_ollama_models(host)  # asks ollama for model list
    client = ollama.Client(host=host)

    if model is None:
        model = models[0]
        rprint(
            f"\n[yellow]HINT: [/yellow] you currently don't have any model selected and prompt input. System automactically ran the first model: [italic cyan]{models[0]}[/italic cyan] to assist you. "
        )
        rprint("you can pass [blue]--model[/blue] option to select a model.")

    elif model not in models and not None:
        raise Exception(
            f"Model {model} not found in ollama. Please install the model first using 'ollama pull' command"
        )

    stream = client.chat(
        model=model, messages=[{"role": "user", "content": prompt}], stream=True
    )
    full_response = ""
    if md_mode:
        rprint("[dark_green]Waiting model to generate...[/dark_green]")
    for (
        chunk
    ) in stream:  # print returned contents in real time, simulate real time chat
        content = chunk["message"]["content"]
        rprint(content, end="", flush=True) if md_mode is False else None
        full_response += content
    if md_mode:
        md = Markdown(full_response)
        console.print(md)
    return full_response


# bootstrap Typer application
app = typer.Typer()


@app.command()
def version():
    try:
        rprint(importlib.metadata.version("termchat"))
    except importlib.metadata.PackageNotFoundError:
        rprint("Version not found (package not installed)")


@app.command()
def chat(
    prompt: Annotated[str, typer.Argument(help="Prompt to send to ollama.")] = None,
    model: Annotated[str, typer.Option(help="Model to use for chat.")] = None,
    md_mode: Annotated[bool, typer.Option(help="Use markdown mode or not.")] = False,
    host: Annotated[
        str, typer.Option(help="use customized ollama endpoint")
    ] = "http://localhost:11434",
):  # this sends a chat request via ollama api using ollama package

    if (
        prompt is None and model is None
    ):  # if no prompt or model is provided, asks ollama use first model to greet user.
        chat_request(f"greet the user. the user is {username}", None, md_mode, host)
        return
    elif model is None:  # no model selected
        chat_request(prompt, None, md_mode, host)
    else:  # normal chat
        chat_request(prompt, model, md_mode, host)


@app.command()
def list_models(host: Annotated[str, typer.Option(help="use customized ollama endpoint")] = "http://localhost:11434"):
    models = get_ollama_models(host)
    rprint("[cyan]Installed models: \n[/cyan]")
    for model in models:
        print(model)


if __name__ == "__main__":
    app()
