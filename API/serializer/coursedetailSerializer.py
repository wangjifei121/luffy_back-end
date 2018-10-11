from rest_framework import serializers
from API import models


class CourseDetailSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name")
    recommend_courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    price_policy_list = serializers.SerializerMethodField()

    def get_price_policy_list(self, obj):
        temp = []
        for price_obj in obj.course.price_policy.all():
            temp.append({
                "pk": price_obj.pk,
                "price": price_obj.price,
                "valid_period": price_obj.valid_period,
                "valid_period_text": price_obj.get_valid_period_display()
            })
        return temp

    def get_recommend_courses(self, obj):
        temp = []
        for course_obj in obj.recommend_courses.all():
            temp.append({
                "course_id": course_obj.id,
                "course_name": course_obj.name,
            })

        return temp

    def get_teachers(self, obj):
        temp = []
        for teacher_obj in obj.teachers.all():
            temp.append({
                "teacher_name": teacher_obj.name,
                "teacher_image": teacher_obj.image,
                "teacher_brief": teacher_obj.brief
            })
        return temp

    class Meta:
        model = models.CourseDetail
        fields = "__all__"
