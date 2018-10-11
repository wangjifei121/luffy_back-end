from rest_framework import serializers
from API import models


class CourseSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source="get_level_display")
    status = serializers.CharField(source="get_status_display")
    price_policy_list = serializers.SerializerMethodField()

    def get_price_policy_list(self, obj):
        temp = []
        for price_obj in obj.price_policy.all():
            temp.append({
                "pk": price_obj.pk,
                "price": price_obj.price,
                "valid_period": price_obj.valid_period,
                "valid_period_text": price_obj.get_valid_period_display()
            })
        return temp

    class Meta:
        model = models.Course
        fields = "__all__"
