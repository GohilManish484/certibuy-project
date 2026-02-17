from django.apps import AppConfig


class InspectionsConfig(AppConfig):
    name = 'inspections'
    
    def ready(self):
        import inspections.signals
