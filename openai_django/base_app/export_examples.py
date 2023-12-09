from .models import Example
from .oai_queries import make_full_prompt


def export_examples():
    # this is used only in django shell
    knowledge = ""
    for example in Example.objects.all():
        knowledge += make_full_prompt(example)
    with open("examples.txt", "w") as f:
        f.write(knowledge)
