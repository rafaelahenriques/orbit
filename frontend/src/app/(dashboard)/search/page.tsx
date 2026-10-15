import { Search } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = {
  title: "Search",
};

export default function SearchPage() {
  return (
    <>
      <PageHeader
        title="Search"
        description="Ask questions about your email, calendar, and news in plain language."
      />
      <EmptyState
        icon={Search}
        title="Search is not ready yet"
        description="Once your data is synced, you can ask things like “What do I have on Thursday?”"
      />
    </>
  );
}
