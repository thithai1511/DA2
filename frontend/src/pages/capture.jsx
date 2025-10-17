import React, { useState } from "react";
import Card from "../components/Card";
import Button from "../components/Button";
import { api } from "../api";

export default function Capture(){
  const [sid,setSid] = useState("");
  const [running,setRunning] = useState(false);

  async function start(){
    if(!sid) return alert("Nhap MSSV truoc");
    setRunning(true);
    try{
      await api("/api/capture",{method:"POST", body: JSON.stringify({student_id:sid})});
      alert("Da gui lenh capture (dang chay background).");
    }catch(e){
      alert(e.message);
    }finally{
      setRunning(false);
    }
  }

  return (
    <Card title="Enroll / Capture faces">
      <div className="grid md:grid-cols-[1fr_auto] gap-3 items-end">
        <div className="grid gap-2">
          <label className="text-sm text-slate-600">Student ID (MSSV)</label>
          <input className="border rounded-xl px-3 py-2" placeholder="22520123" value={sid} onChange={e=>setSid(e.target.value)} />
        </div>
        <Button onClick={start} disabled={running}>{running? "Starting..." : "Start capture"}</Button>
      </div>
      <p className="text-sm text-slate-500 mt-3">Neu preview xuat hien tren Pi, bam q de dung som (neu chay bang CLI).</p>
    </Card>
  );
}
