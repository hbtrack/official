-- ===============================================
-- Step 16: Adicionar permissão view_training_analytics
-- ===============================================
-- Data: 2024-01-30
-- Descrição: Adiciona permissão para visualizar analytics de treino
-- ===============================================

-- Adicionar nova permissão
INSERT INTO permissions (id, code, description) VALUES 
(66, 'view_training_analytics', 'Visualizar analytics de treino (Step 16)');

-- Atribuir permissão para DIRIGENTE (role_id=1)
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(1, 66);

-- Atribuir permissão para COORDENADOR (role_id=2)
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(2, 66);

-- Atribuir permissão para TREINADOR (role_id=3)
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(3, 66);

-- Verificação
SELECT 'Permissão view_training_analytics adicionada' as status;
SELECT r.name, p.code, p.description 
FROM role_permissions rp
JOIN roles r ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
WHERE p.code = 'view_training_analytics'
ORDER BY r.id;
