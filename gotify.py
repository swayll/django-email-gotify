import threading
from typing import override

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from gotify import Gotify


class GotifyMessage(BaseEmailBackend):
    @override
    def __init__(
        self,
        fail_silently=True,
        base_url=settings.GOTIFY_URL,
        app_token=settings.GOTIFY_TOKEN,
        client_token=settings.GOTIFY_CLIENT,
        *args,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently, *args, **kwargs)
        self._lock = threading.RLock()
        self.gotify = Gotify(
            base_url=base_url,
            app_token=app_token,
            client_token=client_token,
        )

    @override
    def open(self):
        try:
            self.gotify.get_health()
        except Exception as e:
            raise e
        return None

    def write_message(self, message, subject):
        return self.gotify.create_message(
            message=str(message.body),
            if isinstance(message, EmailMessage)
            else str(message),
            title=str(message.subject)
            if isinstance(message, EmailMessage)
            else str(subject),
        )

    @override
    def send_messages(self, email_messages, subject="Subject"):
        if not email_messages:
            return 0
        msg_count = 0
        with self._lock:
            try:
                self.open()
                for message in email_messages:
                    self.write_message(message, subject)
                    msg_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return msg_count

