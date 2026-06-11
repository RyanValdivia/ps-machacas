import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registrame.settings')
import django
django.setup()
from django.conf import settings
db = settings.DATABASES['default']
print(f"ENGINE: {db['ENGINE']}")
print(f"NAME: {db['NAME']}")
print(f"USER: {db['USER']}")
print(f"HOST: {db['HOST']}")
print(f"PORT: {db['PORT']}")
print(f"PASSWORD has len: {len(db['PASSWORD'])}")
