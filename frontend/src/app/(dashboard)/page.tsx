import { CalendarClock, Newspaper, Reply } from "lucide-react";

import { BriefingEmptyState } from "@/components/briefing-empty-state";
import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

const SECTIONS = [
  {
    title: "Briefing",
    // Asks people to connect Google until Orbit can read their email and calendar.
    content: <BriefingEmptyState />,
  },
  {
    title: "Needs a reply",
    content: (
      <EmptyState
        icon={Reply}
        title="Nothing waiting on you"
        description="Emails and messages that need your reply will show up here."
      />
    ),
  },
  {
    title: "Upcoming",
    content: (
      <EmptyState
        icon={CalendarClock}
        title="No upcoming events"
        description="Your next meetings and events from Google Calendar will show up here."
      />
    ),
  },
  {
    title: "Top news",
    content: (
      <EmptyState
        icon={Newspaper}
        title="No headlines yet"
        description="Stories from the sources you follow will show up here."
      />
    ),
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
            {section.content}
          </section>
        ))}
      </div>
    </>
  );
}
