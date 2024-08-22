from django.db import models

class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey('user_app.user', on_delete=models.CASCADE, null=True, related_name='%(class)s_creator')
    last_modified_by = models.ForeignKey('user_app.user', on_delete=models.CASCADE, null=True, related_name='%(class)s_last_modified_by', blank=True)

    class Meta:
        abstract = True