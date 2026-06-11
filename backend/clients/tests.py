from django.test import TestCase
from decimal import Decimal
from datetime import date
from django.urls import reverse, resolve
from rest_framework.test import APIClient


class TestClientModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Client
        cls.cliente = Client.objects.create(
            cliTipoDoc="DNI", cliNumDoc="12345678",
            cliNomCompleto="cliente modelo", cliTelef="999888777",
            cliFechaNac=date(1990, 5, 15),
        )

    def test_create_client(self):
        assert self.cliente.cliTipoDoc == "DNI"
        assert self.cliente.cliNumDoc == "12345678"
        assert self.cliente.cliTelef == "999888777"
        assert self.cliente.cliFechaNac == date(1990, 5, 15)

    def test_nombre_uppercase_on_save(self):
        assert self.cliente.cliNomCompleto == "CLIENTE MODELO"

    def test_str_representation(self):
        assert str(self.cliente) == "CLIENTE MODELO (12345678)"

    def test_client_without_document(self):
        from clients.models import Client
        c = Client.objects.create(cliNomCompleto="sin documento")
        assert c.cliNumDoc is None
        assert c.cliTipoDoc == "DNI"

    def test_unique_num_doc(self):
        from clients.models import Client
        from django.db import IntegrityError
        Client.objects.create(cliTipoDoc="DNI", cliNumDoc="99999999", cliNomCompleto="Primero")
        with self.assertRaises(IntegrityError):
            Client.objects.create(cliTipoDoc="DNI", cliNumDoc="99999999", cliNomCompleto="Duplicado")

    def test_minimal_client(self):
        from clients.models import Client
        c = Client.objects.create(cliNomCompleto="Minimo")
        assert c.cliNomCompleto == "MINIMO"
        assert c.cliTipoDoc == "DNI"

    def test_null_telefono(self):
        from clients.models import Client
        c = Client.objects.create(cliNomCompleto="Sin Telefono")
        assert c.cliTelef is None or c.cliTelef == ""

    def test_blank_nombre_raises(self):
        from clients.models import Client
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Client.objects.create(cliNomCompleto=None)


class TestOptometristModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Optometrist
        cls.opt = Optometrist.objects.create(optNombre="Juan", optApellido="Perez")

    def test_create_optometrist(self):
        assert self.opt.optNombre == "Juan"
        assert self.opt.optApellido == "Perez"

    def test_str_representation(self):
        assert str(self.opt) == "Juan Perez"


class TestRecipeModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Client, Optometrist, Recipe
        cls.cliente = Client.objects.create(cliNomCompleto="Recipe Client")
        cls.optometrist = Optometrist.objects.create(optNombre="Dr", optApellido="Luna")
        cls.recipe = Recipe.objects.create(
            cliCod=cls.cliente, optCod=cls.optometrist,
            receDIP=60, receAdd=Decimal("1.50"),
            receEsfeOD=Decimal("-1.00"), receCilinOD=Decimal("-0.50"), receEjeOD=90,
            recObservaciones="Test recipe",
        )

    def test_create_recipe(self):
        assert self.recipe.cliCod == self.cliente
        assert self.recipe.optCod == self.optometrist
        assert self.recipe.receDIP == 60

    def test_str_representation(self):
        assert str(self.recipe) == f"Recipe {self.recipe.recCod}"

    def test_auto_fecha(self):
        from django.utils import timezone
        assert self.recipe.recFech is not None
        assert self.recipe.recFech <= timezone.now().date()

    def test_default_estado(self):
        assert self.recipe.recEstado == "Activo"

    def test_optional_fields_null(self):
        from clients.models import Recipe
        r = Recipe.objects.create(cliCod=self.cliente, optCod=self.optometrist)
        assert r.receEsfeOI is None
        assert r.receCilinOI is None
        assert r.receEjeOI is None
        assert r.diagnostico == []

    def test_rece_es_externa_default(self):
        assert self.recipe.receEsExterna is False

    def test_float_decimal_fields(self):
        assert float(self.recipe.receAdd) == 1.50
        assert float(self.recipe.receEsfeOD) == -1.00


class TestClientSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Client
        cls.cliente = Client.objects.create(
            cliTipoDoc="DNI", cliNumDoc="87654321",
            cliNomCompleto="serial test",
        )

    def test_serialize_fields(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(self.cliente)
        assert s.data["cliCod"] == self.cliente.cliCod
        assert s.data["cliNomCompleto"] == "SERIAL TEST"
        assert s.data["cliNumDoc"] == "87654321"
        assert s.data["cliTipoDoc"] == "DNI"

    def test_serialize_read_only_cod(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={"cliNomCompleto": "X"})
        assert s.is_valid()
        assert "cliCod" not in s.validated_data

    def test_deserialize_valid_minimal(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={"cliNomCompleto": "Nuevo"})
        assert s.is_valid()
        client = s.save()
        assert client.cliNomCompleto == "NUEVO"

    def test_deserialize_valid_all_fields(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={
            "cliTipoDoc": "RUC", "cliNumDoc": "20123456789",
            "cliNomCompleto": "Empresa SAC", "cliTelef": "999000111",
            "cliFechaNac": "1985-03-20",
        })
        assert s.is_valid()
        client = s.save()
        assert client.cliTipoDoc == "RUC"
        assert client.cliNomCompleto == "EMPRESA SAC"
        assert client.cliTelef == "999000111"

    def test_deserialize_invalid_no_name(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={})
        assert not s.is_valid()
        assert "cliNomCompleto" in s.errors

    def test_deserialize_invalid_empty_name(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={"cliNomCompleto": ""})
        assert not s.is_valid()

    def test_deserialize_without_optional_fields(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={"cliNomCompleto": "Solo Nombre"})
        assert s.is_valid()
        client = s.save()
        assert client.cliTelef is None or client.cliTelef == ""

    def test_deserialize_with_ce_document(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={
            "cliTipoDoc": "CE", "cliNumDoc": "A12345678",
            "cliNomCompleto": "Extranjero",
        })
        assert s.is_valid()
        client = s.save()
        assert client.cliNumDoc == "A12345678"

    def test_deserialize_fecha_nac_null(self):
        from clients.serializers import ClientSerializer
        s = ClientSerializer(data={
            "cliNomCompleto": "Sin Fecha",
            "cliFechaNac": None,
        })
        assert s.is_valid()


class TestOptometristSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Optometrist
        cls.opt = Optometrist.objects.create(optNombre="Ana", optApellido="Martinez")

    def test_serialize_fields(self):
        from clients.serializers import OptometristSerializer
        s = OptometristSerializer(self.opt)
        assert s.data["optCod"] == self.opt.optCod
        assert s.data["optNombre"] == "Ana"
        assert s.data["optApellido"] == "Martinez"

    def test_deserialize_valid(self):
        from clients.serializers import OptometristSerializer
        s = OptometristSerializer(data={"optNombre": "Carlos", "optApellido": "Lopez"})
        assert s.is_valid()
        obj = s.save()
        assert obj.optNombre == "Carlos"
        assert obj.optApellido == "Lopez"

    def test_deserialize_invalid_no_nombre(self):
        from clients.serializers import OptometristSerializer
        s = OptometristSerializer(data={"optApellido": "Solo Apellido"})
        assert not s.is_valid()

    def test_deserialize_invalid_no_apellido(self):
        from clients.serializers import OptometristSerializer
        s = OptometristSerializer(data={"optNombre": "Solo Nombre"})
        assert not s.is_valid()


class TestRecipeSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Client, Optometrist
        cls.cliente = Client.objects.create(cliNomCompleto="Recipe Ser")
        cls.optometrist = Optometrist.objects.create(optNombre="Dr", optApellido="Vis")

    def test_serialize_fields(self):
        from clients.models import Recipe
        from clients.serializers import RecipeSerializer
        r = Recipe.objects.create(cliCod=self.cliente, optCod=self.optometrist)
        s = RecipeSerializer(r)
        assert s.data["cliCod"] == self.cliente.cliCod
        assert s.data["optCod"] == self.optometrist.optCod
        assert s.data["recEstado"] == "Activo"

    def test_deserialize_valid_minimal(self):
        from clients.serializers import RecipeSerializer
        s = RecipeSerializer(data={
            "cliCod": self.cliente.cliCod,
            "optCod": self.optometrist.optCod,
        })
        assert s.is_valid()
        r = s.save()
        assert r.recEstado == "Activo"
        assert r.cliCod == self.cliente
        assert r.optCod == self.optometrist

    def test_deserialize_invalid_no_cliente(self):
        from clients.serializers import RecipeSerializer
        s = RecipeSerializer(data={"optCod": self.optometrist.optCod})
        assert not s.is_valid()

    def test_deserialize_invalid_no_optometrist(self):
        from clients.serializers import RecipeSerializer
        s = RecipeSerializer(data={"cliCod": self.cliente.cliCod})
        assert not s.is_valid()

    def test_deserialize_with_all_fields(self):
        from clients.serializers import RecipeSerializer
        s = RecipeSerializer(data={
            "cliCod": self.cliente.cliCod,
            "optCod": self.optometrist.optCod,
            "receDIP": 65, "receDIPCerca": 62, "receAdd": "2.00",
            "receEsfeOD": "-1.50", "receCilinOD": "-0.75", "receEjeOD": 180,
            "receAvccOD": 20, "receEsfeOI": "-1.25", "receCilinOI": "-0.50",
            "receEjeOI": 170, "receAvccOI": 20, "receEsExterna": True,
            "recObservaciones": "Test completo",
            "diagnostico": ["MIOPIA", "ASTIGMATISMO"],
        })
        assert s.is_valid(), s.errors
        r = s.save()
        assert r.receDIP == 65
        assert r.receDIPCerca == 62
        assert float(r.receAdd) == 2.00
        assert r.diagnostico == ["MIOPIA", "ASTIGMATISMO"]
        assert r.recEstado == "Activo"

    def test_deserialize_with_optional_fields_null(self):
        from clients.serializers import RecipeSerializer
        s = RecipeSerializer(data={
            "cliCod": self.cliente.cliCod,
            "optCod": self.optometrist.optCod,
            "receDIP": None, "receAdd": None,
        })
        assert s.is_valid()
        r = s.save()
        assert r.receDIP is None


class TestClientFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        from clients.models import Client
        from datetime import date
        cls.joven = Client.objects.create(
            cliNomCompleto="Joven", cliTipoDoc="DNI", cliNumDoc="10000001",
            cliFechaNac=date(2000, 6, 15),
        )
        cls.adulto = Client.objects.create(
            cliNomCompleto="Adulto", cliTipoDoc="DNI", cliNumDoc="10000002",
            cliFechaNac=date(1990, 3, 10),
        )
        cls.mayor = Client.objects.create(
            cliNomCompleto="Mayor", cliTipoDoc="RUC", cliNumDoc="20000000001",
            cliFechaNac=date(1980, 1, 1),
        )
        cls.sin_fecha = Client.objects.create(
            cliNomCompleto="Sin Fecha", cliTipoDoc="CE", cliNumDoc="10000003",
            cliFechaNac=None,
        )

    def test_filter_by_tipo_doc_ruc(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"cliTipoDoc": "RUC"}, queryset=Client.objects.all())
        assert f.is_valid()
        assert list(f.qs) == [self.mayor]

    def test_filter_by_tipo_doc_dni(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"cliTipoDoc": "DNI"}, queryset=Client.objects.all())
        assert f.is_valid()
        assert len(f.qs) == 2
        assert self.joven in f.qs
        assert self.adulto in f.qs

    def test_filter_by_tipo_doc_ce(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"cliTipoDoc": "CE"}, queryset=Client.objects.all())
        assert f.is_valid()
        assert list(f.qs) == [self.sin_fecha]

    def test_filter_edad_min_includes_older(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_min": 30}, queryset=Client.objects.all())
        assert f.is_valid()
        for c in f.qs:
            if c.cliFechaNac:
                edad = int((date.today() - c.cliFechaNac).days / 365.25)
                assert edad >= 30

    def test_filter_edad_max_includes_younger(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_max": 30}, queryset=Client.objects.all())
        assert f.is_valid()
        for c in f.qs:
            if c.cliFechaNac:
                edad = int((date.today() - c.cliFechaNac).days / 365.25)
                assert edad <= 30

    def test_filter_edad_min_excludes_younger(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_min": 40}, queryset=Client.objects.all())
        assert f.is_valid()
        for c in f.qs:
            if c.cliFechaNac:
                edad = int((date.today() - c.cliFechaNac).days / 365.25)
                assert edad >= 40

    def test_filter_edad_min_without_fecha_excluded(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_min": 1}, queryset=Client.objects.all())
        assert f.is_valid()
        assert self.sin_fecha not in f.qs

    def test_filter_edad_max_without_fecha_excluded(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_max": 100}, queryset=Client.objects.all())
        assert f.is_valid()
        assert self.sin_fecha not in f.qs

    def test_filter_edad_min_invalid_returns_all(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_min": "abc"}, queryset=Client.objects.all())
        assert f.qs.count() == 4

    def test_filter_edad_max_empty(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_max": ""}, queryset=Client.objects.all())
        assert f.qs.count() == 4

    def test_filter_edad_min_very_high_returns_none(self):
        from clients.filters import ClientFilter
        from clients.models import Client
        f = ClientFilter(data={"edad_min": 200}, queryset=Client.objects.all())
        assert f.is_valid()
        assert f.qs.count() == 0


class TestClientUrls(TestCase):
    def test_client_list_url(self):
        match = resolve("/api/clients/client/")
        assert match.url_name == "Client-list"

    def test_client_detail_url(self):
        match = resolve("/api/clients/client/1/")
        assert match.url_name == "Client-detail"

    def test_optometrist_list_url(self):
        match = resolve("/api/clients/optometrist/")
        assert match.url_name == "Optometrist-list"

    def test_optometrist_detail_url(self):
        match = resolve("/api/clients/optometrist/1/")
        assert match.url_name == "Optometrist-detail"

    def test_recipe_list_url(self):
        match = resolve("/api/clients/prescription/")
        assert match.url_name == "Prescription-list"

    def test_recipe_detail_url(self):
        match = resolve("/api/clients/prescription/1/")
        assert match.url_name == "Prescription-detail"

    def test_buscar_url(self):
        match = resolve("/api/clients/buscar/")
        assert match.url_name == "buscar-cliente"

    def test_client_list_reverse(self):
        assert reverse("Client-list") == "/api/clients/client/"

    def test_client_detail_reverse(self):
        assert reverse("Client-detail", args=[1]) == "/api/clients/client/1/"

    def test_optometrist_list_reverse(self):
        assert reverse("Optometrist-list") == "/api/clients/optometrist/"

    def test_optometrist_detail_reverse(self):
        assert reverse("Optometrist-detail", args=[1]) == "/api/clients/optometrist/1/"

    def test_recipe_list_reverse(self):
        assert reverse("Prescription-list") == "/api/clients/prescription/"

    def test_recipe_detail_reverse(self):
        assert reverse("Prescription-detail", args=[1]) == "/api/clients/prescription/1/"

    def test_buscar_reverse(self):
        assert reverse("buscar-cliente") == "/api/clients/buscar/"


class TestClientViewSet(TestCase):
    @classmethod
    def setUpTestData(cls):
        from users.models import User
        from clients.models import Client
        cls.usuario = User.objects.create(
            usuNom="clientview", usuEmail="cv@test.com",
            usuNombreCom="Client View User", password="pass",
        )
        cls.cliente1 = Client.objects.create(
            cliTipoDoc="DNI", cliNumDoc="11111111",
            cliNomCompleto="Alpha Cliente",
        )
        cls.cliente2 = Client.objects.create(
            cliTipoDoc="RUC", cliNumDoc="22222222222",
            cliNomCompleto="Beta Empresa",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.__class__.usuario)

    def test_list_authenticated(self):
        resp = self.api.get("/api/clients/client/")
        assert resp.status_code == 200
        assert "results" in resp.data

    def test_list_unauthenticated(self):
        api = APIClient()
        resp = api.get("/api/clients/client/")
        assert resp.status_code == 401

    def test_create_valid(self):
        resp = self.api.post("/api/clients/client/", {"cliNomCompleto": "Nuevo Cliente"}, format="json")
        assert resp.status_code == 201
        assert resp.data["success"] is True
        assert resp.data["data"]["cliNomCompleto"] == "NUEVO CLIENTE"

    def test_create_invalid_no_data(self):
        resp = self.api.post("/api/clients/client/", {}, format="json")
        assert resp.status_code == 400
        assert resp.data["success"] is False

    def test_create_with_all_fields(self):
        resp = self.api.post("/api/clients/client/", {
            "cliTipoDoc": "CE", "cliNumDoc": "A12345678",
            "cliNomCompleto": "Extranjero Test",
            "cliTelef": "999000111",
            "cliFechaNac": "1988-12-25",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["data"]["cliNomCompleto"] == "EXTRANJERO TEST"
        assert resp.data["data"]["cliNumDoc"] == "A12345678"

    def test_retrieve(self):
        resp = self.api.get(f"/api/clients/client/{self.cliente1.cliCod}/")
        assert resp.status_code == 200

    def test_update_full(self):
        resp = self.api.put(f"/api/clients/client/{self.cliente1.cliCod}/",
            {"cliNomCompleto": "Actualizado Total"}, format="json")
        assert resp.status_code == 200
        assert resp.data["success"] is True
        assert resp.data["data"]["cliNomCompleto"] == "ACTUALIZADO TOTAL"

    def test_update_partial(self):
        resp = self.api.patch(f"/api/clients/client/{self.cliente1.cliCod}/",
            {"cliTelef": "999888777"}, format="json")
        assert resp.status_code == 200
        assert resp.data["data"]["cliTelef"] == "999888777"

    def test_update_invalid(self):
        resp = self.api.put(f"/api/clients/client/{self.cliente1.cliCod}/",
            {"cliNomCompleto": ""}, format="json")
        assert resp.status_code == 400
        assert resp.data["success"] is False

    def test_destroy(self):
        from clients.models import Client
        temp = Client.objects.create(cliNomCompleto="Temp Delete")
        resp = self.api.delete(f"/api/clients/client/{temp.cliCod}/")
        assert resp.status_code == 204
        assert not Client.objects.filter(pk=temp.pk).exists()

    def test_search_by_nombre(self):
        resp = self.api.get("/api/clients/client/?search=Alpha")
        assert resp.status_code == 200
        results = resp.data.get("results", [])
        nombres = [r["cliNomCompleto"] for r in results]
        assert any("ALPHA" in n for n in nombres)

    def test_search_by_documento(self):
        resp = self.api.get("/api/clients/client/?search=11111111")
        assert resp.status_code == 200
        results = resp.data.get("results", [])
        assert any("11111111" in r.get("cliNumDoc", "") for r in results)

    def test_search_no_match(self):
        resp = self.api.get("/api/clients/client/?search=ZZZZNOTEXIST")
        assert resp.status_code == 200
        results = resp.data.get("results", [])
        assert len(results) == 0


class TestOptometristViewSet(TestCase):
    @classmethod
    def setUpTestData(cls):
        from users.models import User
        from clients.models import Optometrist
        cls.usuario = User.objects.create(
            usuNom="optoview", usuEmail="opt@test.com",
            usuNombreCom="Opto View User", password="pass",
        )
        cls.opt1 = Optometrist.objects.create(optNombre="Juan", optApellido="Perez")
        cls.opt2 = Optometrist.objects.create(optNombre="Maria", optApellido="Lopez")

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.__class__.usuario)

    def test_list_authenticated(self):
        resp = self.api.get("/api/clients/optometrist/")
        assert resp.status_code == 200

    def test_list_unauthenticated(self):
        api = APIClient()
        resp = api.get("/api/clients/optometrist/")
        assert resp.status_code == 401

    def test_create_valid(self):
        resp = self.api.post("/api/clients/optometrist/",
            {"optNombre": "Carlos", "optApellido": "Ruiz"}, format="json")
        assert resp.status_code == 201
        assert resp.data["success"] is True
        assert resp.data["data"]["optNombre"] == "Carlos"

    def test_create_invalid_no_data(self):
        resp = self.api.post("/api/clients/optometrist/", {}, format="json")
        assert resp.status_code == 400
        assert resp.data["success"] is False

    def test_retrieve(self):
        resp = self.api.get(f"/api/clients/optometrist/{self.opt1.optCod}/")
        assert resp.status_code == 200

    def test_update_full(self):
        resp = self.api.put(f"/api/clients/optometrist/{self.opt1.optCod}/",
            {"optNombre": "Juan Carlos", "optApellido": "Perez"}, format="json")
        assert resp.status_code == 200
        assert resp.data["success"] is True
        assert resp.data["data"]["optNombre"] == "Juan Carlos"

    def test_update_partial(self):
        resp = self.api.patch(f"/api/clients/optometrist/{self.opt1.optCod}/",
            {"optNombre": "Juanito"}, format="json")
        assert resp.status_code == 200
        assert resp.data["data"]["optNombre"] == "Juanito"

    def test_update_invalid(self):
        resp = self.api.put(f"/api/clients/optometrist/{self.opt1.optCod}/",
            {"optNombre": ""}, format="json")
        assert resp.status_code == 400

    def test_destroy(self):
        from clients.models import Optometrist
        temp = Optometrist.objects.create(optNombre="Temp", optApellido="Del")
        resp = self.api.delete(f"/api/clients/optometrist/{temp.optCod}/")
        assert resp.status_code == 204
        assert not Optometrist.objects.filter(pk=temp.pk).exists()


class TestRecipeViewSet(TestCase):
    @classmethod
    def setUpTestData(cls):
        from users.models import User
        from clients.models import Client, Optometrist, Recipe
        cls.usuario = User.objects.create(
            usuNom="recipeview", usuEmail="rec@test.com",
            usuNombreCom="Recipe View User", password="pass",
        )
        cls.cliente = Client.objects.create(cliNomCompleto="Paciente Recipe")
        cls.optometrist = Optometrist.objects.create(optNombre="Doc", optApellido="Recipe")
        cls.recipe = Recipe.objects.create(
            cliCod=cls.cliente, optCod=cls.optometrist,
            receDIP=60,
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.__class__.usuario)

    def test_list_authenticated(self):
        resp = self.api.get("/api/clients/prescription/")
        assert resp.status_code == 200

    def test_list_unauthenticated(self):
        api = APIClient()
        resp = api.get("/api/clients/prescription/")
        assert resp.status_code == 401

    def test_create_valid_minimal(self):
        resp = self.api.post("/api/clients/prescription/", {
            "cliCod": self.cliente.cliCod, "optCod": self.optometrist.optCod,
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["success"] is True

    def test_create_invalid_no_cliente(self):
        resp = self.api.post("/api/clients/prescription/", {
            "optCod": self.optometrist.optCod,
        }, format="json")
        assert resp.status_code == 400
        assert resp.data["success"] is False

    def test_create_invalid_no_optometrist(self):
        resp = self.api.post("/api/clients/prescription/", {
            "cliCod": self.cliente.cliCod,
        }, format="json")
        assert resp.status_code == 400
        assert resp.data["success"] is False

    def test_retrieve(self):
        resp = self.api.get(f"/api/clients/prescription/{self.recipe.recCod}/")
        assert resp.status_code == 200

    def test_update_full(self):
        resp = self.api.put(f"/api/clients/prescription/{self.recipe.recCod}/", {
            "cliCod": self.cliente.cliCod, "optCod": self.optometrist.optCod,
            "receDIP": 65, "receAdd": "1.50",
        }, format="json")
        assert resp.status_code == 200
        assert resp.data["success"] is True
        assert resp.data["data"]["receDIP"] == 65

    def test_update_partial(self):
        resp = self.api.patch(f"/api/clients/prescription/{self.recipe.recCod}/",
            {"recObservaciones": "Actualizado parcial"}, format="json")
        assert resp.status_code == 200
        assert resp.data["data"]["recObservaciones"] == "Actualizado parcial"

    def test_update_invalid(self):
        resp = self.api.put(f"/api/clients/prescription/{self.recipe.recCod}/", {
            "cliCod": None, "optCod": None,
        }, format="json")
        assert resp.status_code == 400

    def test_destroy(self):
        from clients.models import Recipe
        temp = Recipe.objects.create(
            cliCod=self.cliente, optCod=self.optometrist
        )
        resp = self.api.delete(f"/api/clients/prescription/{temp.recCod}/")
        assert resp.status_code == 204
        assert not Recipe.objects.filter(pk=temp.pk).exists()

    def test_filter_by_cliente(self):
        resp = self.api.get(f"/api/clients/prescription/?cliCod={self.cliente.cliCod}")
        assert resp.status_code == 200

    def test_filter_by_cliente_no_match(self):
        resp = self.api.get("/api/clients/prescription/?cliCod=99999")
        assert resp.status_code == 200


class TestBuscarCliente(TestCase):
    @classmethod
    def setUpTestData(cls):
        from users.models import User
        from clients.models import Client
        cls.usuario = User.objects.create(
            usuNom="buscaruser", usuEmail="bu@test.com",
            usuNombreCom="Buscar User", password="pass",
        )
        cls.cliente = Client.objects.create(
            cliTipoDoc="DNI", cliNumDoc="99999999",
            cliNomCompleto="Encontrado",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.__class__.usuario)

    def test_buscar_encontrado(self):
        resp = self.api.get("/api/clients/buscar/", {"tipo": "DNI", "numero": "99999999"})
        assert resp.status_code == 200
        assert resp.data["encontrado"] is True
        assert resp.data["cliente"]["cliNomCompleto"] == "ENCONTRADO"

    def test_buscar_no_encontrado(self):
        resp = self.api.get("/api/clients/buscar/", {"tipo": "DNI", "numero": "00000000"})
        assert resp.status_code == 200
        assert resp.data["encontrado"] is False
        assert "mensaje" in resp.data

    def test_buscar_sin_numero(self):
        resp = self.api.get("/api/clients/buscar/")
        assert resp.status_code == 400
        assert "error" in resp.data

    def test_buscar_unauthenticated(self):
        api = APIClient()
        resp = api.get("/api/clients/buscar/", {"tipo": "DNI", "numero": "99999999"})
        assert resp.status_code == 401
