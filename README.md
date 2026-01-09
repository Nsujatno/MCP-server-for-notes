# Obsidian Brain Dump MCP

hi, this is just a cool simple mcp server that connects Claude to my Obsidian vault.

basically, it takes a "brain dump" of notes (like the messy ones i take during class when i'm typing fast), automatically reformats them into clean markdown, and saves them directly to my vault.

it was a great intro for me to learn how mcp servers work and honestly i thought it was pretty cool so here we are.

## how to set it up

you can set this up yourself to run with claude desktop. here is the workflow:

1. get the code

first clone the repo:
```
git clone <your-repo-url>
cd <your-repo-folder>
```

2. handle the python stuff (uv)

i used uv for this because it's way faster than pip. if you have uv installed, just run this command to install the dependencies (it creates the virtual env for you):
```
uv sync
```

(if you don't have uv, you can just install mcp and python-dotenv with normal pip, but uv is recommended).

3. connect your vault

create a file named .env in this folder and paste in the path to your obsidian vault (or wherever you want notes to go to):
```
OBSIDIAN_VAULT_PATH="C:\Users\YourName\Documents\ObsidianVault"
```

4. add to claude desktop

make sure you have the claude desktop app installed first. then, just run this command in your terminal:
```
uv run mcp install main.py
```

this will automatically find your claude config file and register the server for you. restart claude desktop and you should your mcp server running in settings -> developer

## how to use it

this is the fun part.
1. open a chat in claude.
2. click the plus button.
3. select add from notes.
4. select organize notes.
5. put in a filename (like lecture-1) and paste your messy brain dump in the other box.

claude will clean it up, make headers/bullets, and save the file to your folder automatically!