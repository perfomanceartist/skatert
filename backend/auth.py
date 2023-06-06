from users.models import Account, AuthTokens
import datetime


def check_token(nickname, tokenVal):
    account = Account.objects.filter(user__nickname=nickname).get()
    if account is None:
        return False

    token = AuthTokens.objects.filter(account=account).filter(token=tokenVal).get()
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