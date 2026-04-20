"use client";
import { useEffect, useState } from "react";
import { Activity } from "lucide-react";

export function Navbar() {
  const [visible, setVisible] = useState(false);

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

  return (
    <nav
      aria-label="Main navigation"
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-zinc-950/80 border-b border-zinc-800/50"
      style={{
        transform: visible ? "translateY(0)" : "translateY(-100%)",
        opacity: visible ? 1 : 0,
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
          <a href="#benchmarks" className="hover:text-white transition-colors">
            Benchmarks
          </a>
          <a href="#pipeline" className="hover:text-white transition-colors">
            Pipeline
          </a>
          <a href="#calibration" className="hover:text-white transition-colors">
            Calibration
          </a>
          <a href="#shift" className="hover:text-white transition-colors">
            Shift Analysis
          </a>
          <a href="#cli" className="hover:text-white transition-colors">
            CLI
          </a>
        </div>
        <a
          href="https://github.com/calebnewtonusc/signallab"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
        >
          GitHub
        </a>
      </div>
    </nav>
  );
}
