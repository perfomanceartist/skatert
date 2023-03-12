from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
from django.core.mail import send_mail

def index(request):
    return HttpResponse("API")



def email_auth(request):
    if request.method == "POST":
        user = request.POST.get("email", "s.sorockoletov@ya.ru")    
        subject = 'Skatert. Код Подтверждения входа'
        ###
        code = '123456'
        ###
        message = f'Код подтверждения для входа в Skatert: {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user, ]
        send_mail( subject, message, email_from, recipient_list, fail_silently=False)
        return HttpResponse("Success")
    else:
        return HttpResponseBadRequest("Некорректные данные")