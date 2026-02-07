"""
Script para processar fila de emails pendentes

Uso:
    # Executar manualmente
    python scripts/process_email_queue.py

    # Cronjob (Linux/Mac) - rodar a cada 1 minuto
    * * * * * cd /path/to/backend && python scripts/process_email_queue.py >> logs/email_queue.log 2>&1

    # Task Scheduler (Windows) - criar tarefa para executar a cada 1 minuto
    schtasks /create /tn "HBTrack Email Queue" /tr "python C:\\path\\to\\backend\\scripts\\process_email_queue.py" /sc minute /mo 1
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from app.db.session import SessionLocal
from app.services.email_queue_service import process_pending_emails

def main():
    """
    Processa emails pendentes da fila.
    """
    print(f"[{datetime.now().isoformat()}] Starting email queue processing...")
    
    db = SessionLocal()
    try:
        stats = process_pending_emails(db, batch_size=50)
        
        print(f"[{datetime.now().isoformat()}] Email processing complete:")
        print(f"  - Sent: {stats['sent']}")
        print(f"  - Failed: {stats['failed']}")
        print(f"  - Retried: {stats['retried']}")
        print(f"  - Skipped: {stats['skipped']}")
        
        return 0
        
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR: {str(e)}", file=sys.stderr)
        return 1
        
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
