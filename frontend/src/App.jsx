import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Categorias } from "./pages/Categorias";
import { Comprovantes } from "./pages/Comprovantes";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { Produtos } from "./pages/Produtos";
import { Registro } from "./pages/Registro";
import { Relatorios } from "./pages/Relatorios";
import { Usuarios } from "./pages/Usuarios";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/produtos" element={<Produtos />} />
        <Route path="/comprovantes" element={<Comprovantes />} />
        <Route path="/categorias" element={<Categorias />} />
        <Route path="/relatorios" element={<Relatorios />} />
        <Route path="/usuarios" element={<Usuarios />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
