from django.apps import AppConfig


class MdiConfig(AppConfig):
    name = 'mdi'
    def ready(self):
        from mdi import signals