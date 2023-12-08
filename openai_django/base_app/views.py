from django.shortcuts import render
from django.http import JsonResponse
from .models import FineTuningJob
from .oai_queries import get_completion


def query_view(request):
    print("====> START")
    if request.method == "POST":
        prompt = request.POST.get("prompt")
        response = get_completion(prompt)
        return JsonResponse({"response": response})
    print("====> END")
    return render(
        request, "query.html", {"update_text": FineTuningJob.get_lastest_update_date()}
    )
