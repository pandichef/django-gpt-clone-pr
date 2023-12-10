# A Django application that collects custom user data to fine tune OpenAI LLMs

This project uses the new [gpt-3.5-turbo](https://platform.openai.com/docs/guides/chat/chat-completions-beta) model API from [OpenAI](https://openai.com/) and a [Django](https://www.djangoproject.com/) webserver, consuming your own OpenAI credits by using your API Key.

## Features

1. Includes a ChatGPT front-end clone to run fine-tuned model
2. Employs the Django Admin to collect custom user data
3. Manages the completely flow to continously fine tune a base OpenAI LLM
4. Implements [RAG](https://research.ibm.com/blog/retrieval-augmented-generation-RAG) by searching through the custom user data to prompt the LLM

## Usage

1. Make sure you have a working account on [OpenAI](https://openai.com/) and have created an API key. Save it.
2. Add the API key to the `OPENAI_API_KEY` environment variable.
3. Install the requirements with `pip install -r requirements.txt` or alternatively create a virtual environment and install the requirements there. Make sure the environment variable is present in the virtual environment.
4. Run the server with `python manage.py runserver`.
5. Go to `http://localhost:8000/` to interact with the bot.
