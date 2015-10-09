from django.conf.urls import include, url,patterns
from rest_framework.routers import DefaultRouter
from views import ExamRegisterViewSet

router = DefaultRouter()
router.register(r'exam_register', ExamRegisterViewSet,
                base_name="exam_register")
urlpatterns = patterns(
    '',
    (r'^', include(router.urls)),
)
