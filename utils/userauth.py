from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from API import models


# 用于认证的类
class UserAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get("token")
        usertoken_obj = models.UserToken.objects.filter(token=token).first()
        if usertoken_obj:
            return usertoken_obj.user, usertoken_obj.token
        else:
            raise AuthenticationFailed("用户认证失败，您无权访问！！！")
