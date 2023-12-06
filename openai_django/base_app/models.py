from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


class SourceType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class FineTuningJob(models.Model):
    openai_id = models.CharField(max_length=256, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    prior_model = models.CharField(max_length=256, null=False, blank=False)
    # post-completion
    # status = models.CharField(max_length=256, null=True, blank=True)
    # error_message = models.CharField(max_length=256, null=True, blank=True)
    fine_tuned_model = models.CharField(max_length=256, null=True, blank=True)


class Example(models.Model):
    prompt_text = models.TextField()
    completion_text = models.TextField()
    is_approved = models.BooleanField(
        default=False, help_text="Approved for fine-tuning"
    )
    # was_processed = models.BooleanField(
    #     default=False, help_text="Processed in a prior fine-tuning run"
    # )
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_type = models.ForeignKey(
        SourceType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The source of the record",
    )
    private_reference = models.URLField(
        null=True, blank=True, help_text="Not used in fine-tuning"
    )
    # reference = models.URLField(max_length=200, blank=True)
    private_note = models.TextField(
        null=True, blank=True, help_text="Not used in fine-tuning"
    )
    fine_tuning_job = models.ForeignKey(
        FineTuningJob, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return (
            f"Example created by {self.created_by.username} on {self.created_at.date()}"
        )
