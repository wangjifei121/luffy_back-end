from API import models
from rest_framework.views import APIView
import uuid
from rest_framework.response import Response
from utils.response import BaseResponse


class LoginView(APIView):
    """
    登录认证的逻辑
    """

    def post(self, request):
        reply = BaseResponse()
        try:
            name = request.data.get("username")
            pwd = request.data.get("pwd")

            user_obj = models.Userinfo.objects.filter(name=name, pwd=pwd).first()
            if user_obj:
                random_str = uuid.uuid4()
                models.UserToken.objects.update_or_create(user=user_obj, defaults={"token": random_str})
                reply.user = user_obj.name
                reply.token = random_str

            else:
                reply.code = 1001
                reply.error = "用户名或者密码错误"
        except Exception as e:
            reply.code = 1002
            reply.error = str(e)

        return Response(reply.dict)
