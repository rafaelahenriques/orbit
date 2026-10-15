import { Orbit } from "lucide-react";
import Link from "next/link";

import { NavLinks } from "@/components/nav-links";
import { UserMenu } from "@/components/user-menu";

export function Sidebar() {
  return (
    // On mobile: a top bar with the user beside the logo and the nav below.
    // On desktop: a full-height column with the user at the bottom.
    <header className="grid grid-cols-[1fr_auto] items-center border-b border-zinc-200 bg-zinc-50 md:sticky md:top-0 md:flex md:h-dvh md:w-60 md:shrink-0 md:flex-col md:items-stretch md:border-r md:border-b-0 dark:border-zinc-800 dark:bg-zinc-900/40">
      <Link
        href="/"
        className="col-start-1 row-start-1 flex items-center gap-2 px-4 py-4 text-lg font-semibold tracking-tight md:px-5 md:py-6"
      >
        <Orbit
          aria-hidden
          className="size-5 text-indigo-600 dark:text-indigo-400"
        />
        Orbit
      </Link>
      <div className="col-span-2 row-start-2">
        <NavLinks />
      </div>
      <div className="col-start-2 row-start-1 px-4 md:mt-auto md:border-t md:border-zinc-200 md:px-4 md:py-4 md:dark:border-zinc-800">
        <UserMenu />
      </div>
    </header>
  );
}
