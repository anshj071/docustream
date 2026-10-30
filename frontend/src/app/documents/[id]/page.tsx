'use client';
import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Citation {
  chunk_content: string;
  page_number: number | null;
  relevance_score: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export default function DocumentPage() {
  const params = useParams();
  const router = useRouter();
  const docId = params.id;
  const [document, setDocument] = useState<any>(null);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocument = useCallback(async () => {
    try {
      const res = await api.get(`/documents/${docId}`);
      setDocument(res.data);
    } catch {
      router.push('/dashboard');
    }
  }, [docId, router]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetchDocument();
  }, [fetchDocument, router]);

  // Auto-poll if document is not yet COMPLETED or FAILED
  useEffect(() => {
    if (!document) return;
    if (document.status === 'COMPLETED' || document.status === 'FAILED') return;

    const interval = setInterval(() => {
      fetchDocument();
    }, 3000);

    return () => clearInterval(interval);
  }, [document, fetchDocument]);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    const userQuestion = question;
    setQuestion('');
    setMessages(prev => [...prev, { role: 'user', content: userQuestion }]);
    setLoading(true);
    try {
      const res = await api.post(`/documents/${docId}/ask`, { question: userQuestion, top_k: 5 });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.answer, citations: res.data.citations }]);
    } catch (err: any) {
      const message = err.response?.data?.detail
        || (err.response
          ? `The answer request failed (HTTP ${err.response.status}). Please try again.`
          : 'Could not reach the DocuStream API. Check that the backend is running and the frontend API URL is configured.');
      setMessages(prev => [...prev, { role: 'assistant', content: message }]);
    } finally {
      setLoading(false);
    }
  };

  if (!document) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>;

  return (
    <div className="max-w-4xl mx-auto p-6 flex flex-col h-screen">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => router.push('/dashboard')} className="text-gray-500 hover:text-gray-700">&larr; Back</button>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{document.filename}</h1>
          <p className="text-sm text-gray-500">
            Status:{' '}
            <span className={`font-semibold ${document.status === 'COMPLETED' ? 'text-green-600' : document.status === 'FAILED' ? 'text-red-600' : 'text-yellow-600'}`}>
              {document.status}
            </span>
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-white rounded-lg shadow-sm border p-4 mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-16">
            <p className="text-lg mb-2">Ask a question about this document</p>
            <p className="text-sm">The AI will answer based only on the document content</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                  <p className="text-xs font-semibold text-gray-500">Sources:</p>
                  {msg.citations.map((c, j) => (
                    <div key={j} className="bg-white p-2 rounded text-xs text-gray-600 border">
                      {c.page_number && <span className="font-medium text-blue-600">Page {c.page_number}</span>}
                      {' — '}{c.chunk_content}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="flex justify-start"><div className="bg-gray-100 p-3 rounded-lg text-gray-500">Thinking...</div></div>}
      </div>

      {document.status === 'COMPLETED' ? (
        <form onSubmit={handleAsk} className="flex gap-2">
          <input
            type="text" value={question} onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this document..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            disabled={loading}
          />
          <button type="submit" disabled={loading} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50">Ask</button>
        </form>
      ) : document.status === 'FAILED' ? (
        <div className="text-center text-red-600 bg-red-50 p-3 rounded-lg">
          Document processing failed. Please delete this document and try uploading again.
        </div>
      ) : (
        <div className="text-center text-yellow-600 bg-yellow-50 p-3 rounded-lg animate-pulse">
          Document is currently being processed ({document.status}). It will automatically be ready in a few seconds...
        </div>
      )}
    </div>
  );
}
