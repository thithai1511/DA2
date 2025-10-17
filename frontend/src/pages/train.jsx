import React, { useState } from "react";
import Card from "../components/Card";
import Button from "../components/Button";
import { api } from "../api";

export default function Train(){
  const [msg,setMsg] = useState("");
  const [running,setRunning] = useState(false);
  async function run(){
    setRunning(true);
    try{ const res = await api("/api/train",{method:"POST"}); setMsg(res.ok? "Queued train" : JSON.stringify(res)); }
    catch(e){ setMsg(String(e)); }
    finally{ setRunning(false); }
  }
  return (
    <Card title="Train encodings">
      <Button onClick={run} disabled={running}>{running? "Training..." : "Run training"}</Button>
      <div className="text-sm text-slate-600 mt-3">{msg}</div>
    </Card>
  );
}
