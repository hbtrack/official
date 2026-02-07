#!/usr/bin/env python3
"""
Verificador de Banco - Ficha Única E2E
======================================

Script para verificar o estado do banco durante testes E2E da Ficha Única.
Execute após cada ação no frontend para validar.

Uso:
    python check_ficha_unica_db.py [comando]

Comandos:
    users       - Lista todos os usuários
    persons     - Lista todas as pessoas
    orgs        - Lista organizações
    teams       - Lista equipes
    memberships - Lista vínculos organizacionais
    athletes    - Lista atletas
    all         - Mostra tudo
    check EMAIL - Verifica usuário específico
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime
from tabulate import tabulate

# Cores
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_db():
    from app.core.db import get_db as _get_db
    return next(_get_db())

def list_users():
    """Lista todos os usuários"""
    from app.models.user import User
    from app.models.role import Role
    
    db = get_db()
    users = db.query(User).filter(User.deleted_at == None).all()
    
    print(f"\n{BLUE}{BOLD}=== USUÁRIOS ({len(users)}) ==={RESET}")
    
    data = []
    for u in users:
        role = db.query(Role).filter(Role.id == u.role_id).first() if hasattr(u, 'role_id') and u.role_id else None
        role_name = role.name if role else "N/A"
        data.append([
            str(u.id)[:8] + "...",
            u.email,
            role_name,
            "✓" if u.password_hash else "✗",
            str(u.person_id)[:8] + "..." if u.person_id else "N/A",
            u.created_at.strftime("%H:%M:%S") if u.created_at else "N/A"
        ])
    
    print(tabulate(data, headers=["ID", "Email", "Role", "Senha", "Person", "Criado"], tablefmt="grid"))

def list_persons():
    """Lista todas as pessoas"""
    from app.models.person import Person
    
    db = get_db()
    persons = db.query(Person).filter(Person.deleted_at == None).order_by(Person.created_at.desc()).limit(20).all()
    
    print(f"\n{BLUE}{BOLD}=== PESSOAS (últimas 20) ==={RESET}")
    
    data = []
    for p in persons:
        data.append([
            str(p.id)[:8] + "...",
            p.full_name,
            p.gender or "N/A",
            str(p.birth_date) if p.birth_date else "N/A",
            p.created_at.strftime("%H:%M:%S") if p.created_at else "N/A"
        ])
    
    print(tabulate(data, headers=["ID", "Nome", "Gênero", "Nascimento", "Criado"], tablefmt="grid"))

def list_organizations():
    """Lista organizações"""
    from app.models.organization import Organization
    
    db = get_db()
    orgs = db.query(Organization).filter(Organization.deleted_at == None).all()
    
    print(f"\n{BLUE}{BOLD}=== ORGANIZAÇÕES ({len(orgs)}) ==={RESET}")
    
    data = []
    for o in orgs:
        data.append([
            str(o.id)[:8] + "...",
            o.name,
            o.created_at.strftime("%H:%M:%S") if o.created_at else "N/A"
        ])
    
    print(tabulate(data, headers=["ID", "Nome", "Criado"], tablefmt="grid"))

def list_teams():
    """Lista equipes"""
    from app.models.team import Team
    from app.models.organization import Organization
    from app.models.category import Category
    
    db = get_db()
    teams = db.query(Team).filter(Team.deleted_at == None).all()
    
    print(f"\n{BLUE}{BOLD}=== EQUIPES ({len(teams)}) ==={RESET}")
    
    data = []
    for t in teams:
        org = db.query(Organization).filter(Organization.id == t.organization_id).first()
        cat = db.query(Category).filter(Category.id == t.category_id).first() if t.category_id else None
        data.append([
            str(t.id)[:8] + "...",
            t.name,
            org.name[:15] if org else "N/A",
            cat.name if cat else "N/A",
            t.gender or "N/A",
            t.created_at.strftime("%H:%M:%S") if t.created_at else "N/A"
        ])
    
    print(tabulate(data, headers=["ID", "Nome", "Organização", "Categoria", "Gênero", "Criado"], tablefmt="grid"))

def list_memberships():
    """Lista vínculos organizacionais"""
    from app.models.membership import OrgMembership
    from app.models.person import Person
    from app.models.organization import Organization
    from app.models.role import Role
    
    db = get_db()
    memberships = db.query(OrgMembership).filter(OrgMembership.deleted_at == None).all()
    
    print(f"\n{BLUE}{BOLD}=== MEMBERSHIPS ({len(memberships)}) ==={RESET}")
    
    data = []
    for m in memberships:
        person = db.query(Person).filter(Person.id == m.person_id).first()
        org = db.query(Organization).filter(Organization.id == m.organization_id).first()
        role = db.query(Role).filter(Role.id == m.role_id).first()
        data.append([
            str(m.id)[:8] + "...",
            person.full_name[:20] if person else "N/A",
            org.name[:15] if org else "N/A",
            role.name if role else "N/A",
            "Ativo" if m.end_at is None else "Inativo"
        ])
    
    print(tabulate(data, headers=["ID", "Pessoa", "Organização", "Papel", "Status"], tablefmt="grid"))

def list_athletes():
    """Lista atletas"""
    from app.models.athlete import Athlete
    from app.models.person import Person
    
    db = get_db()
    athletes = db.query(Athlete).filter(Athlete.deleted_at == None).all()
    
    print(f"\n{BLUE}{BOLD}=== ATLETAS ({len(athletes)}) ==={RESET}")
    
    data = []
    for a in athletes:
        person = db.query(Person).filter(Person.id == a.person_id).first()
        data.append([
            str(a.id)[:8] + "...",
            person.full_name if person else "N/A",
            a.jersey_number or "N/A",
            a.dominant_hand or "N/A",
            a.created_at.strftime("%H:%M:%S") if a.created_at else "N/A"
        ])
    
    print(tabulate(data, headers=["ID", "Nome", "Número", "Mão Dom.", "Criado"], tablefmt="grid"))

def check_user(email: str):
    """Verifica um usuário específico"""
    from app.models.user import User
    from app.models.person import Person
    from app.models.role import Role
    from app.models.membership import OrgMembership
    from app.models.organization import Organization
    
    db = get_db()
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"\n{RED}❌ Usuário não encontrado: {email}{RESET}")
        return
    
    print(f"\n{GREEN}{BOLD}=== USUÁRIO: {email} ==={RESET}")
    
    # Dados do usuário
    role = db.query(Role).filter(Role.id == user.role_id).first() if hasattr(user, 'role_id') and user.role_id else None
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Role: {role.name if role else 'N/A'} (id={user.role_id if hasattr(user, 'role_id') else 'N/A'})")
    print(f"  Senha definida: {'✓' if user.password_hash else '✗'}")
    print(f"  Person ID: {user.person_id}")
    
    # Dados da pessoa
    if user.person_id:
        person = db.query(Person).filter(Person.id == user.person_id).first()
        if person:
            print(f"\n  {BLUE}--- Pessoa ---{RESET}")
            print(f"  Nome: {person.full_name}")
            print(f"  Gênero: {person.gender or 'N/A'}")
            print(f"  Nascimento: {person.birth_date or 'N/A'}")
    
    # Memberships
    memberships = db.query(OrgMembership).filter(
        OrgMembership.person_id == user.person_id,
        OrgMembership.deleted_at == None
    ).all()
    
    if memberships:
        print(f"\n  {BLUE}--- Vínculos Organizacionais ({len(memberships)}) ---{RESET}")
        for m in memberships:
            org = db.query(Organization).filter(Organization.id == m.organization_id).first()
            role = db.query(Role).filter(Role.id == m.role_id).first()
            print(f"    • {org.name if org else 'N/A'} como {role.name if role else 'N/A'}")
    else:
        print(f"\n  {YELLOW}⚠ Sem vínculos organizacionais{RESET}")

def show_all():
    """Mostra todas as tabelas"""
    list_users()
    list_persons()
    list_organizations()
    list_teams()
    list_memberships()
    list_athletes()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    try:
        if cmd == "users":
            list_users()
        elif cmd == "persons":
            list_persons()
        elif cmd == "orgs":
            list_organizations()
        elif cmd == "teams":
            list_teams()
        elif cmd == "memberships":
            list_memberships()
        elif cmd == "athletes":
            list_athletes()
        elif cmd == "all":
            show_all()
        elif cmd == "check" and len(sys.argv) > 2:
            check_user(sys.argv[2])
        else:
            print(__doc__)
    except Exception as e:
        print(f"{RED}Erro: {e}{RESET}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
