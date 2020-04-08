from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    first_page = models.CharField(max_length=100)
    image_name = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Job(models.Model):
    source = models.ForeignKey(Source, models.PROTECT)
    company = models.ForeignKey(Company, models.PROTECT)
    title = models.CharField(max_length=255)
    desc = models.TextField()
    url = models.CharField(max_length=255)
    tech = models.TextField()
    start_count = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} @ {self.company}'

    @property
    def real_count(self):
        return self.count - self.start_count

    @property
    def tech_list(self):
        return self.tech.split(',') if self.tech else []


class Search(models.Model):
    term = models.CharField(max_length=255)
    count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Searches"

    def __str__(self):
        return self.term
