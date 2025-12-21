from django_extensions.management.commands.runserver_plus import (
    Command as RunServerPlusCommand
)

class Command(RunServerPlusCommand):
    help = "Run Django development server with trusted HTTPS"

    def handle(self, *args, **options):
        options["cert_file"] = "127.0.0.1.pem"
        options["key_file"] = "127.0.0.1-key.pem"
        super().handle(*args, **options)
