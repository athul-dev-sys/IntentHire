import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "intenthire | AI Recruitment Platform",
  description: "Advanced semantic resume parsing and candidate ranking for volume hiring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <main className="container animate-enter">
          <header className="flex-between" style={{ marginBottom: "2rem" }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                background: 'linear-gradient(135deg, var(--accent-base), #8b5cf6)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                fontSize: '1.2rem'
              }}>IH</div>
              <h1 style={{ fontSize: '1.5rem', margin: 0 }}>intenthire</h1>
            </div>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
