from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .choices import JOB_POSITION, USER_REGION
from django.urls import reverse
from django.contrib.auth.models import Permission


JOB_POSITION_DICT = {
    'Не_определено': "Нет должности",
    'Делопроизводитель': "Делопроизводитель",
    'Генеральный_директор': "Генеральный директор",
    'Руководитель_ОИ': "Руководитель органа инспекции",
    'Руководитель_ИЛ': "Руководитель ИЛ",
    'Инженер_лаборатории': "Инженер лаборатории",
    'Инженер_инспектор': "Инженер инспектор"
}


class Department(models.Model):
    name            = models.CharField(max_length=128, primary_key=True)
    description     = models.TextField(verbose_name='Описание', max_length=1024, null=True)
    default_perm    = models.ForeignKey(to=Permission,
                                        verbose_name='Права по умолчанию',
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True)


class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    region      = models.CharField(verbose_name='Регион', max_length=256, choices=USER_REGION, default='Ульяновск')
    create_date = models.DateField(verbose_name='Дата создания', auto_now_add=True, auto_now=False)
    avatar      = models.ImageField(verbose_name='Аватар', upload_to='avatar/images/',
                                    default='avatar/images/default_avatar.jpg',
                                    max_length=200)
    position    = models.CharField(verbose_name='Должность', max_length=128, choices=JOB_POSITION, default='Не_определено')
    is_new      = models.BooleanField(verbose_name='Новый', default=False) # null=True, default=True
    department  = models.ForeignKey(verbose_name='Подразделение', to='Department', on_delete=models.CASCADE, null=True, blank=True)
    initials    = models.CharField(max_length=128, null=True, blank=True)
    unique_id   = models.PositiveIntegerField(verbose_name='Идентификатор', null=True, blank=True)
    role_id     = models.PositiveSmallIntegerField(verbose_name='Идентификатор роли', null=True, blank=True)

    class Meta:
        permissions = (
            ('can_view_orders', 'Profile can view ORDERS workflow'),
            ('can_view_laboratory', 'Profile can view laboratory functions'),
            ('can_manage_devices', 'Profile can can manage with devices operations'),
            ('can_view_inspection', 'Profile can view inspection activities'),
            ('can_view_sout', 'Profile can view SOUT activities'),
            ('can_view_stats', 'Profile can view statistics'),
            ('can_distribute_job', 'Profile can distribute job'),
            ('can_upload_rpn_files', 'Profile can UPLOAD RPN Files'),
            ('can_search_rpn_files', 'Profile can Search RPN Files'),
            ('site_administrator', 'Profile can manage web application'),
        )

    def get_absolute_url(self):
        return reverse("site_admin:staff-detail", args=(self.user.username,))

    def get_position(self):
        if JOB_POSITION_DICT.get(self.position, None):
            return JOB_POSITION_DICT[self.position]
        else:
            return "Нет должности"


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        profile_ins = Profile.objects.create(user=instance)

        # # Add default values to profile
        profile_ins.is_new = True
        profile_ins.save()
