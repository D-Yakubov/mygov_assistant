import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm
from .models import GovService, ChatMessage

from django.conf import settings

model = genai.GenerativeModel('gemini-3.5-flash')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserRegisterForm()
    
    return render(request, 'assistant/register.html', {'form': form})




class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'assistant/login.html'
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('chat')
    
def logout_view(request):
    logout(request)
    return redirect('login')


# --- Main chat logic --- 
@login_required(login_url='login')
def chat_view(request):
    if request.method == "POST":
        user_text = request.POST.get('message', '').strip()
        if not user_text:
            return JsonResponse({'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}, status=400)
        
        # 1. Foydalanuvchi xabarini bazaga saqlaymiz
        ChatMessage.objects.create(user=request.user, message=user_text, is_ai=False)
        
        # 2. Bazadan mos keluvchi yo'riqnomani qidiramiz
        matched_service = None
        for service in GovService.objects.all():
            keywords_list = [k.strip().lower() for k in service.keywords.split(',')]
            if any(keyword in user_text.lower() for keyword in keywords_list if keyword):
                matched_service = service
                break
            
        # 3. Prompt (Kontekst) tayyorlash
        if matched_service:
            context = f"Rasmiy yo'riqnoma:\n{matched_service.instructions}"
        else:
            context = "Tizimda bu xizmat haqida aniq yo'riqnoma topilmadi. Foydalanuvchiga faqat my.gov.uz saytiga kirib qidirishni chiroyli tushuntiring."
            
        full_prompt = f"""
        Siz my.gov.uz (Yagona interaktiv davlat xizmatlari portali) bo'yicha rasmiy, professional va malakali davlat xizmatlari maslahatchisisiz.
        Foydalanuvchiga taqdim etilgan rasmiy yo'riqnoma asosida aniq, tushunarli, va ortiqcha so'zlarsiz javob bering.
        Javobingiz rasmiy yozishmalar uslubida bo'lishi, ehtiyotkorlik bilan shakllantirilishi va foydalanuvchiga amaliy qadamlarni aniq ko'rsatishi shart.
        Agar yo'riqnomada aniq havola yoki bo'lim nomi bo'lsa, ularni alohida ajratib ko'rsating.

        Rasmiy ma'lumot:
        {context}

        Foydalanuvchi so'rovi: {user_text}
        
        Iltimos, javobni O'zbek tilida, qisqa va lo'nda qilib, rasmiy ohangda taqdim eting.
        """
        
        # 4. Gemini API orqali javob olish
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            response = model.generate_content(full_prompt)
            ai_response = response.text
        except Exception as e:
            ai_response = "Kechirasiz, tizimda xatolik yuz berdi. Birozdan so'ng urinib ko'ring."

        # 5. AI javobini bazaga saqlaymiz
        ChatMessage.objects.create(user=request.user, message=ai_response, is_ai=True)

        return JsonResponse({'response': ai_response})

    # Sahifa birinchi marta ochilganda eski xabarlar tarixini yuklaymiz
    history = ChatMessage.objects.filter(user=request.user)
    return render(request, 'assistant/chat.html', {'history': history})