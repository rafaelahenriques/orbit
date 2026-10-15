import { CalendarClock, Newspaper, Reply, Sparkles } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

const SECTIONS = [
  {
    title: "Briefing",
    icon: Sparkles,
    emptyTitle: "Your briefing will appear here",
    emptyDescription:
      "Once your Google account is connected, Orbit summarises your day each morning.",
  },
  {
    title: "Needs a reply",
    icon: Reply,
    emptyTitle: "Nothing waiting on you",
    emptyDescription:
      "Emails and messages that need your reply will show up here.",
  },
  {
    title: "Upcoming",
    icon: CalendarClock,
    emptyTitle: "No upcoming events",
    emptyDescription:
      "Your next meetings and events from Google Calendar will show up here.",
  },
  {
    title: "Top news",
    icon: Newspaper,
    emptyTitle: "No headlines yet",
    emptyDescription: "Stories from the sources you follow will show up here.",
  },
];

export default function TodayPage() {
  return (
    <>
      <PageHeader
        title="Today"
        description="What needs your attention, what's coming up, and what's happening."
      />
      <div className="grid gap-6 lg:grid-cols-2">
        {SECTIONS.map((section) => (
          <section key={section.title}>
            <h2 className="mb-3 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              {section.title}
            </h2>
            <EmptyState
              icon={section.icon}
              title={section.emptyTitle}
              description={section.emptyDescription}
            />
          </section>
        ))}
      </div>
    </>
  );
}
