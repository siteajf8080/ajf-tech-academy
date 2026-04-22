import os

import requests
from django.http import JsonResponse


def ai_tutor_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    mistral_key = os.getenv("MISTRAL_API_KEY", "")
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return JsonResponse({"reply": "Mwen la pou m ede w, ekri m yon mesaj!"})

    if not mistral_key:
        return JsonResponse(
            {"reply": "Sistem nan gen yon ti pwoblem konfigirasyon. Kle API a manke."}
        )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {mistral_key}",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ou se AJF-Tech Tutor AI, yon asistan teknik AJF-Tech. "
                    "Reponn an kreyol selman, rete koutwa, teknik, ak klè. "
                    "Si sa itil, sevi ak pwen bal pou esplike etap yo."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )
        result = response.json()
    except requests.RequestException:
        return JsonResponse(
            {"reply": "Mwen gen yon ti pwoblem koneksyon. Verifye entenet la epi re-eseye."}
        )

    if response.status_code != 200:
        return JsonResponse(
            {"reply": "Eskize m, seve AI a okipe pou kounye a. Tanpri re-eseye pita."}
        )

    try:
        ai_reply = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return JsonResponse(
            {"reply": "Sistwm AI a voye yon repons ki pa konple. Tanpri eseye ankò."}
        )

    return JsonResponse({"reply": ai_reply})
