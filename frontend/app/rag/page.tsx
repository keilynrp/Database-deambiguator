"use client";

import { PageHeader } from "../components/ui";
import RAGChatInterface from "../components/RAGChatInterface";

export default function RAGPage() {
    return (
        <div className="space-y-6">
            <PageHeader
                breadcrumbs={[{ label: "Home", href: "/" }, { label: "Semantic RAG" }]}
                title="Semantic AI"
                description="AI-powered retrieval and semantic analysis over your enriched entity catalog"
            />
            <RAGChatInterface />
        </div>
    );
}
