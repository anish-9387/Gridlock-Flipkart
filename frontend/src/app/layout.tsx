import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'CascadeIQ — Event Impact Intelligence',
  description: 'Event Impact Forecasting & Response Intelligence System — Gridlock-Flipkart 2.0',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 ml-64 p-6 lg:p-8 overflow-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
