import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./index.css";

import App from "./App.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Students from "./pages/Students.jsx";
import Capture from "./pages/Capture.jsx";
import Train from "./pages/Train.jsx";
import Attendance from "./pages/Attendance.jsx";

createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="students" element={<Students />} />
        <Route path="capture" element={<Capture />} />
        <Route path="train" element={<Train />} />
        <Route path="attendance" element={<Attendance />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
