import logging
from datetime import datetime

from axes.signals import user_locked_out
from django.dispatch import receiver

from OnlineShop import settings

logger = logging.getLogger(__name__)

@receiver(user_locked_out)
def axes_user_locked_out(sender, request, username, ip_address, **kwargs):
    cooloff = settings.AXES_COOLOFF_TIME
    unlock_time = datetime.now() + cooloff
    # Save the timestamp in timestamp format
    request.session['axes_locked_until'] = unlock_time.timestamp()
    logger.warning("User locked out: username=%s, ip=%s until %s", username, ip_address, unlock_time)
