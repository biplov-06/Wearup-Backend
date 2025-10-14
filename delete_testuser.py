from django.contrib.auth.models import User
User.objects.filter(username='testuser').delete()
print("Testuser deleted if it existed.")
