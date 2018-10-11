from API import models
from rest_framework.viewsets import ModelViewSet
from API.serializer.courseserializer import CourseSerializer


class Courselist(ModelViewSet):
    """
    课程类的API
    """
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer
