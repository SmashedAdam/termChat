# Termchat

A lightweight CLI ollama frontend.

## INFO: branch `main` is under maintainence. Changes will be make to `dev` branch. Once finished `dev` will be merged to `main`

## Installation

Run the following command to install termchat (download the wheel file from releases page):

```bash
pip install <termchat-x.x.x-py3-none-any.whl>
```

## Usage

To start using, type:

```bash
termchat chat
```

This will let ollama use its first model on the list to greet you.

To send a message with desired model, type:

```bash
termchat chat --model <model name> <message>
```

To check what models had instelled, type:

```bash
termchat list-models
```

To use interactive mode, type:  
`--flash` flag will disable markdown render for faster response.

```bash
termchat ichat [--flash]
```

## Configuration

Termchat by default uses the default ollama endpoint, which is <http://localhost:11434>
To override this, pass `--ollama-host <custom api endpoint>` to the command line.

Models will be auto-detected by calling ollama's api.

## Features

* Supports multiple models and prompts
* Real-time chat with ollama
* Customizable endpoint
* Lightweight and easy to use
* Supports markdown mode, which formats LLM's response inside console
* Supports interactive mode, which preserve chat context during the **same session**

## Requirements

Termchat requires Python 3.10 or later, as well as the following packages:

* `ollama` (>=0.5.1,<0.6.0)
* `pyyaml` (>=6.0.2,<7.0.0)
* `typer` (>=0.16.0,<0.17.0)
* `shellingham` (>=1.5.4,<2.0.0)

## TODO

* Add support for preserving context window
* Add support for real-time markdown rendering
* Add support for customizing the temperature

## License

Termchat is distributed under the MIT license.
