from rest_framework.viewsets import ModelViewSet
from API import models
from API.serializer.coursedetailSerializer import CourseDetailSerializer


class CourseDetail(ModelViewSet):
    """
    课程详情的API
    """
    queryset = models.CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
