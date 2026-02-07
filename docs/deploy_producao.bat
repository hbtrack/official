@echo off
REM ============================================================================
REM DEPLOYMENT EM PRODUCAO - Sistema de Relatorios
REM ============================================================================
REM Este script aplica TODAS as migrations em producao
REM (FASE 1 + R1-R4 + FASE 2)
REM
REM IMPORTANTE: So execute apos criar snapshot no Neon!
REM ============================================================================

echo.
echo ================================================================================
echo DEPLOYMENT EM PRODUCAO - Sistema de Relatorios
echo ================================================================================
echo.
echo AVISOS IMPORTANTES:
echo   [!] Voce criou snapshot no Neon Console?
echo   [!] Este script aplicara 6 migrations em producao
echo   [!] Tempo estimado: 2-5 minutos
echo.
echo Pressione Ctrl+C para cancelar ou
pause

echo.
echo [1/4] Verificando estado atual...
echo.
.venv\Scripts\alembic.exe -c backend\db\alembic.ini current

echo.
echo [2/4] Listando migrations a aplicar...
echo.
.venv\Scripts\alembic.exe -c backend\db\alembic.ini history --verbose

echo.
echo [3/4] Aplicando TODAS as migrations (FASE 1 + R1-R4 + FASE 2)...
echo.
echo IMPORTANTE: Isto pode levar alguns minutos...
echo.
.venv\Scripts\alembic.exe -c backend\db\alembic.ini upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo [ERROR] Migration FALHOU!
    echo ================================================================================
    echo.
    echo O que fazer:
    echo   1. Verifique os erros acima
    echo   2. Se necessario, restaure snapshot do Neon
    echo   3. Entre em contato com suporte
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] Verificando estado final...
echo.
.venv\Scripts\alembic.exe -c backend\db\alembic.ini current

echo.
echo ================================================================================
echo [SUCCESS] Migrations aplicadas com sucesso!
echo ================================================================================
echo.
echo Estado esperado: b4b136a1af44 (head)
echo.
echo Proximos passos:
echo   1. Executar: python backend\verify_production_rag.py
echo   2. Testar endpoints de relatorios
echo   3. Refresh de materialized views
echo.
pause
