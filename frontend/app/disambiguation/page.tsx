"use client";

import { PageHeader } from "../components/ui";
import DisambiguationTool from "../components/DisambiguationTool";

export default function DisambiguationPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Disambiguation" }]}
        title="Data Disambiguation"
        description="Find and resolve data inconsistencies across entity fields"
      />
      <DisambiguationTool />
    </div>
  );
}
