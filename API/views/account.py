from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin, ModelViewSet
from utils.userauth import UserAuth
from utils.response import BaseResponse
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django_redis import get_redis_connection
from API.models import Course, PricePolicy, Coupon, CouponRecord
import json
import datetime


class AccountView(ViewSetMixin, APIView):
    """
    结算中心
    """
    authentication_classes = [UserAuth]
    redis = get_redis_connection("default")

    def create(self, request, *args, **kwargs):
        reply = BaseResponse()

        # 1 获取课程ID列表
        course_id_list = request.data.get('course_id_list')
        print(course_id_list)  # course_id_list：[1, 2]

        # 2 获取用户ID
        user_pk = request.user.pk

        # 清除
        keys = self.redis.keys("account_car_%s_*" % user_pk)
        if keys:
            self.redis.delete(*keys)

        # 3 循环处理课程列表
        try:
            for course_id in course_id_list:
                # 结算课程字典的键
                account_key = "account_car_%s_%s" % (user_pk, course_id)
                # 结算课程字典的值
                course_account = {}
                # 校验数据
                course_obj = Course.objects.get(pk=course_id)

                shopping_car_key = "shopping_car_%s_%s" % (user_pk, course_id)

                course_info = self.redis.hgetall(shopping_car_key)
                course_detail = {}

                for key, val in course_info.items():
                    if key.decode("utf8") == "relate_price_policy":
                        course_detail[key.decode("utf8")] = json.loads(val.decode("utf8"))
                    else:
                        course_detail[key.decode("utf8")] = val.decode("utf8")

                # course_account加入课程详细信息
                course_account["course_detail"] = course_detail

                # 查询该用户所有的有效的优惠券信息
                now = datetime.datetime.now()
                coupon_record_list = CouponRecord.objects.filter(user=user_pk,
                                                                 status=0,
                                                                 coupon__valid_begin_date__lt=now,
                                                                 coupon__valid_end_date__gt=now
                                                                 )
                # 课程专用券
                course_coupon_dict = {}
                # 通用券
                global_coupon_dict = {}
                print("coupon_record_list", coupon_record_list)
                for coupon_record in coupon_record_list:
                    coupon_info = {
                        "name": coupon_record.coupon.name,
                        "coupon_type": coupon_record.coupon.coupon_type,
                        "money_equivalent_value": coupon_record.coupon.money_equivalent_value or "",
                        "off_percent": coupon_record.coupon.off_percent or "",
                        "minimum_consume": coupon_record.coupon.minimum_consume or "",
                        "object_id": coupon_record.coupon.object_id or ""
                    }

                    object_id = coupon_info["object_id"]
                    if object_id:
                        # 专用券
                        course_coupon_dict[coupon_record.pk] = coupon_info
                    else:
                        # 通用券
                        global_coupon_dict[coupon_record.pk] = coupon_info

                # course_account加入课程专用优惠券信息
                course_account["course_coupon"] = json.dumps(course_coupon_dict)

                # 4 在redis写入结算数据
                self.redis.hmset(account_key, course_account)
                if global_coupon_dict:
                    self.redis.hmset("global_coupon_%s " % (user_pk), global_coupon_dict)
            reply.data = "结算成功"

        except ObjectDoesNotExist as e:
            reply.error = "课程不存在"
            reply.code = 1002

        except Exception as e:
            reply.code = 1003
            reply.error = str(e)

        return Response(reply.dict)

    def list(self, request, *args, **kwargs):
        pass
