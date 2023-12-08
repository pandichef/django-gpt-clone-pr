from django.shortcuts import render
from django.http import JsonResponse
from .models import FineTuningJob
from .oai_queries import get_completion


def query_view(request):
    if request.method == "POST":
        print("====> START")
        prompt = request.POST.get("prompt")
        response = get_completion(prompt)
        print("====> END")
        return JsonResponse({"response": response})
    return render(
        request, "query.html", {"update_text": FineTuningJob.get_lastest_update_date()}
    )
