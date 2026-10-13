import './globals.css';

export const metadata = {
  title: 'DocuStream - AI Document Intelligence',
  description: 'Upload documents, search semantically, ask questions with AI',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
