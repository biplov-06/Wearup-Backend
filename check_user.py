from django.contrib.auth.models import User
try:
    user = User.objects.get(username='testuser')
    print("User exists:", user)
except User.DoesNotExist:
    print("User does not exist.")
