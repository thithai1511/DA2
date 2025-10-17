import React from "react";
import { NavLink } from "react-router-dom";
const linkCls = ({isActive}) =>
  "px-3 py-1.5 rounded-lg " + (isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-200");
export default function Topbar(){
  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-3">
        <div className="font-bold">Pi5 Face Attendance</div>
        <nav className="ml-auto flex gap-1">
          <NavLink to="/dashboard" className={linkCls}>Dashboard</NavLink>
          <NavLink to="/students" className={linkCls}>Students</NavLink>
          <NavLink to="/capture" className={linkCls}>Capture</NavLink>
          <NavLink to="/train" className={linkCls}>Train</NavLink>
          <NavLink to="/attendance" className={linkCls}>Attendance</NavLink>
        </nav>
      </div>
    </header>
  );
}
