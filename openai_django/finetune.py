import os
import django
from django.conf import settings
from django.db.models.query import QuerySet

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openai_django.settings")
django.setup()

from base_app.models import Example

# Retrieve the data using a QuerySet
qs = Example.objects.filter(is_approved=True, was_processed=False)
# qs = Example.objects.all()


def convert_to_openai_format(qs: QuerySet) -> list:
    openai_list = []

    for obj in qs:
        this_dict = {
            "messages": [
                {"role": "system", "content": settings.SYSTEM_CONTENT},
                {"role": "user", "content": obj.prompt_text},
                {"role": "assistant", "content": obj.completion_text,},
            ]
        }
        openai_list.append(this_dict)
    return openai_list


openai_list = convert_to_openai_format(qs)
print(openai_list)

# print(qs)


# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}
