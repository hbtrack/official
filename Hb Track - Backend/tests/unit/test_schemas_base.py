"""
Testes unitários para base schemas (FASE 3)
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from app.schemas.base import (
    TimestampMixin,
    SoftDeleteMixin,
    BaseSchema,
    BaseResponseSchema,
    BaseResponseWithSoftDelete,
    PaginatedResponse
)
from pydantic import BaseModel


# === Fixtures para testes ===

class TestModelWithTimestamp(TimestampMixin):
    """Modelo de teste com timestamps"""
    name: str


class TestModelWithSoftDelete(SoftDeleteMixin):
    """Modelo de teste com soft delete"""
    name: str


class TestResponseModel(BaseResponseSchema):
    """Modelo de teste para resposta"""
    name: str


class TestResponseModelWithSoftDelete(BaseResponseWithSoftDelete):
    """Modelo de teste para resposta com soft delete"""
    name: str


class PersonOut(BaseModel):
    """Modelo de teste para paginação"""
    id: UUID
    full_name: str


# === Testes TimestampMixin ===

def test_timestamp_mixin_required_fields():
    """Valida que TimestampMixin requer created_at e updated_at"""
    now = datetime.utcnow()

    model = TestModelWithTimestamp(
        name="Test",
        created_at=now,
        updated_at=now
    )

    assert model.created_at == now
    assert model.updated_at == now
    assert model.name == "Test"


def test_timestamp_mixin_from_orm():
    """Valida que TimestampMixin pode ser criado a partir de ORM"""
    class FakeORMModel:
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        name = "Test ORM"

    model = TestModelWithTimestamp.model_validate(FakeORMModel())

    assert model.created_at == FakeORMModel.created_at
    assert model.updated_at == FakeORMModel.updated_at
    assert model.name == "Test ORM"


# === Testes SoftDeleteMixin ===

def test_soft_delete_mixin_optional_fields():
    """Valida que SoftDeleteMixin tem campos opcionais"""
    model = TestModelWithSoftDelete(name="Test")

    assert model.deleted_at is None
    assert model.deleted_reason is None


def test_soft_delete_mixin_with_deletion():
    """Valida SoftDeleteMixin com dados de exclusão (RDB4)"""
    deleted_time = datetime.utcnow()

    model = TestModelWithSoftDelete(
        name="Test",
        deleted_at=deleted_time,
        deleted_reason="Motivo de teste"
    )

    assert model.deleted_at == deleted_time
    assert model.deleted_reason == "Motivo de teste"


# === Testes BaseSchema ===

def test_base_schema_config():
    """Valida configuração do BaseSchema"""
    model = BaseSchema()

    # Verifica que from_attributes está habilitado
    assert model.model_config["from_attributes"] is True
    assert model.model_config["populate_by_name"] is True
    assert model.model_config["str_strip_whitespace"] is True


# === Testes BaseResponseSchema ===

def test_base_response_schema_required_fields():
    """Valida que BaseResponseSchema requer id e timestamps"""
    resource_id = uuid4()
    now = datetime.utcnow()

    model = TestResponseModel(
        id=resource_id,
        name="Test",
        created_at=now,
        updated_at=now
    )

    assert model.id == resource_id
    assert isinstance(model.id, UUID)
    assert model.created_at == now
    assert model.updated_at == now


def test_base_response_schema_inherits_from_base():
    """Valida que BaseResponseSchema herda de BaseSchema"""
    model = TestResponseModel(
        id=uuid4(),
        name="Test",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Deve ter a configuração do BaseSchema
    assert model.model_config["from_attributes"] is True


# === Testes BaseResponseWithSoftDelete ===

def test_base_response_with_soft_delete():
    """Valida BaseResponseWithSoftDelete com todos os campos"""
    resource_id = uuid4()
    now = datetime.utcnow()

    model = TestResponseModelWithSoftDelete(
        id=resource_id,
        name="Test",
        created_at=now,
        updated_at=now,
        deleted_at=None,
        deleted_reason=None
    )

    assert model.id == resource_id
    assert model.created_at == now
    assert model.updated_at == now
    assert model.deleted_at is None
    assert model.deleted_reason is None


def test_base_response_with_soft_delete_deleted():
    """Valida BaseResponseWithSoftDelete com registro deletado"""
    resource_id = uuid4()
    now = datetime.utcnow()
    deleted_time = datetime.utcnow()

    model = TestResponseModelWithSoftDelete(
        id=resource_id,
        name="Test",
        created_at=now,
        updated_at=now,
        deleted_at=deleted_time,
        deleted_reason="Teste de exclusão"
    )

    assert model.deleted_at == deleted_time
    assert model.deleted_reason == "Teste de exclusão"


# === Testes PaginatedResponse ===

def test_paginated_response_basic():
    """Valida PaginatedResponse básico"""
    persons = [
        PersonOut(id=uuid4(), full_name="Person 1"),
        PersonOut(id=uuid4(), full_name="Person 2"),
    ]

    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )

    assert len(response.items) == 2
    assert response.total == 100
    assert response.skip == 0
    assert response.limit == 10


def test_paginated_response_has_next():
    """Valida propriedade has_next"""
    persons = [PersonOut(id=uuid4(), full_name="Person 1")]

    # Primeira página (tem próxima)
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )
    assert response.has_next is True

    # Última página (não tem próxima)
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=90,
        limit=10
    )
    assert response.has_next is False


def test_paginated_response_has_previous():
    """Valida propriedade has_previous"""
    persons = [PersonOut(id=uuid4(), full_name="Person 1")]

    # Primeira página (não tem anterior)
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )
    assert response.has_previous is False

    # Segunda página (tem anterior)
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=10,
        limit=10
    )
    assert response.has_previous is True


def test_paginated_response_page_count():
    """Valida cálculo de page_count"""
    persons = [PersonOut(id=uuid4(), full_name="Person 1")]

    # 100 itens, 10 por página = 10 páginas
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )
    assert response.page_count == 10

    # 105 itens, 10 por página = 11 páginas (arredonda para cima)
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=105,
        skip=0,
        limit=10
    )
    assert response.page_count == 11


def test_paginated_response_current_page():
    """Valida cálculo de current_page (1-indexed)"""
    persons = [PersonOut(id=uuid4(), full_name="Person 1")]

    # Primeira página
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )
    assert response.current_page == 1

    # Segunda página
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=10,
        limit=10
    )
    assert response.current_page == 2

    # Terceira página
    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=20,
        limit=10
    )
    assert response.current_page == 3


def test_paginated_response_empty():
    """Valida PaginatedResponse vazio"""
    response = PaginatedResponse[PersonOut](
        items=[],
        total=0,
        skip=0,
        limit=10
    )

    assert len(response.items) == 0
    assert response.total == 0
    assert response.has_next is False
    assert response.has_previous is False
    assert response.page_count == 0
    assert response.current_page == 1


def test_paginated_response_json_serialization():
    """Valida serialização JSON de PaginatedResponse"""
    persons = [
        PersonOut(id=uuid4(), full_name="Person 1"),
        PersonOut(id=uuid4(), full_name="Person 2"),
    ]

    response = PaginatedResponse[PersonOut](
        items=persons,
        total=100,
        skip=0,
        limit=10
    )

    json_data = response.model_dump(mode='json')

    assert "items" in json_data
    assert "total" in json_data
    assert "skip" in json_data
    assert "limit" in json_data
    assert len(json_data["items"]) == 2
    assert json_data["total"] == 100
