import type { Metadata } from "next";
import "./globals.css";
import Footer from "../components/Footer";

export const metadata: Metadata = {
  title: "AI Tender Assistant for MSMEs",
  description: "Discover, evaluate, and prepare applications for Indian government tenders with AI-powered Sarvam Vision OCR and eligibility matching.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="flex min-h-screen flex-col bg-slate-950 text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
        <Footer />
      </body>
    </html>
  );
}
