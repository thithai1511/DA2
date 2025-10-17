import React from "react";
import Card from "../components/Card";
import Button from "../components/Button";
import { API_BASE } from "../api";
export default function Dashboard(){
  return (
    <div className="grid md:grid-cols-2 gap-5">
      <Card title="Quick actions">
        <div className="flex flex-wrap gap-3">
          <a href="/capture"><Button>Enroll / Capture</Button></a>
          <a href="/train"><Button className="bg-slate-700 hover:bg-slate-600">Train encodings</Button></a>
          <a href="/attendance"><Button className="bg-slate-600 hover:bg-slate-500">View attendance</Button></a>
        </div>
      </Card>
      <Card title="Live preview">
        <div className="aspect-video w-full overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
          <img src={`${API_BASE}/api/stream`} alt="camera" className="w-full h-full object-cover"/>
        </div>
      </Card>
    </div>
  );
}
