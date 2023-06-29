from django.db import models

class Titles(models.Model):
    using = "IMDB"
    tconst = models.CharField(primary_key=True, max_length=1000)
    titletype = models.CharField(max_length=1000, blank=True, null=True)
    primarytitle = models.CharField(max_length=1000, blank=True, null=True)
    originaltitle = models.CharField(max_length=1000, blank=True, null=True)
    isadult = models.CharField(max_length=1000, blank=True, null=True)
    startyear = models.CharField(max_length=1000, blank=True, null=True)
    endyear = models.CharField(max_length=1000, blank=True, null=True)
    runtimeminutes = models.CharField(max_length=1000, blank=True, null=True)
    genres = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'titles'
