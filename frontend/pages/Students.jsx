import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Table from "../components/Table";
import Button from "../components/Button";
import { api } from "../api";

export default function Students(){
  const [rows,setRows] = useState([]);
  const [form,setForm] = useState({student_id:"",full_name:"",class_name:"",email:""});

  async function load(){
    try{
      const data = await api("/api/students");
      setRows((data.items||[]).map(s=>[s.student_id,s.full_name,s.class_name||"-",s.email||"-"]));
    }catch(e){ alert(e.message); }
  }
  useEffect(()=>{ load(); },[]);

  async function submit(e){
    e.preventDefault();
    try{
      await api("/api/students",{method:"POST", body: JSON.stringify(form)});
      setForm({student_id:"",full_name:"",class_name:"",email:""});
      load();
    }catch(e){ alert(e.message); }
  }

  return (
    <div className="grid gap-5">
      <Card title="Add student">
        <form className="grid md:grid-cols-4 gap-3 items-start" onSubmit={submit}>
          <input className="border rounded-xl px-3 py-2" placeholder="MSSV" value={form.student_id} onChange={e=>setForm({...form,student_id:e.target.value})} required/>
          <input className="border rounded-xl px-3 py-2" placeholder="Full name" value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})} required/>
          <input className="border rounded-xl px-3 py-2" placeholder="Class" value={form.class_name} onChange={e=>setForm({...form,class_name:e.target.value})}/>
          <input className="border rounded-xl px-3 py-2" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
          <div className="md:col-span-4"><Button type="submit">Save</Button></div>
        </form>
      </Card>

      <Card title="Students list">
        <Table heads={["MSSV","Name","Class","Email"]} rows={rows}/>
      </Card>
    </div>
  );
}
