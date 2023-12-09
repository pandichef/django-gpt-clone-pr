# import io
# import json
# import os
# import django
# from django.conf import settings
# from django.db.models.query import QuerySet
# from django.db.models import Q
from .models import Example
from .oai_queries import make_full_prompt


def export_examples():
    knowledge = ""
    for example in Example.objects.all():
        knowledge += make_full_prompt(example)
    with open("examples.txt", "w") as f:
        f.write(knowledge)
