import datetime
from django.db import models


class ExpiredCertificateManager(models.Manager):
    """
    This special manager only retrieves active objects (when the current date
    is between the object's publish date and/or its expiration date).

    The date fields are given when creating the Manager instance. If either is
    None then the manager will not take it into account for filtering.

    Example definition for a model:

    class ExampleModel(models.Model):
        publish_date = models.DateTimeField()
        expire_date = models.DateTimeField(blank=True, null=True)

        actives = ActiveManager(from_date='publish_date', to_date='expire_date')

    Or if the model only had an expire_date:

    class ExampleModel(models.Model):
        expire_date = models.DateTimeField(blank=True, null=True)

        actives = ActiveManager(from_date=None, to_date='expire_date')

    Each instance of the manager has an attribute date_filters which can be used in
    custom queries. For example, if you have a ManyToMany relationship to a model
    with ActiveManager and you can't access via the manager (because you
    need to use select_related, for example) then you can do:

    instance.many_to_many.filter(*ExampleModel.actives.date_filters)

    """

    def __init__(self, delta_days=7):
        super(ExpiredCertificateManager, self).__init__()
        self.delta_days = delta_days
        now = datetime.date.today()
        warn_date = now + datetime.timedelta(days=self.delta_days)
        self.date_filters = (models.Q(**{'expire_date__lte': warn_date}),
                             models.Q(**{'status': 'active'}))

    def get_query_set(self):
        """Retrieves items with publication dates according to self.date_filters
        """
        return super(ExpiredCertificateManager, self).get_query_set().filter(*self.date_filters)