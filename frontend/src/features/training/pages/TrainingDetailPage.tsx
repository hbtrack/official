import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Clock, Target, GripVertical, Trash2, Plus, UserCheck } from 'lucide-react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  useTrainingSession,
  usePublishTrainingSession,
  useStartTrainingSession,
  useCompleteTrainingSession,
  useCancelTrainingSession,
  useSessionBlocks,
  useAddSessionBlock,
  useDeleteSessionBlock,
  useReorderSessionBlocks,
  useSessionAttendance,
  useRecordAttendance,
} from '../../../api/hooks/useTraining';
import { useUsers } from '../../../api/hooks/useUsers';

// ─── Constants ────────────────────────────────────────────────────────────────
const STATUS_LABELS: Record<string, { label: string; cls: string }> = {
  SCHEDULED: { label: 'Agendado', cls: 'bg-blue-100 text-blue-700' },
  PUBLISHED: { label: 'Publicado', cls: 'bg-green-100 text-green-700' },
  IN_PROGRESS: { label: 'Em andamento', cls: 'bg-yellow-100 text-yellow-700' },
  COMPLETED: { label: 'Concluído', cls: 'bg-gray-100 text-gray-700' },
  CANCELLED: { label: 'Cancelado', cls: 'bg-red-100 text-red-700' },
};

const PHASE_LABELS: Record<string, string> = {
  WARMUP: 'Aquecimento', ACTIVATION: 'Ativação', TECHNICAL: 'Técnico',
  DECISION_MAKING: 'Decisão', TACTICAL: 'Tático', REDUCED_GAME: 'Jogo reduzido', COOLDOWN: 'Desaquecimento',
};

const INTENSITY_LABELS: Record<string, { label: string; cls: string }> = {
  LOW: { label: 'Baixo', cls: 'bg-green-100 text-green-700' },
  MEDIUM: { label: 'Médio', cls: 'bg-yellow-100 text-yellow-700' },
  HIGH: { label: 'Alto', cls: 'bg-orange-100 text-orange-700' },
  MAXIMUM: { label: 'Máximo', cls: 'bg-red-100 text-red-700' },
};

const ATTENDANCE_STATUS_OPTIONS = ['PRESENT', 'ABSENT', 'JUSTIFIED', 'PRECONFIRMED'] as const;
const ATTENDANCE_LABELS: Record<string, { label: string; cls: string }> = {
  PRESENT: { label: 'Presente', cls: 'bg-green-100 text-green-700' },
  ABSENT: { label: 'Ausente', cls: 'bg-red-100 text-red-700' },
  JUSTIFIED: { label: 'Justificado', cls: 'bg-blue-100 text-blue-700' },
  PRECONFIRMED: { label: 'Pré-confirmado', cls: 'bg-gray-100 text-gray-700' },
};

// ─── SortableBlock component ──────────────────────────────────────────────────
type Block = {
  id: string; phase: string; orderIndex: number; durationMinutes: number;
  blockObjective: string; intensity: string; notes?: string; isOptional: boolean;
};

function SortableBlock({ block, onDelete, canEdit }: {
  block: Block; onDelete: (id: string) => void; canEdit: boolean;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: block.id });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 };
  const intensity = INTENSITY_LABELS[block.intensity] ?? { label: block.intensity, cls: 'bg-gray-100 text-gray-700' };

  return (
    <div ref={setNodeRef} style={style} className="flex items-start gap-3 bg-white rounded-lg border border-gray-200 p-4">
      {canEdit && (
        <button {...attributes} {...listeners} className="mt-1 cursor-grab text-gray-300 hover:text-gray-500">
          <GripVertical className="h-4 w-4" />
        </button>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 rounded px-2 py-0.5">
            {PHASE_LABELS[block.phase] ?? block.phase}
          </span>
          <span className={`text-xs font-medium rounded px-2 py-0.5 ${intensity.cls}`}>{intensity.label}</span>
          <span className="text-xs text-gray-400">{block.durationMinutes}min</span>
          {block.isOptional && <span className="text-xs text-gray-400 italic">opcional</span>}
        </div>
        <p className="text-sm text-gray-800 mt-1">{block.blockObjective}</p>
        {block.notes && <p className="text-xs text-gray-400 mt-0.5">{block.notes}</p>}
      </div>
      {canEdit && (
        <button onClick={() => onDelete(block.id)} className="text-gray-300 hover:text-red-500 transition-colors">
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export function TrainingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const sessionId = id ?? '';

  const { data: session, isLoading, error } = useTrainingSession(sessionId);
  const { data: blocks = [] } = useSessionBlocks(sessionId);
  const { data: attendance = [] } = useSessionAttendance(sessionId);
  const { data: teamMembers } = useUsers(session?.teamId ? { teamId: session.teamId } : undefined);

  const publish = usePublishTrainingSession();
  const start = useStartTrainingSession();
  const complete = useCompleteTrainingSession();
  const cancel = useCancelTrainingSession();
  const addBlock = useAddSessionBlock(sessionId);
  const deleteBlock = useDeleteSessionBlock(sessionId);
  const reorder = useReorderSessionBlocks(sessionId);
  const recordAttendance = useRecordAttendance(sessionId);

  const [showAddBlock, setShowAddBlock] = useState(false);
  const [blockForm, setBlockForm] = useState({
    phase: 'WARMUP' as Block['phase'],
    durationMinutes: 10,
    blockObjective: '',
    intensity: 'MEDIUM' as 'LOW' | 'MEDIUM' | 'HIGH' | 'MAXIMUM',
    notes: '',
    isOptional: false,
  });

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = blocks.findIndex((b) => b.id === active.id);
    const newIndex = blocks.findIndex((b) => b.id === over.id);
    const newOrder = arrayMove(blocks, oldIndex, newIndex);
    reorder.mutate(newOrder.map((b) => b.id));
  }

  function handleAddBlock(e: React.FormEvent) {
    e.preventDefault();
    addBlock.mutate(
      { ...blockForm, orderIndex: blocks.length },
      { onSuccess: () => { setShowAddBlock(false); setBlockForm({ phase: 'WARMUP', durationMinutes: 10, blockObjective: '', intensity: 'MEDIUM', notes: '', isOptional: false }); } }
    );
  }

  const canEditBlocks = session && ['SCHEDULED', 'PUBLISHED'].includes(session.status);

  if (isLoading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
    </div>
  );

  if (error || !session) return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
      Treino não encontrado.
    </div>
  );

  const badge = STATUS_LABELS[session.status] ?? { label: session.status, cls: 'bg-gray-100 text-gray-700' };

  return (
    <div className="space-y-6 max-w-3xl">
      <Link to="/training" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Treinos
      </Link>

      {/* Session header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{session.sessionType}</h1>
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
              <Calendar className="h-4 w-4" />
              <span>{new Date(session.sessionAt).toLocaleString('pt-BR')}</span>
            </div>
          </div>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${badge.cls}`}>{badge.label}</span>
        </div>
        {session.durationPlannedMinutes && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>Duração planejada: {session.durationPlannedMinutes} minutos</span>
          </div>
        )}
        {session.mainObjective && (
          <div className="flex items-start gap-2 text-sm text-gray-600">
            <Target className="h-4 w-4 mt-0.5 shrink-0" />
            <span>{session.mainObjective}</span>
          </div>
        )}
      </div>

      {/* State actions - contextual by status */}
      {session.status !== 'COMPLETED' && session.status !== 'CANCELLED' && (
        <div className="flex flex-wrap gap-3">
          {session.status === 'SCHEDULED' && (
            <button
              onClick={() => publish.mutate(sessionId)}
              disabled={publish.isPending}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-60 transition-colors"
            >
              {publish.isPending ? 'Publicando...' : '▶ Publicar Treino'}
            </button>
          )}
          {(session.status === 'SCHEDULED' || session.status === 'PUBLISHED') && (
            <button
              onClick={() => start.mutate(sessionId)}
              disabled={start.isPending}
              className="rounded-lg bg-yellow-600 px-4 py-2 text-sm font-medium text-white hover:bg-yellow-700 disabled:opacity-60 transition-colors"
            >
              {start.isPending ? 'Iniciando...' : '▶ Iniciar Treino'}
            </button>
          )}
          {session.status === 'IN_PROGRESS' && (
            <button
              onClick={() => complete.mutate(sessionId)}
              disabled={complete.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors"
            >
              {complete.isPending ? 'Concluindo...' : '✓ Concluir Treino'}
            </button>
          )}
          <button
            onClick={() => { if (confirm('Cancelar este treino?')) cancel.mutate(sessionId); }}
            disabled={cancel.isPending}
            className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-60 transition-colors"
          >
            {cancel.isPending ? 'Cancelando...' : 'Cancelar Treino'}
          </button>
        </div>
      )}

      {/* Blocks section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Blocos do treino ({blocks.length})</h2>
          {canEditBlocks && (
            <button
              onClick={() => setShowAddBlock(!showAddBlock)}
              className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
            >
              <Plus className="h-4 w-4" /> Adicionar bloco
            </button>
          )}
        </div>

        {showAddBlock && (
          <form onSubmit={handleAddBlock} className="rounded-lg bg-gray-50 border border-gray-200 p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Fase *</label>
                <select
                  value={blockForm.phase}
                  onChange={(e) => setBlockForm({ ...blockForm, phase: e.target.value as Block['phase'] })}
                  className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {Object.entries(PHASE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Intensidade *</label>
                <select
                  value={blockForm.intensity}
                  onChange={(e) => setBlockForm({ ...blockForm, intensity: e.target.value as 'LOW' | 'MEDIUM' | 'HIGH' | 'MAXIMUM' })}
                  className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {Object.entries(INTENSITY_LABELS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Duração (min) *</label>
                <input
                  type="number" required min={1}
                  value={blockForm.durationMinutes}
                  onChange={(e) => setBlockForm({ ...blockForm, durationMinutes: parseInt(e.target.value) })}
                  className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input type="checkbox" checked={blockForm.isOptional} onChange={(e) => setBlockForm({ ...blockForm, isOptional: e.target.checked })} />
                  Opcional
                </label>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Objetivo *</label>
              <input
                type="text" required
                value={blockForm.blockObjective}
                onChange={(e) => setBlockForm({ ...blockForm, blockObjective: e.target.value })}
                placeholder="Descreva o objetivo pedagógico deste bloco"
                className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Notas</label>
              <input
                type="text"
                value={blockForm.notes}
                onChange={(e) => setBlockForm({ ...blockForm, notes: e.target.value })}
                placeholder="Dicas táticas, adaptações..."
                className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" disabled={addBlock.isPending} className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-60">
                {addBlock.isPending ? 'Adicionando...' : 'Adicionar'}
              </button>
              <button type="button" onClick={() => setShowAddBlock(false)} className="rounded border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50">
                Cancelar
              </button>
            </div>
          </form>
        )}

        {blocks.length === 0 && !showAddBlock && (
          <p className="text-sm text-gray-400 py-4 text-center">Nenhum bloco adicionado ao treino.</p>
        )}

        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={blocks.map((b) => b.id)} strategy={verticalListSortingStrategy}>
            <div className="space-y-2">
              {blocks.map((block) => (
                <SortableBlock
                  key={block.id}
                  block={block}
                  canEdit={!!canEditBlocks}
                  onDelete={(blockId) => deleteBlock.mutate(blockId)}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>

      {/* Attendance section */}
      {(session.status === 'IN_PROGRESS' || session.status === 'COMPLETED' || session.status === 'PUBLISHED') && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <UserCheck className="h-5 w-5 text-gray-500" />
            <h2 className="font-semibold text-gray-900">Lista de presença</h2>
          </div>

          {teamMembers && teamMembers.items.length > 0 ? (
            <div className="space-y-2">
              {teamMembers.items.map((member) => {
                const record = attendance.find((a) => a.athleteId === member.id);
                const badge = record ? (ATTENDANCE_LABELS[record.status] ?? { label: record.status, cls: 'bg-gray-100 text-gray-700' }) : null;
                return (
                  <div key={member.id} className="flex items-center justify-between rounded-lg px-3 py-2 border border-gray-100">
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold">
                        {member.displayName?.[0]?.toUpperCase() ?? '?'}
                      </div>
                      <span className="text-sm text-gray-800">{member.displayName}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {badge && <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge.cls}`}>{badge.label}</span>}
                      {session.status !== 'COMPLETED' && (
                        <div className="flex gap-1">
                          {ATTENDANCE_STATUS_OPTIONS.map((s) => (
                            <button
                              key={s}
                              onClick={() => recordAttendance.mutate({ athleteId: member.id, status: s })}
                              className={`rounded px-2 py-0.5 text-xs border transition-colors ${record?.status === s ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-500 hover:bg-gray-50'}`}
                            >
                              {ATTENDANCE_LABELS[s].label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-400">
              {session.teamId ? 'Nenhum membro encontrado para este time.' : 'Sessão sem time vinculado — presença não disponível.'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
