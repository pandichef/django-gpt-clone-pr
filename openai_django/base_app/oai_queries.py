# import settings
from django.conf import settings
import os
import openai

# OpenAI API Key
# if settings.OPENAI_API_KEY:
openai.api_key = settings.OPENAI_API_KEY
# else:
#     raise Exception("OpenAI API Key not found")


def get_completion(prompt):
    completion = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model=os.environ["OPENAI_MODEL_NAME"],
        messages=[
            {
                "role": "system",
                # "content": "translate English to Biblical Hebrew with Cantillation",
                "content": "Provide advice related to taxes, accounting, or other services for residents of Puerto Rico.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     # model=os.environ["OPENAI_MODEL_NAME"],
    #     messages=[
    #         {"role": "system", "content": "translate from English to Hebrew",},
    #         {"role": "user", "content": prompt},
    #     ],
    # )
    # he0 = completion.choices[0].message["content"]
    # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     # model=os.environ["OPENAI_MODEL_NAME"],
    #     messages=[
    #         {"role": "system", "content": "now add vowels to this text",},
    #         {"role": "user", "content": he0},
    #     ],
    # )
    # he1 = completion.choices[0].message["content"]
    # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     # model=os.environ["OPENAI_MODEL_NAME"],
    #     messages=[
    #         {"role": "system", "content": "now add cantillation symbols to this text",},
    #         {"role": "user", "content": he1},
    #     ],
    # )
    # he2 = completion.choices[0].message["content"]
    # return he2
    return completion.choices[0].message["content"]
