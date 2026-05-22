from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    it's a service for using email instead of username 
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email manzili kiritilishi shart!"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        when we use createsuperuser command, not for asking us to use username
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser uchun is_staff=True bo\'lishi shart.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Super uchun is_superuser=True bo\'lishi shart.'))
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
class GovService(models.Model):
    title = models.CharField(max_length=255, verbose_name="Xizmat nomi")
    keywords = models.TextField(help_text="Vergul bilan ajratilgan kalit so'zlar (masalan: guvohnoma, tug'ilish, bola)")
    instructions = models.TextField(help_text="Bosqichma-bosqich my.gov.uz yo'riqnomasi")
    
    class Meta:
        verbose_name = "Davlat xizmati"
        verbose_name_plural = "Davlat xizmatlari"
        
    def __str__(self):
        return self.title
    
class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Yangi suhbat")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.title}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']