import { Newspaper } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = {
  title: "News",
};

export default function NewsPage() {
  return (
    <>
      <PageHeader
        title="News"
        description="Headlines from the sources you follow, summarised."
      />
      <EmptyState
        icon={Newspaper}
        title="No news sources yet"
        description="Stories from your news sources will be collected and summarised here."
      />
    </>
  );
}
