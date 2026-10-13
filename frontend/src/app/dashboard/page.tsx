'use client';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Document {
  id: number;
  filename: string;
  status: string;
  created_at: string;
}

export default function DashboardPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const router = useRouter();

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get('/documents/');
      setDocuments(res.data.documents);
    } catch {}
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    api.get('/auth/me').then(res => setUserEmail(res.data.email)).catch(() => router.push('/login'));
    fetchDocuments();
  }, [router, fetchDocuments]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post('/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchDocuments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this document?')) return;
    try {
      await api.delete(`/documents/${id}`);
      fetchDocuments();
    } catch {}
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const statusColor = (s: string) => {
    if (s === 'COMPLETED') return 'bg-green-100 text-green-700';
    if (s === 'PROCESSING') return 'bg-yellow-100 text-yellow-700';
    if (s === 'FAILED') return 'bg-red-100 text-red-700';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">DocuStream</h1>
          <p className="text-gray-500">{userEmail}</p>
        </div>
        <div className="flex gap-3">
          <label className={`cursor-pointer px-4 py-2 rounded-lg font-medium transition ${uploading ? 'bg-gray-300' : 'bg-blue-600 text-white hover:bg-blue-700'}`}>
            {uploading ? 'Uploading...' : '+ Upload PDF'}
            <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
          </label>
          <button onClick={handleLogout} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition">Logout</button>
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-xl mb-2">No documents yet</p>
          <p>Upload a PDF to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-white p-4 rounded-lg shadow-sm border flex justify-between items-center">
              <div className="flex-1">
                <button onClick={() => router.push(`/documents/${doc.id}`)} className="text-lg font-medium text-blue-600 hover:underline text-left">
                  {doc.filename}
                </button>
                <p className="text-sm text-gray-400">{new Date(doc.created_at).toLocaleString()}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor(doc.status)}`}>{doc.status}</span>
                <button onClick={() => handleDelete(doc.id)} className="text-red-400 hover:text-red-600 text-sm">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
