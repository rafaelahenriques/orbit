import { CalendarDays } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = {
  title: "Calendar",
};

export default function CalendarPage() {
  return (
    <>
      <PageHeader title="Calendar" description="Your schedule at a glance." />
      <EmptyState
        icon={CalendarDays}
        title="Google Calendar is not connected yet"
        description="Connect Google Calendar to see your upcoming events and what to prepare for them."
      />
    </>
  );
}
