from celery.task import task
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from openbudget.apps.transport.incoming.parsers import get_parser
# TODO: this can't use local
from openbudget.settings import local as settings


@task(name='tasks.save_import')
def save_import(deferred, email):

    from openbudget.apps.transport.incoming.importers.tablibimporter import TablibImporter

    importer = TablibImporter()
    saved = importer.resolve(deferred).save()

    sender = settings.EMAIL_HOST_USER
    recipient = email

    container = deferred['container']
    name = container.get('name', '')
    if not name:
        name = get_parser(deferred['class']).container_model._meta.verbose_name + ' of '
        entity = container.get('entity', None)
        period = container.get('period_start')
        if entity:
            try:
                entity_name = getattr(entity, 'name')
            except AttributeError:
                entity_name = entity.get('name')
            name += entity_name
        else:
            name += 'unknown'
        name += ' for ' + period

    if saved:
        subject = _('[OPEN BUDGET]: Data import success')
        message = _('The data import succeeded for ' + name)

    else:
        subject = _('[OPEN BUDGET]: Data import failure')
        message = _('The data import failed for ' + name)

    return send_mail(
        subject,
        message,
        sender,
        [recipient],
        fail_silently=True
    )
