import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IntentHire | AI Recruitment Platform",
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
                width: '44px',
                height: '44px',
                background: 'linear-gradient(135deg, var(--accent-base), #0f766e)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                fontSize: '1.05rem',
                color: 'white',
                boxShadow: '0 12px 28px rgba(14, 116, 144, 0.22)'
              }}>IH</div>
              <div>
                <h1 style={{ fontSize: '1.65rem', margin: 0 }}>IntentHire</h1>
                <p style={{ margin: '0.15rem 0 0', fontSize: '0.9rem' }}>AI-powered talent screening workspace</p>
              </div>
            </div>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
