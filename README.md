# gpt-console
Unlock the Power of GPT: Experience Command-Line Magic with Interactive GPT Console!

GPT console is a command-line utility that provides an interactive interface to interact with OpenAI's GPT-powered language model. 

This repository contains a single Python file gpt.py, which will be installed into ~/bin/g and have its PATH added to .bashrc or other configuration files.

Installation

Follow the instructions below to install gpt-console:

1. Download the script
Download the gpt.py script from the GitHub repository:

```
mkdir -p ~/bin
curl -L -o ~/bin/g https://raw.githubusercontent.com/mag-/gpt-console/main/gpt.py
chmod +x ~/bin/g
echo 'export PATH="$HOME/bin:$PATH"'
export OPENAI_API_KEY='...'
```

# Usage

```
g "what is the sum of numbers 1 to 10""
```

You can also append a file to the prompt:

```
seq 1 10 > test
g "add numbers" test
```

