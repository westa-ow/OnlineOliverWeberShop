# shop/management/commands/expire_promocodes.py
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Removes expired activated promo codes and clears shopping carts in the Firestore'

    def handle(self, *args, **options):
        db = settings.FIRESTORE_CLIENT
        active_ref = db.collection('ActivePromocodes')
        cart_ref = db.collection('Cart')

        today = datetime.now().date()
        processed = 0

        for promo_doc in active_ref.stream():
            promo = promo_doc.to_dict()
            raw = promo.get('expiration_date')
            email = promo.get('email')
            code = promo.get('coupon_code') or promo.get('code', '')
            discount = promo.get('discount', 0) / 100.0

            if not (raw and email):
                continue

            try:
                expires_date = datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                logger.warning("Invalid date for promo %s: %r", promo_doc.id, raw)
                continue

            if expires_date >= today:
                continue

            processed += 1
            logger.info("Expiring promo %s for %s (expired %s). Promo code is %s",
                        promo_doc.id, email, raw, code)

            try:
                carts = cart_ref.where(field_path='emailOwner', op_string='==', value=email).stream()
            except Exception as e:
                logger.error("Failed to query carts for %s: %s", email, e, exc_info=True)
                continue

            for cart_doc in carts:
                try:
                    data = cart_doc.to_dict()
                    price = data.get('price')
                    if price is None:
                        continue

                    if discount >= 1.0:
                        logger.warning("Discount 100%% for promo %s — skipping price reset", promo_doc.id)
                        continue

                    original_price = price / (1 - discount) if discount > 0 else price

                    cart_doc.reference.update({
                        'price': original_price,
                    })
                    logger.debug(" -> Cart %s: price reset to %s", cart_doc.id, original_price)
                except Exception as e:
                    logger.error("Failed to update cart %s: %s", cart_doc.id, e, exc_info=True)
            try:
                promo_doc.reference.delete()
                logger.info(" -> ActivePromocode %s deleted", promo_doc.id)
            except Exception as e:
                logger.error("Failed to delete promo %s: %s", promo_doc.id, e, exc_info=True)


        logger.info("Finished: processed %d expired promos", processed)
        self.stdout.write(self.style.SUCCESS(f"Processed {processed} expired promos"))
