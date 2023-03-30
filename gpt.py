#!/usr/bin/env python
import os
import json
import random
import requests
import click
import sseclient
import sys
from rich.console import Console
from rich.markdown import Markdown

console = Console()
from pathlib import Path

GPT_PROMPT = """You are a personal assistant, you help the user with their daily tasks.
You help with code problems by providing concise answers with only lines of code that have to changed. Prefer use of python, polars, PyTorch.
To general non coding questions you reply with table."""

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

headers = {
    "Accept": "text/event-stream",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}


def query_gpt(prompt, fast=False):
    data = {
        "model": "gpt-3.5-turbo" if fast else "gpt-4",
        "messages": [{"role": "user", "content": " ".join([GPT_PROMPT, prompt])}],
        "temperature": 0.7,
        "stream": True,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", stream=True, headers=headers, json=data)
    response.raise_for_status()
    client = sseclient.SSEClient(response)
    buffer = ""
    for event in client.events():
        if event.data != "[DONE]":
            j = json.loads(event.data)
            if "content" in j["choices"][0]["delta"]:
                content = j["choices"][0]["delta"]["content"]
                buffer = buffer + content
                print(j["choices"][0]["delta"]["content"], end="", flush=True)
            if "\n" in buffer:
                # add markdown rendering here at some point
                buffer = ""


def data_gpt(prompt, data_path):
    with open(data_path, "r") as data_file:
        file_content = data_file.read()
    prompt_input = json.dumps(prompt + " " + file_content)
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt_input}],
        "temperature": 0.7,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    gpt_response = response.json()
    click.echo(gpt_response["choices"][0]["message"]["content"])


def img_gpt(prompt):
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
    create_img = response.json()
    url = create_img["data"][0]["url"]
    rand_num = random.randint(1, 1000000)
    img_response = requests.get(url)
    with open(f"img-{rand_num}.png", "wb") as img_file:
        img_file.write(img_response.content)
    click.echo(f"Image {url} saved as img-{rand_num}.png")


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument("prompt", required=False)
@click.argument("fname", required=False)
def cli(ctx, prompt, fname):
    if prompt and fname:
        ctx.invoke(query_file, prompt=prompt, data_path=fname)
        return
    if prompt:
        ctx.invoke(query_gpt, prompt=prompt)
        return
    elif ctx.invoked_subcommand is None:
        click.echo("No command is given, executing the 'query' command by default.")
        ctx.invoke(query_gpt, prompt=click.prompt("Enter the prompt"))


@cli.command()
@click.argument("prompt")
def image(prompt):
    img_gpt(prompt)
    click.echo("Image created.")


@cli.command()
@click.argument("prompt")
@click.argument("data_path", type=click.Path(exists=True, dir_okay=False, readable=True))
def query_file(prompt, data_path):
    response = data_gpt(prompt, data_path)
    click.echo(response)


if __name__ == "__main__":
    cli()
