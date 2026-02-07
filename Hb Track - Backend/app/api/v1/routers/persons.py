"""
Router: Persons (R1) - V1.2 Normalizado

Referências RAG:
- R1: Pessoa é entidade raiz
- R26: Permissões por papel (coordenador, dirigente)
- RDB4: Soft delete com deleted_reason obrigatório

V1.2: Endpoints para estrutura normalizada:
- /persons (CRUD de Person)
- /persons/{id}/contacts (CRUD de PersonContact)
- /persons/{id}/addresses (CRUD de PersonAddress)
- /persons/{id}/documents (CRUD de PersonDocument)
- /persons/{id}/media (CRUD de PersonMedia)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import List, Optional

from app.core.db import get_async_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import get_current_context, require_role
from app.services.person_service import (
    PersonService,
    PersonContactService,
    PersonAddressService,
    PersonDocumentService,
    PersonMediaService
)
from app.schemas.person import (
    # Person
    PersonCreate,
    PersonUpdate,
    PersonResponse,
    PersonListResponse,
    PersonSoftDelete,
    # Contact
    PersonContactCreate,
    PersonContactUpdate,
    PersonContactResponse,
    PersonContactSoftDelete,
    # Address
    PersonAddressCreate,
    PersonAddressUpdate,
    PersonAddressResponse,
    PersonAddressSoftDelete,
    # Document
    PersonDocumentCreate,
    PersonDocumentUpdate,
    PersonDocumentResponse,
    PersonDocumentSoftDelete,
    # Media
    PersonMediaCreate,
    PersonMediaUpdate,
    PersonMediaResponse,
    PersonMediaSoftDelete,
)
from app.schemas.base import PaginatedResponse
from app.models.person import Person

router = APIRouter(tags=["Persons"])


# =====================================================
# PERSON ENDPOINTS
# =====================================================

@router.get("", response_model=PaginatedResponse[PersonListResponse])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    gender: Optional[str] = None,
    category_id: Optional[int] = None,
    team_category_id: Optional[int] = Query(None, description="Filtrar atletas da mesma categoria ou inferior"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Lista todas as pessoas (V1.2) com filtros

    Permissões: coordenador, dirigente (R26)
    
    Filtros:
    - search: busca por nome (case-insensitive)
    - gender: filtro por gênero (masculino, feminino)
    - category_id: filtro por categoria (1-7)
    - team_category_id: filtra apenas atletas da mesma categoria ou inferior (para evitar cadastrar atletas mais velhos em categorias menores)

    Referências RAG:
    - R26: Coordenador e Dirigente têm acesso a dados operacionais
    - R29: Apenas pessoas não deletadas são listadas
    """
    from sqlalchemy import or_, and_
    from app.models.athlete import Athlete
    from app.models.category import Category
    
    # Base query
    query = select(Person).where(Person.deleted_at == None)
    
    # Aplicar filtro de busca
    if search:
        search_term = f"%{search}%"
        query = query.where(Person.full_name.ilike(search_term))
    
    # NOTA: Athlete NÃO tem category_id diretamente
    # A categoria vem via TeamRegistration (team_registrations.category_id)
    # Por enquanto, retornar todos os atletas sem filtro de categoria
    # TODO: Implementar filtro correto quando houver necessidade específica
    
    # Join com Athlete apenas para garantir que é atleta
    if team_category_id or category_id:
        query = query.join(Athlete, Athlete.person_id == Person.id)
    
    # Aplicar filtro de gênero (se existir campo gender na tabela Person)
    # TODO: Validar se campo existe, senão remover este filtro
    # if gender:
    #     query = query.where(Person.gender == gender)
    
    # Paginação
    result = await db.execute(query.offset(skip).limit(limit))
    persons = result.scalars().all()
    
    # Contar total
    count_query = select(func.count()).select_from(Person).where(Person.deleted_at == None)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(Person.full_name.ilike(search_term))
    
    # Join com Athlete apenas para garantir que é atleta no count
    if team_category_id or category_id:
        count_query = count_query.join(Athlete, Athlete.person_id == Person.id)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return PaginatedResponse(
        items=[PersonListResponse.model_validate(p) for p in persons],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Busca pessoa por ID com todos os dados relacionados (V1.2)

    Permissões: coordenador, dirigente (R26)

    Retorna:
    - Dados básicos da pessoa
    - Contatos (telefone, email, whatsapp)
    - Endereços (residencial_1, residencial_2)
    - Documentos (CPF, RG, CNH)
    - Mídias (foto_perfil, foto_documento)
    """
    person = await PersonService.get_by_id(db, person_id)
    return PersonResponse.model_validate(person)


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_data: PersonCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Cria nova pessoa com dados relacionados (V1.2)

    Permissões: coordenador, dirigente (R26)

    Permite criar pessoa com:
    - Contatos
    - Endereços
    - Documentos
    - Mídias

    Todos em uma única requisição.
    """
    person = await PersonService.create(db, person_data)
    await db.commit()
    await db.refresh(person)
    return PersonResponse.model_validate(person)


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: str,
    person_data: PersonUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Atualiza dados básicos da pessoa (V1.2)

    Permissões: coordenador, dirigente (R26)

    Nota: Para atualizar contatos, endereços, documentos ou mídias,
    use os endpoints específicos.
    """
    person = await PersonService.update(db, person_id, person_data)
    await db.commit()
    await db.refresh(person)
    return PersonResponse.model_validate(person)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: str,
    delete_data: PersonSoftDelete,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Soft delete de pessoa e todos os dados relacionados (V1.2)

    Permissões: coordenador, dirigente (R26)

    Referências RAG:
    - RDB4: deleted_reason obrigatório
    - R29: Exclusão lógica de pessoa + contatos + endereços + documentos + mídias
    """
    await PersonService.soft_delete(db, person_id, delete_data)
    await db.commit()
    return None


# =====================================================
# PERSON CONTACT ENDPOINTS
# =====================================================

@router.get("/{person_id}/contacts", response_model=List[PersonContactResponse])
async def list_person_contacts(
    person_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Lista todos os contatos de uma pessoa"""
    contacts = await PersonContactService.get_by_person(db, person_id)
    return [PersonContactResponse.model_validate(c) for c in contacts]


@router.get("/{person_id}/contacts/{contact_id}", response_model=PersonContactResponse)
async def get_person_contact(
    person_id: str,
    contact_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Busca contato por ID"""
    contact = await PersonContactService.get_by_id(db, person_id, contact_id)
    return PersonContactResponse.model_validate(contact)


@router.post("/{person_id}/contacts", response_model=PersonContactResponse, status_code=status.HTTP_201_CREATED)
async def create_person_contact(
    person_id: str,
    contact_data: PersonContactCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Cria novo contato para pessoa"""
    contact = await PersonContactService.create(db, person_id, contact_data)
    await db.commit()
    await db.refresh(contact)
    return PersonContactResponse.model_validate(contact)


@router.put("/{person_id}/contacts/{contact_id}", response_model=PersonContactResponse)
async def update_person_contact(
    person_id: str,
    contact_id: str,
    contact_data: PersonContactUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Atualiza contato"""
    contact = await PersonContactService.update(db, person_id, contact_id, contact_data)
    await db.commit()
    await db.refresh(contact)
    return PersonContactResponse.model_validate(contact)


@router.delete("/{person_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person_contact(
    person_id: str,
    contact_id: str,
    delete_data: PersonContactSoftDelete,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Soft delete de contato"""
    await PersonContactService.soft_delete(db, person_id, contact_id, delete_data)
    await db.commit()
    return None


# =====================================================
# PERSON ADDRESS ENDPOINTS
# =====================================================

@router.get("/{person_id}/addresses", response_model=List[PersonAddressResponse])
async def list_person_addresses(
    person_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Lista todos os endereços de uma pessoa"""
    addresses = await PersonAddressService.get_by_person(db, person_id)
    return [PersonAddressResponse.model_validate(a) for a in addresses]


@router.get("/{person_id}/addresses/{address_id}", response_model=PersonAddressResponse)
async def get_person_address(
    person_id: str,
    address_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Busca endereço por ID"""
    address = await PersonAddressService.get_by_id(db, person_id, address_id)
    return PersonAddressResponse.model_validate(address)


@router.post("/{person_id}/addresses", response_model=PersonAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_person_address(
    person_id: str,
    address_data: PersonAddressCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Cria novo endereço para pessoa"""
    address = await PersonAddressService.create(db, person_id, address_data)
    await db.commit()
    await db.refresh(address)
    return PersonAddressResponse.model_validate(address)


@router.put("/{person_id}/addresses/{address_id}", response_model=PersonAddressResponse)
async def update_person_address(
    person_id: str,
    address_id: str,
    address_data: PersonAddressUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Atualiza endereço"""
    address = await PersonAddressService.update(db, person_id, address_id, address_data)
    await db.commit()
    await db.refresh(address)
    return PersonAddressResponse.model_validate(address)


@router.delete("/{person_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person_address(
    person_id: str,
    address_id: str,
    delete_data: PersonAddressSoftDelete,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Soft delete de endereço"""
    await PersonAddressService.soft_delete(db, person_id, address_id, delete_data)
    await db.commit()
    return None


# =====================================================
# PERSON DOCUMENT ENDPOINTS
# =====================================================

@router.get("/{person_id}/documents", response_model=List[PersonDocumentResponse])
async def list_person_documents(
    person_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Lista todos os documentos de uma pessoa"""
    documents = await PersonDocumentService.get_by_person(db, person_id)
    return [PersonDocumentResponse.model_validate(d) for d in documents]


@router.get("/{person_id}/documents/{document_id}", response_model=PersonDocumentResponse)
async def get_person_document(
    person_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Busca documento por ID"""
    document = await PersonDocumentService.get_by_id(db, person_id, document_id)
    return PersonDocumentResponse.model_validate(document)


@router.post("/{person_id}/documents", response_model=PersonDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_person_document(
    person_id: str,
    document_data: PersonDocumentCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Cria novo documento para pessoa"""
    document = await PersonDocumentService.create(db, person_id, document_data)
    await db.commit()
    await db.refresh(document)
    return PersonDocumentResponse.model_validate(document)


@router.put("/{person_id}/documents/{document_id}", response_model=PersonDocumentResponse)
async def update_person_document(
    person_id: str,
    document_id: str,
    document_data: PersonDocumentUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Atualiza documento"""
    document = await PersonDocumentService.update(db, person_id, document_id, document_data)
    await db.commit()
    await db.refresh(document)
    return PersonDocumentResponse.model_validate(document)


@router.delete("/{person_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person_document(
    person_id: str,
    document_id: str,
    delete_data: PersonDocumentSoftDelete,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Soft delete de documento"""
    await PersonDocumentService.soft_delete(db, person_id, document_id, delete_data)
    await db.commit()
    return None


# =====================================================
# PERSON MEDIA ENDPOINTS
# =====================================================

@router.get("/{person_id}/media", response_model=List[PersonMediaResponse])
async def list_person_media(
    person_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Lista todas as mídias de uma pessoa"""
    media_list = await PersonMediaService.get_by_person(db, person_id)
    return [PersonMediaResponse.model_validate(m) for m in media_list]


@router.get("/{person_id}/media/{media_id}", response_model=PersonMediaResponse)
async def get_person_media(
    person_id: str,
    media_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Busca mídia por ID"""
    media = await PersonMediaService.get_by_id(db, person_id, media_id)
    return PersonMediaResponse.model_validate(media)


@router.post("/{person_id}/media", response_model=PersonMediaResponse, status_code=status.HTTP_201_CREATED)
async def create_person_media(
    person_id: str,
    media_data: PersonMediaCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Cria nova mídia para pessoa"""
    media = await PersonMediaService.create(db, person_id, media_data)
    await db.commit()
    await db.refresh(media)
    return PersonMediaResponse.model_validate(media)


@router.put("/{person_id}/media/{media_id}", response_model=PersonMediaResponse)
async def update_person_media(
    person_id: str,
    media_id: str,
    media_data: PersonMediaUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Atualiza mídia"""
    media = await PersonMediaService.update(db, person_id, media_id, media_data)
    await db.commit()
    await db.refresh(media)
    return PersonMediaResponse.model_validate(media)


@router.delete("/{person_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person_media(
    person_id: str,
    media_id: str,
    delete_data: PersonMediaSoftDelete,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """Soft delete de mídia"""
    await PersonMediaService.soft_delete(db, person_id, media_id, delete_data)
    await db.commit()
    return None
