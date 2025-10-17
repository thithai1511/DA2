import React from "react";
export default function Card({title,children,footer}){
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200">
      {title && <div className="px-5 pt-5 text-lg font-semibold">{title}</div>}
      <div className="p-5">{children}</div>
      {footer && <div className="px-5 pb-5 text-sm text-slate-500">{footer}</div>}
    </div>
  );
}
