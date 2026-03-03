'use client';

/**
 * SCREEN-TRAIN-024: Interface conversacional do atleta com IA Coach pós-treino.
 *
 * AR_192 — AR-TRAIN-021
 *
 * INV-079: Reconhecimento usa apenas métricas agregadas (não texto íntimo).
 * INV-080: Propostas da IA chegam como rascunho — treinador aprova.
 * INV-081: Sugestões com justificativa são 'recomendacao'; sem = 'ideia_generica'.
 */

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

// Tipos base (CONTRACT-TRAIN-101..104)
interface AIMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  label?: 'recomendacao' | 'ideia_generica';  // INV-081
  isDraft?: boolean;                           // INV-080
  timestamp: string;
}

interface ChatState {
  messages: AIMessage[];
  isLoading: boolean;
  inputValue: string;
}

export default function AIChatPage() {
  const params = useParams();
  const sessionId = params?.sessionId as string;

  const [state, setState] = useState<ChatState>({
    messages: [
      {
        id: '0',
        role: 'ai',
        content:
          'Olá! Sou o IA Coach. Vejo que você acabou de concluir uma sessão de treino. ' +
          'Como você está se sentindo? Posso ajudar com feedback personalizado.',
        timestamp: new Date().toISOString(),
      },
    ],
    isLoading: false,
    inputValue: '',
  });

  const handleSend = async () => {
    const userMessage = state.inputValue.trim();
    if (!userMessage) return;

    const newUserMsg: AIMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, newUserMsg],
      inputValue: '',
      isLoading: true,
    }));

    try {
      const res = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });

      if (res.ok) {
        const data = await res.json();
        const aiMsg: AIMessage = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: data.response ?? 'Resposta da IA não disponível.',
          timestamp: new Date().toISOString(),
        };
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, aiMsg],
          isLoading: false,
        }));
      } else {
        setState((prev) => ({ ...prev, isLoading: false }));
      }
    } catch {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">IA Coach — Pós-Treino</h1>
        <p className="text-sm text-gray-500">Sessão: {sessionId}</p>
      </header>

      {/* Histórico de mensagens */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {state.messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs rounded-lg px-4 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {msg.content}
              {/* Badge para rascunho da IA (INV-080) */}
              {msg.isDraft && (
                <span className="ml-2 inline-block rounded bg-yellow-200 px-1 text-xs text-yellow-800">
                  Rascunho
                </span>
              )}
              {/* Badge label de sugestão (INV-081) */}
              {msg.label && (
                <span
                  className={`ml-2 inline-block rounded px-1 text-xs ${
                    msg.label === 'recomendacao'
                      ? 'bg-green-200 text-green-800'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {msg.label === 'recomendacao' ? 'Recomendação' : 'Ideia Genérica'}
                </span>
              )}
            </div>
          </div>
        ))}
        {state.isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2 text-sm text-gray-500">
              IA Coach está digitando...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={state.inputValue}
          onChange={(e) =>
            setState((prev) => ({ ...prev, inputValue: e.target.value }))
          }
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Digite sua mensagem..."
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={state.isLoading}
        />
        <button
          onClick={handleSend}
          disabled={state.isLoading || !state.inputValue.trim()}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}
