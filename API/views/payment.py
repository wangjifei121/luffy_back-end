from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin, ModelViewSet
from utils.userauth import UserAuth
from utils.response import BaseResponse
from rest_framework.response import Response

from utils.exceptions import CommonException

from API.models import Course, CouponRecord, PricePolicy, CourseDetail
import datetime


class PaymentView(APIView, ViewSetMixin):
    """
    支付接口===订单接口:

         1 接收数据

         2 校验数据

         3 生成订单（默认未支付状态）
             --- Order
             --- OrderDetail
             --- OrderDetail
             --- OrderDetail

         4 调支付宝的支付接口:
             返回的post：修改订单，修改优惠券，修改贝里
             返回的get： 查看订单状态

    """
    authentication_classes = [UserAuth]

    def create(self, request, *args, **kwargs):
        '''
        请求发送的数据:
        {
          courses:{
                        1:{
                           choose_price_id:1,
                           coupon_id:2,
                        },
                        2:{
                          choose_price_id:4,
                          coupon_record_id:3,
                          },
                    },

          global_coupon_id:3,

          beli:2000,
          total_money:2000

        }

        计算价格优先级

           （课程1原价格*课程1优惠券+课程2原价格*课程2优惠券）*通用优惠券-贝里/10

        '''

        res = BaseResponse()

        try:
            # 1 获取数据
            user = request.user
            beli = int(request.data.get("beli", 0))
            courses_dict = request.data.get("courses")
            global_coupon_id = request.data.get("global_coupon_id")
            total_money = request.data.get("total_money")

            # 2 校验数据

            # 2.1 校验内里数是否在登录用户实际拥有范围内
            if user.beli < beli:
                raise CommonException("贝里数有问题！", 1004)

            # 2.2 校验课程信息
            now = datetime.datetime.now()
            course_price_list = []
            for course_pk, course_info in courses_dict.items():

                # 2.2.2 校验课程是否存在
                course_obj = Course.objects.filter(pk=course_pk).first()
                if not course_obj:
                    raise CommonException("课程不存在！", 1002)

                if course_obj.status != 0:
                    raise CommonException("课程未上线或者已下线！", 1005)

                # 2.2.3 校验价格策略
                choose_price_id = course_info.get("choose_price_id")

                price_policy_all = course_obj.price_policy.all()

                if choose_price_id not in [obj.pk for obj in price_policy_all]:
                    raise CommonException("价格策略错误！", 1003)

                # 2.2.4 校验课程优惠券

                coupon_record_id = course_info.get("coupon_record_id")

                coupon_record = CouponRecord.objects.filter(pk=coupon_record_id,
                                                            user=user,
                                                            status=0,
                                                            coupon__valid_begin_date__lt=now,
                                                            coupon__valid_end_date__gt=now,
                                                            ).first()

                if not coupon_record:
                    raise CommonException("优惠券有问题！", 1006)

                rel_course_obj = coupon_record.coupon.content_object
                if course_obj != rel_course_obj:
                    raise CommonException("优惠券与课程不匹配！", 1007)

                # 计算优惠后的价格
                price = PricePolicy.objects.filter(pk=choose_price_id).first().price
                rebate_price = self.cal_price(price, coupon_record)
                course_price_list.append(rebate_price)

            # 2.3 校验通用优惠券合法性
            global_coupon_record = CouponRecord.objects.filter(pk=global_coupon_id,
                                                               user=user,
                                                               status=0,
                                                               coupon__valid_begin_date__lt=now,
                                                               coupon__valid_end_date__gt=now,
                                                               ).first()

            if not global_coupon_record:
                raise CommonException("通用优惠券有问题！", 1009)

            # 2.4 校验最终价格是否一致
            cal_price = self.cal_price(sum(course_price_list), global_coupon_record)

            final_price = cal_price - beli / 10

            if final_price < 0:
                final_price = 0

            if total_money != final_price:
                raise CommonException("支付价格有问题！", 1010)

            # 3 生成订单
            # Order记录
            # OrderDetail
            # OrderDetail

            # 4 调用支付宝接口

            # alipay = ali()
            # 生成支付的url
            # query_params = alipay.direct_pay(
            #     subject="Django课程",  # 商品简单描述
            #     out_trade_no="x2" + str(time.time()),  # 商户订单号
            #     total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
            # )
            #
            # pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
            #
            # return redirect(pay_url)

            # 注意：
            # POST请求访问notify_url：
            # 更改订单
            # 更改优惠券
            # 更改贝里数

            # GET请求return_url，用于页面的跳转展示

        except CommonException as e:
            res.code = 1004
            res.error = e.error

        return Response(res.dict)

    def cal_price(self, price, coupon_record):
        """
         price：原价格
         coupon_record：优惠券对象
         目的：计算优惠后的价格
        :param price:
        :param coupon_record:
        :return:
        """
        # 获取优惠券的类型
        coupon_type = coupon_record.coupon.coupon_type

        if coupon_type == 0:  # 立减券
            money_equivalent_value = coupon_record.coupon.money_equivalent_value
            rebate_price = price - money_equivalent_value
            if rebate_price < 0:
                rebate_price = 0
        elif coupon_type == 1:  # 满减券
            minimum_consume = coupon_record.coupon.minimum_consume
            if price > minimum_consume:
                money_equivalent_value = coupon_record.coupon.money_equivalent_value
                rebate_price = price - money_equivalent_value
            else:
                raise CommonException("优惠券不符合条件", 1008)
        elif coupon_type == 2:
            off_percent = coupon_record.coupon.off_percent
            rebate_price = price * (off_percent / 100)
        else:
            rebate_price = price

        return rebate_price
