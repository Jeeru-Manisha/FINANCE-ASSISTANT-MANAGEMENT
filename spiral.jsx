import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Play,
  Pause,
  RotateCcw,
  SkipBack,
  RefreshCcw
} from "lucide-react";

const ROWS = 5;
const COLS = 5;
const SPEED = 350;

const SpiralMatrix = () => {
  const [grid, setGrid] = useState([]);
  const [path, setPath] = useState([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    initGrid();
    setPath(generateSpiralPath(ROWS, COLS));
  }, []);

  useEffect(() => {
    if (!isRunning || isPaused) return;
    if (stepIndex >= path.length) {
      setIsRunning(false);
      return;
    }

    const timer = setTimeout(() => {
      const { r, c } = path[stepIndex];
      setLogs((l) => [`Visiting [${r},${c}]`, ...l].slice(0, 3));
      setStepIndex((i) => i + 1);
    }, SPEED);

    return () => clearTimeout(timer);
  }, [stepIndex, isRunning, isPaused]);

  const initGrid = () => {
    setGrid(
      Array.from({ length: ROWS }, (_, r) =>
        Array.from({ length: COLS }, (_, c) => ({
          val: r * COLS + c + 1,
          row: r,
          col: c
        }))
      )
    );
    setStepIndex(0);
    setLogs([]);
    setIsRunning(false);
    setIsPaused(false);
  };

  const start = () => {
    if (stepIndex === path.length) return;
    setIsRunning(true);
    setIsPaused(false);
  };

  const pauseResume = () => {
    if (!isRunning) return;
    setIsPaused((p) => !p);
  };

  const replay = () => {
    setStepIndex(0);
    setLogs([]);
    setIsRunning(true);
    setIsPaused(false);
  };

  const backStep = () => {
    if (stepIndex === 0) return;
    setIsPaused(true);
    setStepIndex((i) => i - 1);
    setLogs((l) => l.slice(1));
  };

  const visitedSet = new Set(
    path.slice(0, stepIndex).map((p) => `${p.r}-${p.c}`)
  );

  const activeCell = path[stepIndex];

  return (
    <div className="flex flex-col items-center gap-6 p-6 bg-slate-900 rounded-xl w-full max-w-3xl border border-slate-700">
      <h2 className="text-2xl font-semibold text-slate-100">
        Spiral Matrix Traversal
      </h2>

      {/* Controls */}
      <div className="flex flex-wrap gap-3">
        <ControlBtn icon={<Play size={16} />} label="Start" onClick={start} />
        <ControlBtn
          icon={isPaused ? <Play size={16} /> : <Pause size={16} />}
          label={isPaused ? "Resume" : "Pause"}
          onClick={pauseResume}
        />
        <ControlBtn
          icon={<SkipBack size={16} />}
          label="Back"
          onClick={backStep}
        />
        <ControlBtn
          icon={<RefreshCcw size={16} />}
          label="Replay"
          onClick={replay}
        />
        <ControlBtn
          icon={<RotateCcw size={16} />}
          label="Reset"
          onClick={initGrid}
        />
      </div>

      {/* Grid */}
      <div className="grid grid-cols-5 gap-2 p-4 bg-slate-800 rounded-xl border border-slate-700">
        {grid.map((row, r) =>
          row.map((cell, c) => {
            const visited = visitedSet.has(`${r}-${c}`);
            const active = activeCell?.r === r && activeCell?.c === c;

            return (
              <motion.div
                key={`${r}-${c}`}
                animate={{
                  scale: active ? 1.12 : 1,
                  backgroundColor: active
                    ? "#6366F1" // Indigo
                    : visited
                    ? "#334155" // Slate
                    : "#1E293B",
                  borderColor: active ? "#818CF8" : "#475569",
                  color: visited || active ? "#F8FAFC" : "#94A3B8"
                }}
                className="w-12 h-12 flex items-center justify-center border rounded-md font-semibold"
              >
                {cell.val}
              </motion.div>
            );
          })
        )}
      </div>

      {/* Logs */}
      <div className="h-20 w-full max-w-sm bg-black/40 rounded-md p-2 font-mono text-xs text-indigo-300 border border-slate-700">
        {logs.map((log, i) => (
          <div key={i}>> {log}</div>
        ))}
      </div>
    </div>
  );
};

/* ---------- Helpers ---------- */

const ControlBtn = ({ icon, label, onClick }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-md text-sm font-medium transition"
  >
    {icon} {label}
  </button>
);

const generateSpiralPath = (rows, cols) => {
  const res = [];
  let top = 0,
    bottom = rows - 1,
    left = 0,
    right = cols - 1;

  while (top <= bottom && left <= right) {
    for (let c = left; c <= right; c++) res.push({ r: top, c });
    top++;
    for (let r = top; r <= bottom; r++) res.push({ r, c: right });
    right--;
    if (top <= bottom)
      for (let c = right; c >= left; c--) res.push({ r: bottom, c });
    bottom--;
    if (left <= right)
      for (let r = bottom; r >= top; r--) res.push({ r, c: left });
    left++;
  }
  return res;
};

export default SpiralMatrix;
