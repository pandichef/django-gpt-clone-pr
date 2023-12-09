# import settings
from django.conf import settings
import os
import openai
from .models import FineTuningJob, Example
from .simple_search import sort_string_list
from .finetune import add_date_and_source
import tiktoken

# encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def token_count(string: str) -> int:
    """Returns the number of tokens in a text string."""
    # encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def make_full_prompt(example):
    return (
        f"Question: {example.prompt_text}\nAnswer: {add_date_and_source(example)}\n##\n"
    )


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
    # prompt_index = 1
    for example in examples:
        examples_list.append(make_full_prompt(example))
    sorted = sort_string_list(prompt, examples_list)[:return_size]
    print("Prior prompts found: ", len(sorted))
    # print(sorted)
    database_prompts = ""
    database_prompts_summarized = ""
    for x in sorted:
        # print(prompt_index)
        database_prompts += x
        database_prompts_summarized += " ".join(x.split()[:20]) + "..."
        # prompt_index += 1
    # return sorted[:return_size]
    # print(len(database_prompts))
    return database_prompts, database_prompts_summarized  # , prompt_index


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

        (database_prompts, database_prompts_summarized,) = collate_prior_prompts(prompt)
        prompt_plus = (
            "Provide the best possible answer to the following questions.\n\n"
            + database_prompts
            + f"Question: {prompt}\nAnswer: "
        )
        prompt_plus_summarized = (
            "Provide the best possible answer to the following questions.\n\n"
            + database_prompts_summarized
            + f"Question: {prompt}\nAnswer: "
        )
        # print(prompt_plus)
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
        # print(
        #     "prompt_plus:\n",
        #     database_prompts_summarized + f"Question: {prompt}\nAnswer: ",
        # )
        print("prompt_plus:\n", prompt_plus_summarized)
        print("Prompt token count: ", token_count(prompt_plus))
        print(f"Used {lastest_openai_model} for front-end application")
        return str(completion.choices[0].message.content)
    except Exception as e:
        return str(e)
