# import settings
from django.conf import settings
import os
import openai
from .models import FineTuningJob

# OpenAI API Key
# if settings.OPENAI_API_KEY:
# openai.api_key = settings.OPENAI_API_KEY
# else:
#     raise Exception("OpenAI API Key not found")


def get_completion(prompt):
    lastest_openai_model = FineTuningJob.get_latest_openai_model()
    try:
        from openai import OpenAI

        client = OpenAI()

        completion = client.chat.completions.create(
            model=lastest_openai_model,
            messages=[
                {"role": "system", "content": settings.SYSTEM_CONTENT,},
                {"role": "user", "content": prompt},
            ],
        )
        # print(completion)
        print(f"Used {lastest_openai_model} for front-end application")
        return str(completion.choices[0].message.content)
        # return 'completion.choices[0].message["content"]'
    except Exception as e:
        return str(e)
