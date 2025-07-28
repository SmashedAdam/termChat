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


def chat_without_history(prompt, model, flash, host):
    """sends a single chat request. no chat history

    Args:
        prompt (str): chat prompt send to ollama
        model (str): model name
        md_mode (bool): use Markdown mode or not
        host (str): ollama api endpoint

    Raises:
        Exception: Model is not found on ollama

    Returns:
        str: full response from ollama
    """

    models = get_ollama_models(host)  # asks ollama for model list
    client = ollama.Client(host=host)

    if model is None:
        model = models[0]
        rprint(
            f"\n[yellow]HINT: [/yellow] you currently don't have any model selected and prompt input. System automatically ran the first model: [italic cyan]{models[0]}[/italic cyan] to assist you. "
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
    if flash is False:
        rprint("[green]Waiting model to generate...[/green]")
    for (
        chunk
    ) in stream:  # print returned contents in real time, simulate real time chat
        content = chunk["message"]["content"]
        rprint(content, end="", flush=True) if flash is True else None
        full_response += content
    if flash is False:
        md = Markdown(full_response)
        console.print(md)
    return full_response


def chat_with_history(chat_hist, msg, host, model, md_mode):
    client = ollama.Client(host=host)
    chat_hist.append(msg)
    response = client.chat(model=model, messages=chat_hist, stream=True)
    chunks = []
    full_msg = ""
    for chunk in response:
        print(chunk["message"]["content"], end="", flush=True) if md_mode is False else None
        chunks.append(chunk)
        full_msg += chunk["message"]["content"]
    chat_hist.append({"role": "assistant", "content": full_msg})
    return chat_hist, full_msg


# bootstrap Typer application
app = typer.Typer(no_args_is_help=True)


@app.command()
def version():
    """Show version info."""
    try:
        print(importlib.metadata.version("termchat"))
    except importlib.metadata.PackageNotFoundError:
        print("Version not found (package not installed)")


@app.command()  # TODO: merge to use chat_without_history in future
def chat(
    prompt: Annotated[str, typer.Argument(help="Prompt to send to ollama.")] = None,
    model: Annotated[str, typer.Option(help="Model to use for chat.")] = None,
    flash: Annotated[bool, typer.Option(help="Use markdown mode or not.")] = False,
    host: Annotated[
        str, typer.Option(help="use customized ollama endpoint")
    ] = "http://localhost:11434",
):  # this sends a chat request via ollama api using ollama package
    """Send a single chat request to ollama."""
    if (
        prompt is None and model is None
    ):  # if no prompt or model is provided, asks ollama use first model to greet user.
        chat_without_history(
            f"greet the user. the user is {username}", None, flash, host
        )
        return
    elif model is None:  # no model selected
        chat_without_history(prompt, None, flash, host)
    else:  # normal chat
        chat_without_history(prompt, model, flash, host)


@app.command()
def list_models(
    host: Annotated[
        str, typer.Option(help="use customized ollama endpoint")
    ] = "http://localhost:11434",
):
    """Query ollama for available models."""
    models = get_ollama_models(host)
    rprint("[cyan]Installed models: \n[/cyan]")
    for model in models:
        print(model)


@app.command()
def ichat(
    host: Annotated[
        str, typer.Option(help="use customized ollama endpoint")
    ] = "http://localhost:11434",
    flash: Annotated[
        bool, typer.Option(help="enable instant reply. This disable Markdown support.")
    ] = False,
):
    """Do interactive chat with ollama."""
    # ask user to select an existing model
    rprint("Please select a model to start chatting")
    models = get_ollama_models(host)
    rprint("[cyan]Installed models: \n[/cyan]")
    for model in models:  # verify is model present or not
        print(model)
    model = input(": ")
    if model not in models:
        rprint(
            "[yellow]WARN: [/yellow] selected model is not installed. Please install the model first."
        )
        return  # quit if model is not exist on ollama

    # initialize ollama client
    rprint(f"Initializing chat with model: [cyan]{model}[/cyan]")
    rprint("Type [green]/quit[/green] to exit")

    # greet user
    chat_without_history(f"greet the user. the user is {username}", model, False, host)
    print()

    # main chat loop - flash mode
    if flash:  # when flash mode is enabled, respond instantly.
        rprint(
            "[cyan]INFO: [/cyan] Model is instructed to use plain text, but it may still returns markdown, especially when responding complex questions." # todo: let the model know to use plain text.
        )
        msg_hist = [
            {
                "role": "system",
                "content": f"Your responses should ALWAYS be in plain text. AVOID any markdown formatting like bolding, italics, bullet points, or code blocks AT ALL COST. Instead, you can use arrows, such as '->' to inform the user that is a point. The user is {username}. If the user asks how to quit, tell them to type '/quit' to exit.",
            }
        ]
        while True:
            # user prompt
            userPrompt = input("Prompt>>> ")
            if userPrompt == "/quit":
                break
            msg = {"role": "user", "content": userPrompt}
            # TODO: check num_ctx, handle context window
            # send chat request, including history
            msg_hist, full_response = chat_with_history(
                msg_hist, msg, host, model, False
            )
            print()
        return
    else:  # mode that support markdown
        msg_hist = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. The user is {username}Your jos is to answer the user about their questions. RESPOND in MARKDOWN format if needed, such as using point form, headings, bold, italics and code blocks. If the user asks how to quit, tell them to type '/quit' to exit.",
            }
        ]
        while True:
            # user prompt
            userPrompt = input("Prompt>>> ")
            if userPrompt == "/quit":
                break
            msg = {"role": "user", "content": userPrompt}
            # TODO: check num_ctx, handle context window
            # send chat request, including history
            rprint("[green]Waiting model to respond...[/green]")
            msg_hist, full_response = chat_with_history(
                msg_hist, msg, host, model, True
            )
            
            md = Markdown(full_response)
            console.print(md)
            print()

        return


if __name__ == "__main__":
    app()
