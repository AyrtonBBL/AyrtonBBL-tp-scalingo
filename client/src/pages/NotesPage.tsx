import { type FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, api, auth, type Note } from "../api";

export default function NotesPage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleError(err: unknown) {
    if (err instanceof ApiError && err.status === 401) {
      auth.clear();
      navigate("/login");
      return;
    }
    setError(err instanceof Error ? err.message : "Erreur inconnue");
  }

  useEffect(() => {
    api.listNotes().then(setNotes).catch(handleError);
  }, []);

  async function onAdd(e: FormEvent) {
    e.preventDefault();
    try {
      const note = await api.createNote(title, content);
      setNotes((n) => [note, ...n]);
      setTitle("");
      setContent("");
    } catch (err) {
      handleError(err);
    }
  }

  async function onDelete(id: number) {
    try {
      await api.deleteNote(id);
      setNotes((n) => n.filter((x) => x.id !== id));
    } catch (err) {
      handleError(err);
    }
  }

  function logout() {
    auth.clear();
    navigate("/login");
  }

  return (
    <section>
      <header className="row">
        <h1>Mes notes</h1>
        <button className="ghost" onClick={logout}>
          Déconnexion
        </button>
      </header>
      <form className="card" onSubmit={onAdd}>
        <input placeholder="Titre" value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={200} />
        <textarea placeholder="Contenu" value={content} onChange={(e) => setContent(e.target.value)} rows={3} />
        <button>Ajouter</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="notes">
        {notes.map((n) => (
          <li key={n.id} className="card">
            <div className="row">
              <strong>{n.title}</strong>
              <button className="ghost" onClick={() => onDelete(n.id)} aria-label={`Supprimer ${n.title}`}>
                ✕
              </button>
            </div>
            {n.content && <p>{n.content}</p>}
          </li>
        ))}
        {notes.length === 0 && <p className="muted">Aucune note pour l'instant.</p>}
      </ul>
    </section>
  );
}
