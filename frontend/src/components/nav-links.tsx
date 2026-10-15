"use client";

import { CalendarDays, Inbox, Newspaper, Search, Sun } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Today", icon: Sun },
  { href: "/inbox", label: "Inbox", icon: Inbox },
  { href: "/calendar", label: "Calendar", icon: CalendarDays },
  { href: "/news", label: "News", icon: Newspaper },
  { href: "/search", label: "Search", icon: Search },
];

// A section stays active on its sub-pages, e.g. /inbox and /inbox/123.
function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav aria-label="Main">
      <ul className="flex gap-1 overflow-x-auto px-2 pb-2 md:flex-col md:px-3">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
          <li key={href}>
            <Link
              href={href}
              aria-current={isActive(pathname, href) ? "page" : undefined}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm whitespace-nowrap text-zinc-600 transition-colors hover:bg-zinc-200/60 hover:text-zinc-900 aria-[current=page]:bg-white aria-[current=page]:font-medium aria-[current=page]:text-zinc-900 aria-[current=page]:shadow-sm dark:text-zinc-400 dark:hover:bg-zinc-800/60 dark:hover:text-zinc-100 dark:aria-[current=page]:bg-zinc-800 dark:aria-[current=page]:text-zinc-100"
            >
              <Icon aria-hidden className="size-4" />
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
