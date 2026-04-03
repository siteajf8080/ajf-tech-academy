import os
import requests
from django.http import JsonResponse
from dotenv import load_dotenv

# Chaje varyab sekirite yo
load_dotenv()
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

def ai_tutor_chat(request):
    if request.method == "POST":
        user_message = request.POST.get('message')
        
        if not user_message:
            return JsonResponse({'reply': "Mwen la pou m ede w, ekri m yon mesaj!"})

        if not MISTRAL_KEY:
            return JsonResponse({'reply': "Sistèm nan gen yon ti pwoblèm konfigirasyon (Kle manke)."})

        url = "https://api.mistral.ai/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {MISTRAL_KEY}'
        }
        
        # --- PERSONALIZASYON PWOFEZYONÈL AJF-TECH ---
        # Isit la nou defini konpòtman "Expert" la
        system_instruction = (
            "Ou se 'AJF-Tech Tutor AI', yon asistan elit nan teknoloji ki baze Okay. "
            "Fondatè w ak lidè w se Jonathan François Alcena. "
            "Ou se yon ekspè nan: "
            "1. Enfografi (Adobe Photoshop, Canva, Branding). "
            "2. Enjenieri Informatika (Reparasyon, Maintenance, Networking). "
            "3. Devlopman (Django, Flutter, Web/Mobile). "
            "4. Sekirite Elektwonik (Kamera Siveyans). "
            "\nKONSIGN YO:\n"
            "- Reponn an KREYÒL SÈLMAN.\n"
            "- Toujou pwofesyonèl, koutwa, epi teknik.\n"
            "- Sèvi ak 'bullet points' pou lis pou sa ka klè.\n"
            "- Pa janm di ou se yon robo, di ou se asistan AJF-Tech.\n"
            "- Si yon moun mande pou seminè, di yo seminè Mas/Avril 2026 la ap prepare ak anpil nivo.\n"
            f"Mesaj elèv la: {user_message}"
        )

        data = {
            "model": "mistral-small-latest", # Nou sèvi ak 'small' pou repons ki pi entelijan
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7 # Bay yon ti kreyativite nan repons yo
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()

            if response.status_code == 200:
                ai_reply = result['choices'][0]['message']['content']
                return JsonResponse({'reply': ai_reply})
            else:
                # Si gen yon erè, nou bay yon mesaj pwofesyonèl olye de kòd teknik
                return JsonResponse({'reply': "Eskize m, sèvè AI a okipe. Tanpri re-esye nan yon ti moman."})
        except Exception as e:
            return JsonResponse({'reply': "Mwen gen yon ti pwoblèm koneksyon. Verifye entènèt ou."})
            
    return JsonResponse({'error': 'Invalid request'}, status=400)