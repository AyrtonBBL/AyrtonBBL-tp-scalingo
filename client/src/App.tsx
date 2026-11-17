import type { ReactNode } from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import { auth } from "./api";
import AuthPage from "./pages/AuthPage";
import NotesPage from "./pages/NotesPage";

function Protected({ children }: { children: ReactNode }) {
  return auth.get() ? children : <Navigate to="/connexion" replace />;
}

export default function App() {
  return (
    <main className="container">
      <Routes>
        <Route path="/" element={<Navigate to="/mes-notes" replace />} />
        <Route path="/connexion" element={<AuthPage mode="login" />} />
        <Route path="/inscription" element={<AuthPage mode="register" />} />
        <Route
          path="/mes-notes"
          element={
            <Protected>
              <NotesPage />
            </Protected>
          }
        />
        <Route
          path="*"
          element={
            <p>
              Page introuvable. <Link to="/">Retour</Link>
            </p>
          }
        />
      </Routes>
    </main>
  );
}
