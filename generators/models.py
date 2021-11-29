from django.db import models
from django.urls import reverse
from django.db.models import Max

# Create your models here.


class Generator(models.Model):
    no = models.IntegerField(verbose_name='Текущий номер')
    gen_type = models.CharField(verbose_name='Префикс', max_length=32)
    year = models.CharField(verbose_name='Год', max_length=16)
    use_area = models.CharField(verbose_name='Область применения', max_length=128, primary_key=True)

    def get_absolute_url(self):
        return reverse("generators:generator-detail", args=(self.use_area,))

    def __str__(self):
        return '%s%s%s' % (self.no, self.gen_type, self.year)

    @staticmethod
    def get_last(use_area):
        obj = Generator.objects.filter(use_area=use_area).first()
        return obj

    @staticmethod
    def set_new(use_area):
        last_obj = Generator.objects.filter(use_area=use_area).first()
        last_obj.no = last_obj.no + 1
        last_obj.save()
        return last_obj
