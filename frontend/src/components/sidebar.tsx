import { Orbit } from "lucide-react";
import Link from "next/link";

import { NavLinks } from "@/components/nav-links";

export function Sidebar() {
  return (
    <header className="border-b border-zinc-200 bg-zinc-50 md:w-60 md:shrink-0 md:border-r md:border-b-0 dark:border-zinc-800 dark:bg-zinc-900/40">
      <Link
        href="/"
        className="flex items-center gap-2 px-4 py-4 text-lg font-semibold tracking-tight md:px-5 md:py-6"
      >
        <Orbit
          aria-hidden
          className="size-5 text-indigo-600 dark:text-indigo-400"
        />
        Orbit
      </Link>
      <NavLinks />
    </header>
  );
}
