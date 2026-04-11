#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.test import Client
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from core.models import User

user = User.objects.filter(username='Pablo').first()
if not user:
    raise SystemExit('Usuario Pablo no encontrado')

print('Usuario:', user.username, user.email)

client = Client()
uid = urlsafe_base64_encode(force_bytes(user.pk))
token = default_token_generator.make_token(user)
url = f'/password-reset/confirm/{uid}/{token}/'
print('URL:', url)

response = client.get(url, follow=True)
print('GET status:', response.status_code)
print('Final path:', response.request['PATH_INFO'])
print('Contains form:', b'new_password1' in response.content)
print('Invalid warning:', 'El enlace de restablecimiento de contraseña no es válido' in response.content.decode('utf-8', errors='ignore'))

response2 = client.post(response.request['PATH_INFO'], {
    'new_password1': 'NewPablo1234',
    'new_password2': 'NewPablo1234'
}, follow=True)
print('POST status:', response2.status_code)
print('POST final path:', response2.request['PATH_INFO'])
print('Complete page:', 'Contraseña restablecida' in response2.content.decode('utf-8', errors='ignore'))

print('Try login with old password:', client.login(username='Pablo', password='OldPasswordShouldntWork'))
client.logout()
print('Try login with new password:', client.login(username='Pablo', password='NewPablo1234'))
