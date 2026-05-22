from google import genai
from google.genai import types
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm
from .models import GovService, ChatMessage, ChatSession

from django.conf import settings

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat_new')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_new')
    else:
        form = UserRegisterForm()
    
    return render(request, 'assistant/register.html', {'form': form})




class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'assistant/login.html'
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('chat_new')
    
def logout_view(request):
    logout(request)
    return redirect('login')


# --- Main chat logic --- 
def chat_view(request, session_id=None):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Iltimos, savol berish uchun tizimga kiring yoki ro\'yxatdan o\'ting.', 'redirect': '/login/'}, status=401)

        user_text = request.POST.get('message', '').strip()
        req_session_id = request.POST.get('session_id')
        
        if not user_text:
            return JsonResponse({'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}, status=400)
            
        if req_session_id:
            session = get_object_or_404(ChatSession, id=req_session_id, user=request.user)
        else:
            title = user_text[:30] + ('...' if len(user_text) > 30 else '')
            session = ChatSession.objects.create(user=request.user, title=title)
            
        # Oldingi xabarlarni API formatiga o'tkazish (yangi xabar saqlanishidan oldin)
        history_messages = []
        for msg in session.messages.all().order_by('created_at')[:20]:
            role = "model" if msg.is_ai else "user"
            history_messages.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg.message)])
            )
        
        # 1. Foydalanuvchi xabarini bazaga saqlaymiz
        ChatMessage.objects.create(session=session, user=request.user, message=user_text, is_ai=False)
        
        # 2. Bazadan mos keluvchi yo'riqnomani qidiramiz
        matched_service = None
        for service in GovService.objects.all():
            keywords_list = [k.strip().lower() for k in service.keywords.split(',')]
            if any(keyword in user_text.lower() for keyword in keywords_list if keyword):
                matched_service = service
                break
            
        # 3. Prompt (Kontekst) tayyorlash
        if matched_service:
            context = f" [TIZIM XABARI: Quyidagi rasmiy yo'riqnoma topildi. Agar savol bunga oid bo'lsa, qat'iyan shu asosida javob bering:\n{matched_service.instructions}]"
        else:
            context = ""
            
        latest_prompt = f"""[TIZIM KO'RSATMASI: Siz my.gov.uz (Yagona interaktiv davlat xizmatlari portali) bo'yicha rasmiy, professional va malakali maslahatchisiz. 
Javobingiz rasmiy yozishmalar uslubida bo'lishi, qisqa va lo'nda bo'lishi shart.
Agar savol davlat xizmatlari, hujjatlar yoki oldingi suhbatga aloqador bo'lsa, o'z bilimingiz va oldingi xabarlar asosida yordam bering.{context}]

Foydalanuvchi so'rovi: {user_text}"""
        
        # 4. Gemini API orqali javob olish
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            chat = client.chats.create(model='gemini-2.5-flash', history=history_messages)
            response = chat.send_message(latest_prompt)
            ai_response = response.text
        except Exception as e:
            ai_response = "Kechirasiz, tizimda xatolik yuz berdi. Birozdan so'ng urinib ko'ring."

        # 5. AI javobini bazaga saqlaymiz
        ChatMessage.objects.create(session=session, user=request.user, message=ai_response, is_ai=True)
        
        return JsonResponse({
            'response': ai_response,
            'session_id': session.id,
            'is_new_session': not req_session_id
        })
        
    # GET so'rovlari uchun
    if request.user.is_authenticated:
        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        
        current_session = None
        history = []
        if session_id:
            current_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            history = current_session.messages.all().order_by('created_at')
            
        return render(request, 'assistant/chat.html', {
            'sessions': sessions,
            'current_session': current_session,
            'history': history,
        })
    else:
        if session_id:
            return redirect('login')
            
        return render(request, 'assistant/chat.html', {
            'sessions': [],
            'current_session': None,
            'history': [],
        })

@login_required(login_url='login')
def delete_chat(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return redirect('chat_new')