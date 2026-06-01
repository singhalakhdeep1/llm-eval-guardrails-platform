import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "LLM Evaluation and Guardrails Platform",
    description: "Prompt registry, model evaluation, guardrail scorecards, and release gates.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
