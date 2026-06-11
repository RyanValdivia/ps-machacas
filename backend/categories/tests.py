import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestProductCategoryModel:
    # TEST: crear categoria con todos los campos
    def test_create_category(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        assert cat.catproCode == "XX"
        assert cat.catproNom == "Xyz"
        assert cat.catproRequiereInventario is True

    # TEST: str representation
    def test_str(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="YY", catproNom="Why")
        assert str(cat) == "YY - Why"

    # TEST: save uppercases catproCode
    def test_code_uppercase_on_save(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="xx", catproNom="Xyz")
        assert cat.catproCode == "XX"

    # TEST: save titlecases catproNom
    def test_nom_title_on_save(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="XX", catproNom="xyz")
        assert cat.catproNom == "Xyz"

    # TEST: save strips whitespace from catproCode
    def test_code_strip_on_save(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="  xx  ", catproNom="Xyz")
        assert cat.catproCode == "XX"

    # TEST: save strips whitespace from catproNom
    def test_nom_strip_on_save(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="XX", catproNom="  xyz  ")
        assert cat.catproNom == "Xyz"

    # TEST: unique constraint on catproCode via full_clean
    def test_unique_code(self):
        from categories.models import ProductCategory
        ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        with pytest.raises(ValidationError):
            ProductCategory.objects.create(catproCode="XX", catproNom="Otra")

    # TEST: unique constraint on catproNom via full_clean
    def test_unique_nom(self):
        from categories.models import ProductCategory
        ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        with pytest.raises(ValidationError):
            ProductCategory.objects.create(catproCode="YY", catproNom="Xyz")

    # TEST: default requiereInventario is True
    def test_default_requiere_inventario(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="ZZ", catproNom="Zeta")
        assert cat.catproRequiereInventario is True

    # TEST: puede crear con catproRequiereInventario=False
    def test_requiere_inventario_false(self):
        from categories.models import ProductCategory
        cat = ProductCategory.objects.create(catproCode="NN", catproNom="NoInv", catproRequiereInventario=False)
        assert cat.catproRequiereInventario is False

    # TEST: full_clean se ejecuta en save
    def test_full_clean_on_save(self):
        from categories.models import ProductCategory
        with pytest.raises(ValidationError):
            ProductCategory.objects.create(catproCode="", catproNom="Vacio")

    # TEST: code vacio lanza error
    def test_code_vacio(self):
        from categories.models import ProductCategory
        with pytest.raises(ValidationError):
            ProductCategory.objects.create(catproCode="", catproNom="Test")

    # TEST: nom vacio lanza error
    def test_nom_vacio(self):
        from categories.models import ProductCategory
        with pytest.raises(ValidationError):
            ProductCategory.objects.create(catproCode="TE", catproNom="")


@pytest.mark.django_db
class TestProductCategorySerializer:
    # TEST: serializer con todos los campos
    def test_serializer_all_fields(self):
        from categories.models import ProductCategory
        from categories.serializers import ProductCategorySerializer
        cat = ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        serializer = ProductCategorySerializer(cat)
        assert serializer.data['catproCode'] == "XX"
        assert serializer.data['catproNom'] == "Xyz"
        assert serializer.data['catproRequiereInventario'] is True
        assert serializer.data['catproCod'] == cat.catproCod

    # TEST: serializer valid data
    def test_serializer_valid(self):
        from categories.serializers import ProductCategorySerializer
        data = {"catproCode": "YY", "catproNom": "Why"}
        serializer = ProductCategorySerializer(data=data)
        assert serializer.is_valid()

    # TEST: serializer invalid sin code
    def test_serializer_invalid_sin_code(self):
        from categories.serializers import ProductCategorySerializer
        data = {"catproNom": "Test"}
        serializer = ProductCategorySerializer(data=data)
        assert not serializer.is_valid()

    # TEST: serializer invalid sin nom
    def test_serializer_invalid_sin_nom(self):
        from categories.serializers import ProductCategorySerializer
        data = {"catproCode": "TE"}
        serializer = ProductCategorySerializer(data=data)
        assert not serializer.is_valid()

    # TEST: serializer with requiereInventario=false
    def test_serializer_requiere_inventario_false(self):
        from categories.serializers import ProductCategorySerializer
        data = {"catproCode": "NN", "catproNom": "NoInv", "catproRequiereInventario": False}
        serializer = ProductCategorySerializer(data=data)
        assert serializer.is_valid()

    # TEST: serializer empty data
    def test_serializer_empty(self):
        from categories.serializers import ProductCategorySerializer
        serializer = ProductCategorySerializer(data={})
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestProductCategoryViewSet:
    # TEST: list sin autenticacion retorna 401
    def test_list_unauthenticated(self, api_client):
        resp = api_client.get("/api/categories/categories/")
        assert resp.status_code == 401

    # TEST: list autenticado retorna 200
    def test_list(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="testcat", usuContra="pass", usuEmail="testcat@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/categories/categories/")
        assert resp.status_code == 200

    # TEST: list retorna datos incluyendo semilla
    def test_list_with_data(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat2", usuContra="pass", usuEmail="testcat2@test.com")
        ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/categories/categories/")
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    # TEST: create categoria
    def test_create(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="testcat3", usuContra="pass", usuEmail="testcat3@test.com")
        api_client.force_authenticate(user=user)
        data = {"catproCode": "ZZ", "catproNom": "Zeta"}
        resp = api_client.post("/api/categories/categories/", data, format="json")
        assert resp.status_code == 201
        assert resp.data["catproCode"] == "ZZ"
        assert resp.data["catproNom"] == "Zeta"

    # TEST: create uppercase conversion
    def test_create_uppercase_conversion(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="testcat4", usuContra="pass", usuEmail="testcat4@test.com")
        api_client.force_authenticate(user=user)
        data = {"catproCode": "zz", "catproNom": "zeta"}
        resp = api_client.post("/api/categories/categories/", data, format="json")
        assert resp.status_code == 201
        assert resp.data["catproCode"] == "ZZ"
        assert resp.data["catproNom"] == "Zeta"

    # TEST: retrieve categoria
    def test_retrieve(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat5", usuContra="pass", usuEmail="testcat5@test.com")
        cat = ProductCategory.objects.create(catproCode="YY", catproNom="Why")
        api_client.force_authenticate(user=user)
        resp = api_client.get(f"/api/categories/categories/{cat.catproCod}/")
        assert resp.status_code == 200
        assert resp.data["catproNom"] == "Why"

    # TEST: update categoria
    def test_update(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat6", usuContra="pass", usuEmail="testcat6@test.com")
        cat = ProductCategory.objects.create(catproCode="YY", catproNom="Why")
        api_client.force_authenticate(user=user)
        resp = api_client.put(f"/api/categories/categories/{cat.catproCod}/",
            {"catproCode": "YY", "catproNom": "Why Edit"}, format="json")
        assert resp.status_code == 200
        assert resp.data["catproNom"] == "Why Edit"

    # TEST: partial update categoria
    def test_partial_update(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat7", usuContra="pass", usuEmail="testcat7@test.com")
        cat = ProductCategory.objects.create(catproCode="YY", catproNom="Why")
        api_client.force_authenticate(user=user)
        resp = api_client.patch(f"/api/categories/categories/{cat.catproCod}/",
            {"catproNom": "Why Parcial"}, format="json")
        assert resp.status_code == 200
        assert resp.data["catproNom"] == "Why Parcial"

    # TEST: delete categoria
    def test_destroy(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat8", usuContra="pass", usuEmail="testcat8@test.com")
        cat = ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        api_client.force_authenticate(user=user)
        resp = api_client.delete(f"/api/categories/categories/{cat.catproCod}/")
        assert resp.status_code == 204

    # TEST: create duplicate code retorna 400
    def test_create_duplicate_code(self, api_client):
        from users.models import User
        from categories.models import ProductCategory
        user = User.objects.create_user(usuNom="testcat9", usuContra="pass", usuEmail="testcat9@test.com")
        ProductCategory.objects.create(catproCode="XX", catproNom="Xyz")
        api_client.force_authenticate(user=user)
        data = {"catproCode": "XX", "catproNom": "Otra"}
        resp = api_client.post("/api/categories/categories/", data, format="json")
        assert resp.status_code == 400

    # TEST: list retorna datos semilla
    def test_list_returns_seed_data(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="testcat10", usuContra="pass", usuEmail="testcat10@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/categories/categories/")
        assert resp.status_code == 200
        assert len(resp.data) >= 1


@pytest.mark.django_db
class TestProductCategoryUrls:
    # TEST: resolve categories list
    def test_list_url(self):
        from django.urls import resolve
        resolver = resolve("/api/categories/categories/")
        assert resolver.view_name == "productcategory-list"

    # TEST: resolve categories detail
    def test_detail_url(self):
        from django.urls import resolve
        resolver = resolve("/api/categories/categories/1/")
        assert resolver.view_name == "productcategory-detail"
