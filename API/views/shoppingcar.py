from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from utils.userauth import UserAuth
from utils.exceptions import PriceDoesNotExist
from API import models
from django.core.exceptions import ObjectDoesNotExist
from django_redis import get_redis_connection
import json
from utils.response import BaseResponse
from rest_framework.response import Response
from django.conf import global_settings

# 添加商品到购物车
class ShoppingCar(ViewSetMixin, APIView):
    """
    提交post请求，将提交课程存放redis中

        状态码：
             1000 : 成功
             1001 ：认证失败
             1002 : 课程不存在
             1003 : 价格策略不存在
             1004 : 要删除的课程不存在
    """
    authentication_classes = [UserAuth, ]
    # 创建reids链接
    redis = get_redis_connection()

    def list(self, request, *args, **kwargs):
        """ 查看购物车 """
        user_pk = request.user.pk
        #获取当前用户购物车中的key
        shopping_course_list = self.redis.keys("shopping_car_%s_*" % user_pk)

        #解码数据
        course_dict = {}
        for course in shopping_course_list:
            course_info = self.redis.hgetall(course.decode("utf8"))
            course_detail = {}
            for key, val in course_info.items():
                if key.decode("utf8") == "relate_price_policy":
                    course_detail[key.decode("utf8")] = json.loads(val.decode("utf8"))
                else:
                    course_detail[key.decode("utf8")] = val.decode("utf8")
            course_dict[course.decode("utf8")] = course_detail

        course_list = []
        for key in course_dict:
            course_dict[key]["course_id"] = key.split("_").pop()
            course_list.append(course_dict[key])

        return Response(course_list)

    def create(self, request, *args, **kwargs):
        """ 添加购物车 """
        reply = BaseResponse()
        try:
            # 1. 获取用户id
            user_pk = request.user.pk

            # 2. 获取课程id和对应的价格策略id
            course_id = request.data["course_id"]
            price_policy_id = request.data["price_policy_id"]

            # 3.校验课程数据合法性
            course_obj = models.Course.objects.get(pk=course_id)
            # 4. 校验课程关联的价格策略
            price_policy_list = course_obj.price_policy.all()

            # 构建价格策略字典
            price_policy_dict = {}
            for price_policy in price_policy_list:
                price_policy_dict[price_policy.pk] = {
                    "price": price_policy.price,
                    "valid_period": price_policy.valid_period,
                    "valid_period_text": price_policy.get_valid_period_display()
                }
            if price_policy_id not in price_policy_dict:
                raise PriceDoesNotExist

            # 5.redis中存储数据
            # 得到redis中存储的key
            shopping_car_key = "shopping_car_%s_%s" % (user_pk, course_id)
            # 构造value
            course_info = {
                "name": course_obj.name,
                "course_img": course_obj.course_img,
                "relate_price_policy": json.dumps(price_policy_dict),
                "default_price_policy_id": price_policy_id
            }
            reply.data = "更新购物车成功" if self.redis.exists(shopping_car_key) else "加入购物车成功"

            self.redis.hmset(shopping_car_key, course_info)


        except ObjectDoesNotExist as e:
            reply.code = "1002"
            reply.error = "课程不存在！！！"

        except PriceDoesNotExist as e:
            reply.code = "1003"
            reply.error = e.error

        except Exception as e:
            reply.code = "1004"
            reply.error = str(e)

        return Response(reply.dict)


    def destroy(self,request, *args, **kwargs):
        """ 删除购物车 """
        reply = BaseResponse()
        #1、获取用户id
        user_pk = request.user.pk
        #2、获取选中的课程id
        course_id = request.parser_context["kwargs"]["course_id"]
        #3、得到相应的shopping_car_key
        shopping_car_key = "shopping_car_%s_%s"%(user_pk,course_id)
        #4、从数据库中取出对应user的购物车记录
        shopping_car_course_list =[
            shopping_car_key.decode("utf8") for shopping_car_key in self.redis.keys("shopping_car_%s_*"%user_pk)
        ]
        #校验用户选中课程是否在购物车中
        if shopping_car_key in shopping_car_course_list:
            self.redis.delete(shopping_car_key)
            reply.data = "删除成功"
        else:
            reply.code = 1004
            reply.error = "要删除的课程不存在"

        return Response(reply.dict)

    def update(self,request, *args, **kwargs):
        pass
