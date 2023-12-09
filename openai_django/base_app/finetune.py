import io
import json
import os
import django
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models import Q


from base_app.models import Example

# Retrieve the data using a QuerySet
# qs = Example.objects.filter(is_approved=True)  # , was_processed=False)
# qs = Example.objects.all()
qs = Example.objects.filter(Q(is_approved=True) & Q(fine_tuning_job__isnull=True))


def add_context_info(obj):
    if obj.source_type:
        return f'On {obj.created_at.date().strftime("%B %d, %Y")}, according to a {obj.source_type}, {obj.completion_text}'
    else:
        return (
            f'On {obj.created_at.date().strftime("%B %d, %Y")}, {obj.completion_text}'
        )


def convert_to_openai_format(examples: QuerySet) -> list:
    openai_list = []

    for obj in examples:
        this_dict = {
            "messages": [
                {"role": "system", "content": settings.SYSTEM_CONTENT},
                {"role": "user", "content": obj.prompt_text,},
                {"role": "assistant", "content": add_context_info(obj),},
            ]
        }
        openai_list.append(this_dict)
    return openai_list  # i.e., records


# print(qs)


def write_records_to_bytesio(records: list) -> io.BytesIO:
    string_io = io.StringIO()
    for record in records:
        string_io.write(json.dumps(record))
        string_io.write("\n")
    string_io.seek(0)
    string_data = string_io.getvalue()
    # Convert the string data to bytes
    bytes_data = string_data.encode("utf-8")
    # Create a BytesIO object from the bytes data
    bytes_io = io.BytesIO(bytes_data)
    # return output
    return bytes_io


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openai_django.settings")
    django.setup()
    openai_records = convert_to_openai_format(qs)
    # print(openai_records)

    bytesio_object = write_records_to_bytesio(openai_records)

    # {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
    # {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
    # {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}

    from openai import OpenAI

    client = OpenAI()

    # https://platform.openai.com/files
    # https://platform.openai.com/finetune

    openai_file_object = client.files.create(file=bytesio_object, purpose="fine-tune")
    openai_ftjob_object = client.fine_tuning.jobs.create(
        training_file=openai_file_object.id, model="gpt-3.5-turbo",
    )
