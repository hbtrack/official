"""
Service: Person (R1) - V1.2 Normalizado

Camada de lógica de negócio

Referências RAG:
- R1: Pessoa é entidade raiz
- RDB4: Soft delete com deleted_reason obrigatório
- R29: Exclusão lógica (nenhuma entidade relevante é apagada fisicamente)

V1.2: Estrutura normalizada com serviços para:
- Person (identidade básica)
- PersonContact (telefone, email, whatsapp)
- PersonAddress (endereços)
- PersonDocument (CPF, RG, CNH)
- PersonMedia (fotos, arquivos)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timezone

from app.models.person import Person, PersonContact, PersonAddress, PersonDocument, PersonMedia
from app.schemas.person import (
    PersonCreate, PersonUpdate, PersonSoftDelete,
    PersonContactCreate, PersonContactUpdate, PersonContactSoftDelete,
    PersonAddressCreate, PersonAddressUpdate, PersonAddressSoftDelete,
    PersonDocumentCreate, PersonDocumentUpdate, PersonDocumentSoftDelete,
    PersonMediaCreate, PersonMediaUpdate, PersonMediaSoftDelete
)
from app.schemas.error import ErrorResponse, ErrorCode, ErrorDetail
from fastapi import HTTPException, status


class PersonService:
    """Service para operações de Person (V1.2)"""

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Person]:
        """
        Lista todas as pessoas (exceto deletadas) com relacionamentos

        Args:
            db: Sessão do banco
            skip: Offset de paginação
            limit: Limite de resultados

        Returns:
            Lista de Person com contacts, addresses, documents, media

        Referências RAG:
            - R29: Exclusão lógica (filtra deleted_at == None)
        """
        stmt = (
            select(Person)
            .options(
                selectinload(Person.contacts),
                selectinload(Person.addresses),
                selectinload(Person.documents),
                selectinload(Person.media)
            )
            .where(Person.deleted_at == None)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        """
        Conta todas as pessoas não deletadas

        Args:
            db: Sessão do banco

        Returns:
            Total de pessoas ativas
        """
        stmt = select(func.count()).select_from(Person).where(Person.deleted_at == None)
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_by_id(db: AsyncSession, person_id: str) -> Person:
        """
        Busca pessoa por ID com todos os relacionamentos

        Args:
            db: Sessão do banco
            person_id: UUID da pessoa (string)

        Returns:
            Person com contacts, addresses, documents, media

        Raises:
            HTTPException 404: Se pessoa não encontrada

        Referências RAG:
            - R29: Só retorna se não deletada
        """
        stmt = (
            select(Person)
            .options(
                selectinload(Person.contacts),
                selectinload(Person.addresses),
                selectinload(Person.documents),
                selectinload(Person.media)
            )
            .where(
                Person.id == person_id,
                Person.deleted_at == None
            )
        )
        result = await db.execute(stmt)
        person = result.scalar_one_or_none()

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Person {person_id} não encontrada",
                    request_id="",
                    details=ErrorDetail(field="person_id")
                ).model_dump()
            )

        return person

    @staticmethod
    async def create(db: AsyncSession, person_data: PersonCreate) -> Person:
        """
        Cria nova pessoa com dados relacionados (V1.2)

        Args:
            db: Sessão do banco
            person_data: Dados da pessoa (pode incluir contacts, addresses, documents, media)

        Returns:
            Person criada com relacionamentos

        Referências RAG:
            - R1: Pessoa é entidade raiz
        """
        # Extrair dados aninhados
        contacts_data = person_data.contacts or []
        addresses_data = person_data.addresses or []
        documents_data = person_data.documents or []
        media_data = person_data.media or []

        # Criar full_name a partir de first_name + last_name
        full_name = f"{person_data.first_name} {person_data.last_name}".strip()

        # Criar person (excluindo dados aninhados)
        person_dict = person_data.model_dump(exclude={'contacts', 'addresses', 'documents', 'media'})
        person_dict['full_name'] = full_name
        
        person = Person(**person_dict)
        db.add(person)
        await db.flush()  # Gerar ID antes de adicionar relacionamentos

        # Criar contacts
        for contact_data in contacts_data:
            contact = PersonContact(
                person_id=person.id,
                **contact_data.model_dump()
            )
            db.add(contact)

        # Criar addresses
        for address_data in addresses_data:
            address = PersonAddress(
                person_id=person.id,
                **address_data.model_dump()
            )
            db.add(address)

        # Criar documents
        for document_data in documents_data:
            # Validar CPF único
            if document_data.document_type == 'cpf':
                stmt = select(PersonDocument).where(
                    PersonDocument.document_type == 'cpf',
                    PersonDocument.document_number == document_data.document_number,
                    PersonDocument.deleted_at == None
                )
                result = await db.execute(stmt)
                existing_cpf = result.scalar_one_or_none()
                
                if existing_cpf:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=ErrorResponse(
                            error_code=ErrorCode.DUPLICATE_PERSON,
                            message=f"CPF {document_data.document_number} já cadastrado",
                            request_id="",
                            details=ErrorDetail(
                                field="cpf",
                                existing_id=str(existing_cpf.person_id)
                            )
                        ).model_dump()
                    )
            
            document = PersonDocument(
                person_id=person.id,
                **document_data.model_dump()
            )
            db.add(document)

        # Criar media
        for media_item_data in media_data:
            media_item = PersonMedia(
                person_id=person.id,
                **media_item_data.model_dump()
            )
            db.add(media_item)

        await db.flush()
        
        # Recarregar com relacionamentos
        await db.refresh(person)
        return person

    @staticmethod
    async def update(db: AsyncSession, person_id: str, person_data: PersonUpdate) -> Person:
        """
        Atualiza pessoa (apenas dados básicos)

        Args:
            db: Sessão do banco
            person_id: UUID da pessoa (string)
            person_data: Dados para atualizar

        Returns:
            Person atualizada

        Referências RAG:
            - R1: Atualização de dados da pessoa
        """
        person = await PersonService.get_by_id(db, person_id)

        # Atualizar apenas campos fornecidos
        update_data = person_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(person, field, value)

        # Atualizar full_name se first_name ou last_name mudaram
        if 'first_name' in update_data or 'last_name' in update_data:
            person.full_name = f"{person.first_name} {person.last_name}".strip()

        await db.flush()
        return person

    @staticmethod
    async def soft_delete(db: AsyncSession, person_id: str, delete_data: PersonSoftDelete) -> Person:
        """
        Soft delete de pessoa e todos os dados relacionados

        Args:
            db: Sessão do banco
            person_id: UUID da pessoa (string)
            delete_data: Motivo da exclusão

        Returns:
            Person deletada

        Referências RAG:
            - RDB4: deleted_reason obrigatório
            - R29: Exclusão lógica (nenhuma entidade é apagada fisicamente)
        """
        person = await PersonService.get_by_id(db, person_id)
        now = datetime.now(timezone.utc)

        # Soft delete da pessoa
        person.deleted_at = now
        person.deleted_reason = delete_data.deleted_reason

        # Soft delete de todos os relacionamentos
        for contact in person.contacts:
            if not contact.deleted_at:
                contact.deleted_at = now
                contact.deleted_reason = f"Pessoa deletada: {delete_data.deleted_reason}"

        for address in person.addresses:
            if not address.deleted_at:
                address.deleted_at = now
                address.deleted_reason = f"Pessoa deletada: {delete_data.deleted_reason}"

        for document in person.documents:
            if not document.deleted_at:
                document.deleted_at = now
                document.deleted_reason = f"Pessoa deletada: {delete_data.deleted_reason}"

        for media_item in person.media:
            if not media_item.deleted_at:
                media_item.deleted_at = now
                media_item.deleted_reason = f"Pessoa deletada: {delete_data.deleted_reason}"

        await db.flush()
        return person


# =====================================================
# PERSON CONTACT SERVICE
# =====================================================

class PersonContactService:
    """Service para operações de PersonContact"""

    @staticmethod
    async def get_by_person(db: AsyncSession, person_id: str) -> List[PersonContact]:
        """Lista todos os contatos de uma pessoa"""
        # Validar pessoa existe
        await PersonService.get_by_id(db, person_id)

        stmt = select(PersonContact).where(
            PersonContact.person_id == person_id,
            PersonContact.deleted_at == None
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, person_id: str, contact_id: str) -> PersonContact:
        """Busca contato por ID"""
        stmt = select(PersonContact).where(
            PersonContact.id == contact_id,
            PersonContact.person_id == person_id,
            PersonContact.deleted_at == None
        )
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Contato {contact_id} não encontrado",
                    request_id="",
                    details=ErrorDetail(field="contact_id")
                ).model_dump()
            )

        return contact

    @staticmethod
    async def create(db: AsyncSession, person_id: str, contact_data: PersonContactCreate) -> PersonContact:
        """Cria novo contato para pessoa"""
        # Validar pessoa existe
        await PersonService.get_by_id(db, person_id)

        # Se is_primary, remover primary dos outros do mesmo tipo
        if contact_data.is_primary:
            stmt = select(PersonContact).where(
                PersonContact.person_id == person_id,
                PersonContact.contact_type == contact_data.contact_type,
                PersonContact.is_primary == True,
                PersonContact.deleted_at == None
            )
            result = await db.execute(stmt)
            other_contacts = result.scalars().all()
            for c in other_contacts:
                c.is_primary = False

        contact = PersonContact(
            person_id=person_id,
            **contact_data.model_dump()
        )
        db.add(contact)
        await db.flush()
        return contact

    @staticmethod
    async def update(db: AsyncSession, person_id: str, contact_id: str, contact_data: PersonContactUpdate) -> PersonContact:
        """Atualiza contato"""
        contact = await PersonContactService.get_by_id(db, person_id, contact_id)

        # Se marcando como primary, remover primary dos outros do mesmo tipo
        if contact_data.is_primary:
            stmt = select(PersonContact).where(
                PersonContact.person_id == person_id,
                PersonContact.contact_type == contact.contact_type,
                PersonContact.id != contact_id,
                PersonContact.is_primary == True,
                PersonContact.deleted_at == None
            )
            result = await db.execute(stmt)
            other_contacts = result.scalars().all()
            for c in other_contacts:
                c.is_primary = False

        update_data = contact_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)

        await db.flush()
        return contact

    @staticmethod
    async def soft_delete(db: AsyncSession, person_id: str, contact_id: str, delete_data: PersonContactSoftDelete) -> PersonContact:
        """Soft delete de contato"""
        contact = await PersonContactService.get_by_id(db, person_id, contact_id)
        
        contact.deleted_at = datetime.now(timezone.utc)
        contact.deleted_reason = delete_data.deleted_reason
        
        await db.flush()
        return contact


# =====================================================
# PERSON ADDRESS SERVICE
# =====================================================

class PersonAddressService:
    """Service para operações de PersonAddress"""

    @staticmethod
    async def get_by_person(db: AsyncSession, person_id: str) -> List[PersonAddress]:
        """Lista todos os endereços de uma pessoa"""
        await PersonService.get_by_id(db, person_id)

        stmt = select(PersonAddress).where(
            PersonAddress.person_id == person_id,
            PersonAddress.deleted_at == None
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, person_id: str, address_id: str) -> PersonAddress:
        """Busca endereço por ID"""
        stmt = select(PersonAddress).where(
            PersonAddress.id == address_id,
            PersonAddress.person_id == person_id,
            PersonAddress.deleted_at == None
        )
        result = await db.execute(stmt)
        address = result.scalar_one_or_none()

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Endereço {address_id} não encontrado",
                    request_id="",
                    details=ErrorDetail(field="address_id")
                ).model_dump()
            )

        return address

    @staticmethod
    async def create(db: AsyncSession, person_id: str, address_data: PersonAddressCreate) -> PersonAddress:
        """Cria novo endereço para pessoa"""
        await PersonService.get_by_id(db, person_id)

        # Se is_primary, remover primary dos outros
        if address_data.is_primary:
            stmt = select(PersonAddress).where(
                PersonAddress.person_id == person_id,
                PersonAddress.is_primary == True,
                PersonAddress.deleted_at == None
            )
            result = await db.execute(stmt)
            other_addresses = result.scalars().all()
            for a in other_addresses:
                a.is_primary = False

        address = PersonAddress(
            person_id=person_id,
            **address_data.model_dump()
        )
        db.add(address)
        await db.flush()
        return address

    @staticmethod
    async def update(db: AsyncSession, person_id: str, address_id: str, address_data: PersonAddressUpdate) -> PersonAddress:
        """Atualiza endereço"""
        address = await PersonAddressService.get_by_id(db, person_id, address_id)

        if address_data.is_primary:
            stmt = select(PersonAddress).where(
                PersonAddress.person_id == person_id,
                PersonAddress.id != address_id,
                PersonAddress.is_primary == True,
                PersonAddress.deleted_at == None
            )
            result = await db.execute(stmt)
            other_addresses = result.scalars().all()
            for a in other_addresses:
                a.is_primary = False

        update_data = address_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)

        await db.flush()
        return address

    @staticmethod
    async def soft_delete(db: AsyncSession, person_id: str, address_id: str, delete_data: PersonAddressSoftDelete) -> PersonAddress:
        """Soft delete de endereço"""
        address = await PersonAddressService.get_by_id(db, person_id, address_id)
        
        address.deleted_at = datetime.now(timezone.utc)
        address.deleted_reason = delete_data.deleted_reason
        
        await db.flush()
        return address


# =====================================================
# PERSON DOCUMENT SERVICE
# =====================================================

class PersonDocumentService:
    """Service para operações de PersonDocument"""

    @staticmethod
    async def get_by_person(db: AsyncSession, person_id: str) -> List[PersonDocument]:
        """Lista todos os documentos de uma pessoa"""
        await PersonService.get_by_id(db, person_id)

        stmt = select(PersonDocument).where(
            PersonDocument.person_id == person_id,
            PersonDocument.deleted_at == None
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, person_id: str, document_id: str) -> PersonDocument:
        """Busca documento por ID"""
        stmt = select(PersonDocument).where(
            PersonDocument.id == document_id,
            PersonDocument.person_id == person_id,
            PersonDocument.deleted_at == None
        )
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Documento {document_id} não encontrado",
                    request_id="",
                    details=ErrorDetail(field="document_id")
                ).model_dump()
            )

        return document

    @staticmethod
    async def create(db: AsyncSession, person_id: str, document_data: PersonDocumentCreate) -> PersonDocument:
        """Cria novo documento para pessoa"""
        await PersonService.get_by_id(db, person_id)

        # Validar CPF único
        if document_data.document_type == 'cpf':
            stmt = select(PersonDocument).where(
                PersonDocument.document_type == 'cpf',
                PersonDocument.document_number == document_data.document_number,
                PersonDocument.deleted_at == None
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error_code=ErrorCode.DUPLICATE_PERSON,
                        message=f"CPF {document_data.document_number} já cadastrado",
                        request_id="",
                        details=ErrorDetail(
                            field="cpf",
                            existing_id=str(existing.person_id)
                        )
                    ).model_dump()
                )

        document = PersonDocument(
            person_id=person_id,
            **document_data.model_dump()
        )
        db.add(document)
        await db.flush()
        return document

    @staticmethod
    async def update(db: AsyncSession, person_id: str, document_id: str, document_data: PersonDocumentUpdate) -> PersonDocument:
        """Atualiza documento"""
        document = await PersonDocumentService.get_by_id(db, person_id, document_id)

        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        await db.flush()
        return document

    @staticmethod
    async def soft_delete(db: AsyncSession, person_id: str, document_id: str, delete_data: PersonDocumentSoftDelete) -> PersonDocument:
        """Soft delete de documento"""
        document = await PersonDocumentService.get_by_id(db, person_id, document_id)
        
        document.deleted_at = datetime.now(timezone.utc)
        document.deleted_reason = delete_data.deleted_reason
        
        await db.flush()
        return document


# =====================================================
# PERSON MEDIA SERVICE
# =====================================================

class PersonMediaService:
    """Service para operações de PersonMedia"""

    @staticmethod
    async def get_by_person(db: AsyncSession, person_id: str) -> List[PersonMedia]:
        """Lista todas as mídias de uma pessoa"""
        await PersonService.get_by_id(db, person_id)

        stmt = select(PersonMedia).where(
            PersonMedia.person_id == person_id,
            PersonMedia.deleted_at == None
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, person_id: str, media_id: str) -> PersonMedia:
        """Busca mídia por ID"""
        stmt = select(PersonMedia).where(
            PersonMedia.id == media_id,
            PersonMedia.person_id == person_id,
            PersonMedia.deleted_at == None
        )
        result = await db.execute(stmt)
        media = result.scalar_one_or_none()

        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Mídia {media_id} não encontrada",
                    request_id="",
                    details=ErrorDetail(field="media_id")
                ).model_dump()
            )

        return media

    @staticmethod
    async def create(db: AsyncSession, person_id: str, media_data: PersonMediaCreate) -> PersonMedia:
        """Cria nova mídia para pessoa"""
        await PersonService.get_by_id(db, person_id)

        # Se is_primary, remover primary dos outros do mesmo tipo
        if media_data.is_primary:
            stmt = select(PersonMedia).where(
                PersonMedia.person_id == person_id,
                PersonMedia.media_type == media_data.media_type,
                PersonMedia.is_primary == True,
                PersonMedia.deleted_at == None
            )
            result = await db.execute(stmt)
            other_media = result.scalars().all()
            for m in other_media:
                m.is_primary = False

        media = PersonMedia(
            person_id=person_id,
            **media_data.model_dump()
        )
        db.add(media)
        await db.flush()
        return media

    @staticmethod
    async def update(db: AsyncSession, person_id: str, media_id: str, media_data: PersonMediaUpdate) -> PersonMedia:
        """Atualiza mídia"""
        media = await PersonMediaService.get_by_id(db, person_id, media_id)

        if media_data.is_primary:
            stmt = select(PersonMedia).where(
                PersonMedia.person_id == person_id,
                PersonMedia.media_type == media.media_type,
                PersonMedia.id != media_id,
                PersonMedia.is_primary == True,
                PersonMedia.deleted_at == None
            )
            result = await db.execute(stmt)
            other_media = result.scalars().all()
            for m in other_media:
                m.is_primary = False

        update_data = media_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media, field, value)

        await db.flush()
        return media

    @staticmethod
    async def soft_delete(db: AsyncSession, person_id: str, media_id: str, delete_data: PersonMediaSoftDelete) -> PersonMedia:
        """Soft delete de mídia"""
        media = await PersonMediaService.get_by_id(db, person_id, media_id)
        
        media.deleted_at = datetime.now(timezone.utc)
        media.deleted_reason = delete_data.deleted_reason
        
        await db.flush()
        return media

    @staticmethod
    async def process_profile_photo(
        db: AsyncSession,
        person_id: str,
        image_bytes: bytes,
        filename: str,
        *,
        remove_background: bool = True,
        background_color: tuple = (255, 255, 255),  # Branco
    ) -> PersonMedia:
        """
        Processa e salva foto de perfil com remoção de fundo.
        
        CANÔNICO (31/12/2025): Fotos de atletas usam person_media, não athletes.athlete_photo_path.
        
        Fluxo:
        1. Remove fundo com rembg (se remove_background=True)
        2. Aplica fundo branco
        3. Converte para JPEG
        4. Salva arquivo e cria registro em person_media
        
        Args:
            db: Sessão do banco
            person_id: ID da pessoa
            image_bytes: Bytes da imagem original
            filename: Nome original do arquivo
            remove_background: Se True, remove fundo com rembg
            background_color: Cor RGB do fundo (default: branco)
            
        Returns:
            PersonMedia criado
            
        Raises:
            HTTPException: Se processamento falhar
        """
        import io
        import os
        from uuid import uuid4
        
        # Import lazy para não carregar se não usar
        try:
            from PIL import Image
            if remove_background:
                from rembg import remove
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error_code=ErrorCode.INTERNAL_ERROR,
                    message=f"Dependência de processamento de imagem não instalada: {e}",
                    request_id="",
                    details=None
                ).model_dump()
            )
        
        try:
            # Verificar que pessoa existe
            await PersonService.get_by_id(db, person_id)
            
            # Abrir imagem
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # Converter para RGB se necessário
            if input_image.mode in ('RGBA', 'P'):
                input_image = input_image.convert('RGB')
            
            # Remover fundo se solicitado
            if remove_background:
                # Processar com rembg
                output_bytes = remove(image_bytes)
                output_image = Image.open(io.BytesIO(output_bytes))
                
                # Criar imagem com fundo branco
                background = Image.new('RGB', output_image.size, background_color)
                
                # Se tem alpha (transparência), composite
                if output_image.mode == 'RGBA':
                    background.paste(output_image, mask=output_image.split()[3])
                else:
                    background = output_image
                
                final_image = background
            else:
                final_image = input_image
            
            # Redimensionar se muito grande (max 800x800)
            max_size = (800, 800)
            final_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Converter para JPEG bytes
            output_buffer = io.BytesIO()
            final_image.save(output_buffer, format='JPEG', quality=85, optimize=True)
            output_bytes = output_buffer.getvalue()
            
            # Gerar nome único para arquivo
            file_id = str(uuid4())
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}_{file_id}.jpg"
            
            # Caminho relativo para storage (pode ser ajustado para S3/CloudStorage)
            storage_path = f"uploads/persons/{person_id}/photos/{new_filename}"
            
            # Garantir que diretório existe
            full_dir = os.path.dirname(storage_path)
            os.makedirs(full_dir, exist_ok=True)
            
            # Salvar arquivo
            with open(storage_path, 'wb') as f:
                f.write(output_bytes)
            
            # Desativar outras fotos de perfil primárias
            stmt = select(PersonMedia).where(
                PersonMedia.person_id == person_id,
                PersonMedia.media_type == 'profile_photo',
                PersonMedia.is_primary == True,
                PersonMedia.deleted_at == None
            )
            result = await db.execute(stmt)
            other_media = result.scalars().all()
            for m in other_media:
                m.is_primary = False
            
            # Criar registro em person_media
            media = PersonMedia(
                person_id=person_id,
                media_type='profile_photo',
                file_url=storage_path,
                file_name=new_filename,
                file_size=len(output_bytes),
                mime_type='image/jpeg',
                is_primary=True,
                description='Foto de perfil processada com remoção de fundo'
            )
            db.add(media)
            await db.flush()
            
            return media
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error_code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erro ao processar imagem: {str(e)}",
                    request_id="",
                    details=None
                ).model_dump()
            )

