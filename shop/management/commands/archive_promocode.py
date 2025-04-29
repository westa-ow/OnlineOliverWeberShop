# shop/management/commands/archive_promocode.py
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, date, time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archives expired master Promocodes to ExpiredPromocodes'

    def handle(self, *args, **options):
        db = settings.FIRESTORE_CLIENT
        master = db.collection('Promocodes')
        archive = db.collection('ExpiredPromocodes')
        today = datetime.now().date()
        print(today)
        count = 0
        for doc in master.stream():
            data = doc.to_dict()
            raw = data.get('expiration_date')
            if not raw:
                continue

            try:
                expires_date = datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                logger.warning("Invalid date format for promo %s: %r", doc.id, raw)
                continue

            if expires_date < today:
                count += 1
                logger.info(
                    "Archiving promo %s (code=%s, expired=%s)",
                    doc.id, data.get('code'), raw
                )
                archive.document(doc.id).set({
                    **data,
                    'archived_at': datetime.now().isoformat(),
                })
                doc.reference.delete()


        msg = f"Archived {count} expired promos"
        logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

