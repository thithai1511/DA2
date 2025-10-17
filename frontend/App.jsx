import React from "react";
import { Outlet } from "react-router-dom";
import Topbar from "./components/Topbar";
export default function App(){
  return (
    <div className="min-h-screen bg-slate-50">
      <Topbar />
      <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <Outlet />
      </main>
    </div>
  );
}
