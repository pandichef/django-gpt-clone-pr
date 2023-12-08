# import settings
from django.conf import settings
import os
import openai
from .models import FineTuningJob, Example
from .simple_search import sort_string_list


# OpenAI API Key
# if settings.OPENAI_API_KEY:
# openai.api_key = settings.OPENAI_API_KEY
# else:
#     raise Exception("OpenAI API Key not found")


def collate_prior_prompts(prompt, return_size=5):
    # todo: limit examples by rank
    examples = Example.objects.all()
    examples_list = []
    # database_prompts = ""
    for example in examples:
        examples_list.append(
            f"Prompt:\n{example.prompt_text}\n\nCompletion:\n{example.completion_text}\n\n"
        )
        # database_prompts += f"Prompt:\n{example.prompt_text}\n\nCompletion:\n{example.completion_text}\n\n"
    # print(examples)
    database_prompts = ""
    sorted = sort_string_list(prompt, examples_list)[:return_size]
    # print(sorted)
    for x in sorted:
        database_prompts += x
    # return sorted[:return_size]
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
        print(f"Estimated token count: {len(prompt_plus.split())}")
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
        return prompt_plus + str(completion.choices[0].message.content)
        # return 'completion.choices[0].message["content"]'
    except Exception as e:
        return str(e)
