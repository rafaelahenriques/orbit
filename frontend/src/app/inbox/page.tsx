import { Inbox } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = {
  title: "Inbox",
};

export default function InboxPage() {
  return (
    <>
      <PageHeader
        title="Inbox"
        description="Important email, ranked and summarised."
      />
      <EmptyState
        icon={Inbox}
        title="Gmail is not connected yet"
        description="Connect Gmail to see important email and the messages that need a reply."
      />
    </>
  );
}
