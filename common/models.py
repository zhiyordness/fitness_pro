from django.db import models

# Create your models here.

class BaseModel(models.Model):
    name = models.CharField(
        max_length=50,
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
    )
    updated_on = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True