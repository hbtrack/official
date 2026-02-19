import os

def consolidar_limpo(diretorio_raiz, arquivo_saida):
    extensoes_permitidas = ['.py', '.ts', '.tsx', '.js', '.sql']
    pastas_proibidas = ['node_modules', 'venv', '.venv', '.next', '__pycache__', '.git', 'dist', 'build', 'backup']

    with open(arquivo_saida, 'w', encoding='utf-8') as f_saida:
        for raiz, diretorios, arquivos in os.walk(diretorio_raiz):
            # 1. Bloqueia pastas proibidas e ocultas
            diretorios[:] = [d for d in diretorios if not d.startswith('.') and d.lower() not in pastas_proibidas]
            
            # 2. Foca apenas nas pastas de código real
            caminho_rel = os.path.relpath(raiz, diretorio_raiz).lower()
            if not any(f in caminho_rel for f in ['app', 'src', 'infra', 'db']) and caminho_rel != '.':
                continue

            for arquivo in arquivos:
                if arquivo.lower() == 'preparar_contexto.py' or 'lock' in arquivo.lower():
                    continue

                if os.path.splitext(arquivo)[1].lower() in extensoes_permitidas:
                    caminho_full = os.path.join(raiz, arquivo)
                    
                    try:
                        with open(caminho_full, 'r', encoding='utf-8') as f_in:
                            linhas = f_in.readlines()
                            
                            # FILTRO RADICAL: Só aceita o arquivo se ele não tiver linhas "monstro"
                            # E se tiver um tamanho total razoável
                            if len(linhas) < 2000 and all(len(l) < 300 for l in linhas):
                                f_saida.write(f"\n{'='*50}\nARQUIVO: {os.path.relpath(caminho_full, diretorio_raiz)}\n{'='*50}\n\n")
                                f_saida.writelines(linhas)
                                f_saida.write("\n\n")
                    except:
                        continue

consolidar_limpo('.', 'projeto_completo_para_gemini.txt')
print("Limpeza profunda concluída!")