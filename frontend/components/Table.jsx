import React from "react";
export default function Table({heads=[],rows=[]}){
  return (
    <div className="overflow-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-100 text-slate-700">
          <tr>{heads.map((h,i)=>(<th key={i} className="px-4 py-2 text-left font-semibold">{h}</th>))}</tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((r,ri)=>(
            <tr key={ri} className="hover:bg-slate-50">
              {r.map((c,ci)=>(<td key={ci} className="px-4 py-2">{c}</td>))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
