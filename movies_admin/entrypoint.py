import subprocess
import sys

from loguru import logger

COMMANDS = (
    'python manage.py makemigrations',
    'python manage.py migrate --fake-initial',
    'python manage.py createsuperuser --noinput',
    'python manage.py runserver 0.0.0.0:8000'
)

logger.info('Запуск entrypoint.py')
for command in COMMANDS:
    exit_code = subprocess.run(command.split()).returncode

    if exit_code:
        sys.exit(exit_code)
