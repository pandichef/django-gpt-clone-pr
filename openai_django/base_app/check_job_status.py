from django.contrib import messages
from openai import OpenAI
from .models import FineTuningJob
from datetime import datetime, timedelta, timezone

wait_time_hours = 0  # don't expect fine-tuning to be ready for a while


class CheckJobStatus:
    # At some point this should be an always on task
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This code will run before the view is called for each request.
        # You can execute your script here.
        # Example:
        # my_script()
        # print("hello world")
        from time import time

        t0 = time()
        running_jobs = FineTuningJob.objects.all().filter(job_status="Running")
        last_job = running_jobs.last()
        if running_jobs.count() > 1:
            messages.success(
                request,
                "Something went wrong.  Only one OpenAI job can be running at the same time.",
            )
        elif running_jobs.count() == 1 and datetime.now(
            timezone.utc
        ) > last_job.created_at + timedelta(hours=wait_time_hours):
            # last_job = running_jobs.first()
            client = OpenAI()
            openai_job_object = client.fine_tuning.jobs.retrieve(last_job.openai_id)
            if openai_job_object.status == "cancelled":
                last_job.error_message = "Cancelled"
                last_job.save()
                related_examples = last_job.example_set.all()
                for example in related_examples:
                    example.fine_tuning_job = None
                    example.save()
            elif openai_job_object.error:
                last_job.error_message = openai_job_object.error.message
                last_job.save()
                related_examples = last_job.example_set.all()
                for example in related_examples:
                    example.fine_tuning_job = None
                    example.save()
            elif openai_job_object.fine_tuned_model:
                last_job.fine_tuned_model = openai_job_object.fine_tuned_model
                last_job.save()
            # print(openai_job_object)
            print(f"Job {last_job.openai_id} status: {openai_job_object.status}")
        print(f"Middleware runtime: {time()-t0}")
        response = self.get_response(request)

        # This code will run after the view is called for each request.
        # You can execute additional logic here.

        return response
