import os

def consolidar_arquivos_especificos():
    # Lista de arquivos a serem consolidados
    arquivos_alvo = [
        r'./docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml',
        r'./docs/_canon/_agent/FAILURE_TO_GATES.yaml',
        r'./docs/_canon/_agent/GATES_REGISTRY.yaml',
        r'./docs/_INDEX.yaml',
        r'./_reports/audit/HB-AUDIT-20260218-014/context.json',
        r'./_reports/audit/HB-AUDIT-20260218-014/summary.json',
        r'./_reports/cases/CORR-2026-02-18-003/state.yaml',
    ]
    
    arquivo_saida = 'arquivos_consolidados.txt'
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f_saida:
        for caminho_arquivo in arquivos_alvo:
            # Verifica se é um arquivo (não diretório) e existe
            if os.path.isfile(caminho_arquivo):
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f_in:
                        conteudo = f_in.read()
                        
                        # Formata o separador no TXT final
                        f_saida.write(f"\n{'='*80}\nARQUIVO: {caminho_arquivo}\n{'='*80}\n\n")
                        f_saida.write(conteudo)
                        f_saida.write("\n\n")
                        
                    print(f"✓ Adicionado: {os.path.basename(caminho_arquivo)}")
                        
                except Exception as e:
                    print(f"✗ Erro ao ler {caminho_arquivo}: {e}")
            else:
                print(f"⚠ Arquivo não encontrado ou é diretório: {caminho_arquivo}")

# Roda a função
consolidar_arquivos_especificos()
print(f"\nSucesso! Arquivos consolidados em 'arquivos_consolidados.txt'.")