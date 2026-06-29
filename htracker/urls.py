from django.urls import path
from rest_framework.routers import DefaultRouter
from htracker.apps import HtrackerConfig
from htracker.views import HabitsViewSet, UserHabitViewSet, PublishedHabitListAPIView

app_name = HtrackerConfig.name

router = DefaultRouter()
router.register(r"htracker", HabitsViewSet, basename="htracker")

urlpatterns = [
    path("user-htracker-list/", UserHabitViewSet.as_view(), name="user_htracker_list"),
    path("user-htracker-list-published/", PublishedHabitListAPIView.as_view(), name="user_htracker_list_published"),
] + router.urls