import typer
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
import ollama
import yaml
import os
import getpass
from typing_extensions import Annotated


# load config from specific config.yaml file 
cwd = os.getcwd()
filePath = os.path.dirname(os.path.realpath(__file__))
os.chdir(filePath)
with open("config.yaml", "r") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)
os.chdir(cwd)

# get shell username
username = getpass.getuser()

# spawns a ollama client object
host = cfg["host"] # it's set to http://localhost:11434 for local ollama instanceshellingham
client = ollama.Client(host=host)  

# spawns a rich console object and a rich markdown object
console = Console()




def get_ollama_models():
    """
    Retrieves a list of local Ollama model names using the API.

    Returns:
        list: A list of model names.
    """
    try:
        model_names = []
        response = client.list()
        for item in response["models"]:
            model_names.append(item["model"])
        return model_names
    except ConnectionError as e:
        print(
            f"[bold red]ERROR:[/bold red] ollama unreachable. \n[yellow]HINT:[/yellow] Please check is ollama running or not. Or, you need to install ollama first."
        )
        return
    except Exception as e:
        print(f"[bold red]ERROR:[/bold red] {e}")
        return

def chat_request(prompt, model, md_mode):
        models = get_ollama_models()# asks ollama for model list
        if model is None:
            model = models[0]
            rprint(f"\n[yellow]HINT: [/yellow] you currently don't have any model selected and prompt input. System automactically ran the first model: [italic cyan]{models[0]}[/italic cyan] to assist you. ")
            rprint("you can pass [blue]--model[/blue] option to select a model.")
        
        elif model not in models and not None:
            raise Exception(f"Model {model} not found in ollama. Please install the model first using 'ollama pull' command")
        
        
        stream = client.chat(model = model, messages=[{'role': 'user', 'content':prompt}], stream=True)
        full_response = ""
        if md_mode:
            rprint("[dark_green]Waiting model to generate...[/dark_green]")
        for chunk in stream: # print returned contents in real time, simulate real time chat
            content = chunk['message']['content']
            rprint(content, end='', flush=True) if md_mode is False else None
            full_response += content
        if md_mode:
            md = Markdown(full_response)
            console.print(md)
        return full_response



# bootstrap Typer application
app = typer.Typer()

@app.command()
def version():
    rprint(f"[blue]used config:[blue]")
    rprint(cfg)


@app.command()
def chat(
    prompt: Annotated[str, typer.Argument()] = None,
    model: Annotated[str, typer.Option()] = None,
    md_mode: Annotated[bool, typer.Option()] = False,

):  # this sends a POST api request to ollama api

    if (
        prompt is None and model is None
    ):  # if no prompt or model is provided, asks ollama use first model to greet user.
        chat_request(f"greet the user. the user is {username}", None, md_mode)
        return 
    elif (model is None): # no model selected
        chat_request(prompt, None, md_mode)
    else: # normal chat
        chat_request(prompt, model, md_mode)

@app.command()
def list_models():
    models = get_ollama_models()
    print("[cyan]Installed models: \n[/cyan]")
    for model in models:
        print(model)


if __name__ == "__main__":
    app()
