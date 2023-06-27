from users.models import Account, AuthTokens
import datetime

def find_token(nickname, tokenVal):
    account = Account.objects.filter(user__nickname=nickname).get()
    if account is None:
        return None

    token = AuthTokens.objects.filter(account=account).filter(token=tokenVal).get()
    return token

def delete_token(request):    
    nickname = request.COOKIES.get("nickname")
    tokenVal = request.COOKIES.get("token")
    if nickname is None or tokenVal is None:
        return False
    
    token = find_token(nickname, tokenVal)
    if token is None:
        return False
    token.delete()
    return True


def check_token(nickname, tokenVal):    
    token = find_token(nickname, tokenVal)
    if token is None:
        return False
    
    if token.type != "email":
        return False

    if datetime.datetime.now().timestamp() > token.expiration_date.timestamp():
        token.delete()
        return False

    return True


def check_cookie(request):
    nickname = request.COOKIES.get("nickname")
    token = request.COOKIES.get("token")
    if nickname is None or token is None:
        return False
    return check_token(nickname, token)