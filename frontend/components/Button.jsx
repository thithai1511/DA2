import React from "react";
export default function Button({children,className="",...props}){
  return (
    <button
      className={"inline-flex items-center justify-center rounded-xl px-4 py-2 text-white bg-slate-900 hover:bg-slate-800 active:bg-slate-950 transition " + className}
      {...props}
    >
      {children}
    </button>
  );
}
