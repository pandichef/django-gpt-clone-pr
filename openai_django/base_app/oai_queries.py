# import settings
from django.conf import settings
import os
import openai
from .models import FineTuningJob, Example
from .simple_search import sort_string_list
from .finetune import add_date_and_source


def make_full_prompt(example):
    return f"Prompt:\n{add_date_and_source(example)}\n\nCompletion:\n{example.completion_text}\n\n"


# OpenAI API Key
# if settings.OPENAI_API_KEY:
# openai.api_key = settings.OPENAI_API_KEY
# else:
#     raise Exception("OpenAI API Key not found")


def collate_prior_prompts(prompt, return_size=3):
    # todo: limit examples by rank
    examples = Example.objects.all()
    examples_list = []
    # database_prompts = ""
    for example in examples:
        examples_list.append(make_full_prompt(example))
    sorted = sort_string_list(prompt, examples_list)[:return_size]
    print(len(sorted))
    # print(sorted)
    database_prompts = ""
    for x in sorted:
        database_prompts += x
    # return sorted[:return_size]
    # print(len(database_prompts))
    return database_prompts


# def collate_prior_prompts():
#     # todo: limit examples by rank
#     examples = Example.objects.all()
#     database_prompts = ""
#     for example in examples:
#         database_prompts += f"Prompt:\n{example.prompt_text}\n\nCompletion:\n{example.completion_text}\n\n"
#     return database_prompts


def get_completion(prompt):
    lastest_openai_model = FineTuningJob.get_latest_openai_model()
    try:
        from openai import OpenAI

        client = OpenAI()

        prompt_plus = (
            collate_prior_prompts(prompt) + f"Prompt:\n{prompt}\n\nCompletion:\n"
        )
        print(prompt_plus)
        # print(f"Estimated token count: {len(prompt_plus.split())}")
        # print(prompt_plus)
        # prompt_plus = prompt

        completion = client.chat.completions.create(
            model=lastest_openai_model,
            messages=[
                {"role": "system", "content": settings.SYSTEM_CONTENT,},
                {"role": "user", "content": prompt_plus},
            ],
        )
        # print(completion)
        print(f"Used {lastest_openai_model} for front-end application")
        # return prompt_plus + str(
        #     completion.choices[0].message.content
        # )  # to see full prompt text
        return str(completion.choices[0].message.content)
    except Exception as e:
        return str(e)
