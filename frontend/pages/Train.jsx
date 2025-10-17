import React, { useState } from "react";
import Card from "../components/Card";
import Button from "../components/Button";
import { api } from "../api";

export default function Train(){
  const [out,setOut] = useState("");
  const [running,setRunning] = useState(false);

  async function run(){
    setRunning(true);
    try{ const res = await api("/api/train",{method:"POST"}); setOut(res.stdout||JSON.stringify(res)); }
    catch(e){ setOut(String(e)); }
    finally{ setRunning(false); }
  }

  return (
    <Card title="Train encodings">
      <Button onClick={run} disabled={running}>{running? "Training..." : "Run training"}</Button>
      <pre className="mt-4 bg-slate-900 text-slate-100 p-3 rounded-xl overflow-auto text-xs max-h-96">{out}</pre>
    </Card>
  );
}
