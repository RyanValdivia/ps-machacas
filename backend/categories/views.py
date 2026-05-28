from rest_framework.viewsets import ModelViewSet
from .models import ProductCategory
from .serializers import ProductCategorySerializer

class ProductCategoryViewSet(ModelViewSet):
  queryset = ProductCategory.objects.all()
  serializer_class = ProductCategorySerializer