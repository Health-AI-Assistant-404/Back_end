from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User

import json
import traceback

from openai import OpenAI
from .models import Message


SYSTEM_PROMPT = """
You are HealthAI.
You provide general health information only.
You do not diagnose or prescribe.
Always recommend consulting a doctor.
If the user asks for diagnosis or medication, politely refuse.
Answer in Persian.
"""


def build_messages():
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    last_messages = Message.objects.order_by("-timestamp")[:10][::-1]

    for m in last_messages:
        role = "assistant" if m.sender.username == "healthai" else "user"
        messages.append({
            "role": role,
            "content": m.text
        })

    return messages


@csrf_exempt
def chat_api(request):

    # ======================
    # GET
    # ======================
    if request.method == "GET":
        messages = Message.objects.all().order_by("timestamp")
        return JsonResponse([
            {
                "sender": m.sender.username,
                "text": m.text,
                "time": m.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for m in messages
        ], safe=False)

    # ======================
    # POST
    # ======================
    if request.method == "POST":

        if not settings.OPENAI_API_KEY:
            return JsonResponse(
                {"error": "API key not configured"},
                status=500
            )

        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )

        try:
            body = json.loads(request.body.decode("utf-8"))
            username = body.get("sender")
            text = body.get("text")

            if not username or not text:
                return JsonResponse(
                    {"error": "sender and text are required"},
                    status=400
                )

            user = User.objects.get(username=username)
            ai_user = User.objects.get(username="healthai")

            # ذخیره پیام کاربر
            user_msg = Message.objects.create(
                sender=user,
                text=text
            )

            # ساخت کانتکست
            messages = build_messages()
            messages.append({
                "role": "user",
                "content": text
            })

            # ===== درخواست به DeepSeek =====
            response = client.responses.create(
                model="deepseek-chat",
                input=messages
            )

            # ===== استخراج امن متن پاسخ =====
            ai_text = ""

            for item in response.output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            ai_text += content.get("text", "")

            if not ai_text:
                ai_text = "متأسفم، پاسخی دریافت نشد. لطفاً دوباره تلاش کنید."

            # ذخیره پاسخ AI
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

        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User not found"},
                status=400
            )

        except Exception as e:
            return JsonResponse({
                "error": str(e),
                "trace": traceback.format_exc()
            }, status=500)

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )
