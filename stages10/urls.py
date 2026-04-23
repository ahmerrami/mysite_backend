from rest_framework.routers import DefaultRouter
from .views import VilleViewSet, PeriodeViewSet, StageViewSet, CandidatViewSet, CandidatureViewSet

router = DefaultRouter()
router.register(r'villes', VilleViewSet)
router.register(r'periodes', PeriodeViewSet)
router.register(r'stages', StageViewSet)
router.register(r'candidats', CandidatViewSet)
router.register(r'candidatures', CandidatureViewSet)

urlpatterns = router.urls
