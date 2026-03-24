import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Calendar } from 'lucide-react';
import { useSeason } from '../../../api/hooks/useSeasons';

export function SeasonDetailPage() {
  const { seasonId } = useParams<{ seasonId: string }>();
  const { data: season, isLoading, error } = useSeason(seasonId ?? '');

  if (isLoading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
    </div>
  );

  if (error || !season) return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
      Temporada não encontrada.
    </div>
  );

  const started = season.startDate ? new Date(season.startDate).toLocaleDateString('pt-BR') : '—';
  const ended = season.endDate ? new Date(season.endDate).toLocaleDateString('pt-BR') : '—';

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to="/seasons" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Temporadas
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Temporada {season.year}</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Calendar className="h-4 w-4" />
          <span>{started} — {ended}</span>
        </div>
      </div>
    </div>
  );
}
