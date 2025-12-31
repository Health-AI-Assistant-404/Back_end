from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from openai import OpenAI

from django.conf import settings
from .models import Message
from django.contrib.auth.models import User


client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are HealthAI.
You provide general health information only.
You do not diagnose or prescribe.
Always recommend consulting a doctor.
Answer in Persian.
"""

def build_messages():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    last_messages = Message.objects.order_by("-timestamp")[:10][::-1]

    for m in last_messages:
        role = "assistant" if m.sender.username == "healthai" else "user"
        messages.append({"role": role, "content": m.text})

    return messages

@csrf_exempt
def chat_api(request):
    if request.method == "GET":
        messages = Message.objects.all().order_by("timestamp")
        data = [
            {
                "sender": m.sender.username,
                "text": m.text,
                "time": m.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for m in messages
        ]
        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        body = json.loads(request.body.decode("utf-8"))
        username = body.get("sender")
        text = body.get("text")

        try:
            user = User.objects.get(username=username)
            ai_user = User.objects.get(username="healthai")
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=400)

        # 1️⃣ ذخیره پیام کاربر
        user_msg = Message.objects.create(sender=user, text=text)

        # 2️⃣ ارسال به OpenAI
        messages = build_messages()
        messages.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )

        ai_text = response.choices[0].message.content

        # 3️⃣ ذخیره پاسخ AI
        ai_msg = Message.objects.create(
            sender=ai_user,
            text=ai_text
        )

        return JsonResponse({
            "user": {
                "sender": user_msg.sender.username,
                "text": user_msg.text,
                "time": user_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            },
            "ai": {
                "sender": ai_msg.sender.username,
                "text": ai_msg.text,
                "time": ai_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })



