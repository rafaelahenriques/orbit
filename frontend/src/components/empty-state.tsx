import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type EmptyStateProps = {
  icon: LucideIcon;
  title: string;
  description: string;
  /** What to do next, e.g. a button. */
  action?: ReactNode;
};

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-zinc-300 px-6 py-10 text-center dark:border-zinc-700">
      <Icon aria-hidden className="size-6 text-zinc-400 dark:text-zinc-500" />
      <p className="mt-3 text-sm font-medium">{title}</p>
      <p className="mt-1 max-w-sm text-sm text-zinc-600 dark:text-zinc-400">
        {description}
      </p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

/** Holds the space of an empty state while its content loads. */
export function EmptyStateSkeleton() {
  return (
    <div
      role="status"
      className="h-48 animate-pulse rounded-xl border border-dashed border-zinc-300 bg-zinc-100/60 dark:border-zinc-700 dark:bg-zinc-900/60"
    >
      <span className="sr-only">Loading…</span>
    </div>
  );
}
