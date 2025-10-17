import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Table from "../components/Table";
import { api } from "../api";

export default function Attendance(){
  const [rows,setRows] = useState([]);
  async function load(){
    try{
      const url = "/api/attendance?from="+new Date().toISOString().slice(0,10);
      const data = await api(url);
      setRows((data.items||[]).map(a=>[
        a.student_id, a.full_name||"-", new Date(a.recognized_at).toLocaleString(), a.device_id
      ]));
    }catch(e){ alert(e.message); }
  }
  useEffect(()=>{ load(); },[]);
  return (
    <Card title="Attendance logs (today)">
      <Table heads={["MSSV","Name","Time","Device"]} rows={rows}/>
      <div className="mt-3 text-sm text-slate-500">Reload trang de cap nhat log moi.</div>
    </Card>
  );
}
