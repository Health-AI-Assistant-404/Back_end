from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Message
from django.contrib.auth.models import User

@csrf_exempt
def chat_api(request):
    if request.method == "GET":
        # لیست همه پیام‌ها
        messages = Message.objects.all().order_by("timestamp")
        data = [
            {"sender": m.sender.username, "text": m.text, "time": m.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
            for m in messages
        ]
        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        # ذخیره پیام جدید
        body = json.loads(request.body.decode("utf-8"))
        username = body.get("sender")
        text = body.get("text")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=400)

        msg = Message.objects.create(sender=user, text=text, timestamp=timezone.now())
        return JsonResponse({"sender": msg.sender.username, "text": msg.text, "time": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")})
