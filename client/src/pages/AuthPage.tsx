import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, auth } from "../api";

export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const isLogin = mode === "login";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (!isLogin) await api.register(email, password);
      const { access_token } = await api.login(email, password);
      auth.set(access_token);
      navigate("/notes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h1>{isLogin ? "Connexion" : "Créer un compte"}</h1>
      <form onSubmit={onSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input
          type="password"
          placeholder="Mot de passe (8 caractères min.)"
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button disabled={loading}>{loading ? "…" : isLogin ? "Se connecter" : "S'inscrire"}</button>
      </form>
      {error && <p className="error">{error}</p>}
      <p className="muted">
        {isLogin ? (
          <>
            Pas de compte ? <Link to="/register">Inscription</Link>
          </>
        ) : (
          <>
            Déjà inscrit ? <Link to="/login">Connexion</Link>
          </>
        )}
      </p>
    </section>
  );
}
