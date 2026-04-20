"use client";
import { useEffect, useState } from "react";
import { Activity, Menu, X } from "lucide-react";

const LINKS = [
  { href: "#benchmarks", label: "Benchmarks" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#calibration", label: "Calibration" },
  { href: "#shift", label: "Shift Analysis" },
  { href: "#cli", label: "CLI" },
];

export function Navbar() {
  const [visible, setVisible] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const docHeight = document.documentElement.scrollHeight;
      const winHeight = window.innerHeight;
      const nearBottom = scrollY + winHeight >= docHeight - 200;
      setVisible(scrollY > 80 && !nearBottom);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!open) return;
    const close = () => setOpen(false);
    window.addEventListener("resize", close);
    return () => window.removeEventListener("resize", close);
  }, [open]);

  return (
    <nav
      aria-label="Main navigation"
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-zinc-950/80 border-b border-zinc-800/50"
      style={{
        transform: visible || open ? "translateY(0)" : "translateY(-100%)",
        opacity: visible || open ? 1 : 0,
        transition: "transform 0.3s ease, opacity 0.3s ease",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2 text-zinc-100">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-400">
            <Activity className="w-4 h-4" aria-hidden="true" />
          </span>
          <span className="font-semibold tracking-tight text-sm">
            SignalLab
          </span>
        </a>
        <div className="hidden md:flex items-center gap-6 text-sm text-zinc-400">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="hover:text-white transition-colors focus:outline-none focus-visible:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <a
            href="https://github.com/calebnewtonusc/signallab"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
          >
            GitHub
          </a>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            aria-controls="mobile-nav"
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-200 hover:border-zinc-700 hover:bg-zinc-800 transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            {open ? (
              <X className="w-4 h-4" aria-hidden="true" />
            ) : (
              <Menu className="w-4 h-4" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>
      <div
        id="mobile-nav"
        hidden={!open}
        className="md:hidden border-t border-zinc-800/60 bg-zinc-950/95 backdrop-blur-md"
      >
        <div className="max-w-7xl mx-auto px-4 py-3 grid gap-1">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              {link.label}
            </a>
          ))}
          <a
            href="https://github.com/calebnewtonusc/signallab"
            target="_blank"
            rel="noreferrer"
            onClick={() => setOpen(false)}
            className="mt-1 block rounded-lg px-3 py-2 text-sm text-indigo-300 hover:bg-indigo-500/10 hover:text-indigo-200 transition-colors"
          >
            GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
