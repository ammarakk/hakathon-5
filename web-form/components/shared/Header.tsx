"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const path = usePathname();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-amber-500 rounded-xl flex items-center justify-center">
              <span className="text-white text-lg">🌹</span>
            </div>
            <div>
              <p className="font-bold text-gray-900 text-sm leading-none">
                Nur Scents
              </p>
              <p className="text-xs text-gray-400 leading-none mt-0.5">
                CRM System
              </p>
            </div>
          </div>

          <nav className="flex items-center gap-1">
            <Link
              href="/owner"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                path?.startsWith("/owner")
                  ? "bg-amber-50 text-amber-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              Owner Dashboard
            </Link>
            <Link
              href="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                path === "/"
                  ? "bg-amber-50 text-amber-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              Customer Portal
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
