"use client";

import { useEffect, useMemo, useState } from "react";

type FileItem = { id: number; name: string; url: string; category: string; type: string; size: string; updated: string; color: string; favorite?: boolean };
type FileResponse = { id: number; category_id: number; url: string; size: number };
type CategoryResponse = { id: number; name: string };

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes;
  let unit = -1;
  do { value /= 1024; unit += 1; } while (value >= 1024 && unit < units.length - 1);
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unit]}`;
}

function fileType(url: string) {
  const extension = url.split("?")[0].split(".").pop();
  return extension ? extension.toUpperCase().slice(0, 4) : "FILE";
}

function fileColor(type: string) {
  if (["PDF", "TXT"].includes(type)) return "red";
  if (["FIG", "SVG", "PSD"].includes(type)) return "orange";
  if (["XLS", "CSV"].includes(type)) return "green";
  if (["MP4", "MOV", "MP3"].includes(type)) return "purple";
  return "blue";
}

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    folder: <><path d="M3 7.5h18l-1.4 11a2 2 0 0 1-2 1.7H5.4a2 2 0 0 1-2-1.7L2 7.5Z"/><path d="M3 7.5V5a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v.5"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>, star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/>,
    trash: <><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></>, settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.5 1.5-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-2.1v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.5-1.5.1-.1A1.7 1.7 0 0 0 9 15a1.7 1.7 0 0 0-1.6-1H7.2v-2.1h.2A1.7 1.7 0 0 0 9 11a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.5-1.5.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h2.1v.2a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.5 1.5-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2V14h-.2a1.7 1.7 0 0 0-1.5 1Z"/></>, search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></>, upload: <><path d="M12 16V3m0 0L7 8m5-5 5 5"/><path d="M4 14v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></>, more: <><circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/></>, list: <><path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/></>, chevron: <path d="m9 18 6-6-6-6"/>, close: <><path d="m6 6 12 12M18 6 6 18"/></>, plus: <><path d="M12 5v14M5 12h14"/></>, download: <><path d="M12 3v13m0 0 5-5m-5 5-5-5M4 20h16"/></>
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

export default function Home() {
  const [active, setActive] = useState("All files");
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [fileItems, setFileItems] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState<FileItem | null>(null);
  const [toast, setToast] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const filesResponse = await fetch(`${API_BASE_URL}/files`);
        if (!filesResponse.ok) throw new Error(`Files API returned ${filesResponse.status}`);
        const apiFiles: FileResponse[] = await filesResponse.json();
        let categories: CategoryResponse[] = [];
        try {
          const categoriesResponse = await fetch(`${API_BASE_URL}/file-categories`);
          if (categoriesResponse.ok) categories = await categoriesResponse.json();
        } catch {
          // Category labels are optional; file loading should still succeed.
        }
        const categoryNames = new Map(categories.map(category => [category.id, category.name]));
        setFileItems(apiFiles.map(file => {
          const name = file.url.split("?")[0].split("/").pop() || file.url;
          const type = fileType(file.url);
          return {
            id: file.id,
            name,
            url: file.url,
            category: categoryNames.get(file.category_id) ?? `Category ${file.category_id}`,
            type,
            size: formatSize(file.size),
            updated: "Recently added",
            color: fileColor(type),
          };
        }));
      } catch {
        setToast(`Could not connect to the file API at ${API_BASE_URL}`);
      } finally {
        setIsLoading(false);
      }
    };
    void loadFiles();
  }, []);
  const filtered = useMemo(() => fileItems.filter(file => (active === "All files" || file.category === active || (active === "Favorites" && file.favorite)) && file.name.toLowerCase().includes(query.toLowerCase())), [active, fileItems, query]);
  const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2600); };
  const nav = [{ icon: "grid", label: "All files", count: "128" }, { icon: "clock", label: "Recent", count: "" }, { icon: "star", label: "Favorites", count: "12" }, { icon: "trash", label: "Trash", count: "3" }];
  const cats = [{ name: "Design", count: 42, color: "orange" }, { name: "Marketing", count: 26, color: "purple" }, { name: "Finance", count: 18, color: "green" }, { name: "Media", count: 31, color: "blue" }];
  return <main className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">V</span><span>vault</span></div><div className="workspace"><div className="avatar">AS</div><div><strong>Acme Studio</strong><small>Personal workspace</small></div><span className="workspace-chevron">⌄</span></div>
      <nav className="nav-list">{nav.map(item => <button className={`nav-item ${active === item.label ? "active" : ""}`} key={item.label} onClick={() => setActive(item.label)}><Icon name={item.icon}/><span>{item.label}</span>{item.count && <em>{item.count}</em>}</button>)}</nav>
      <div className="section-label">Folders <button onClick={() => notify("Folder creation coming soon")}>+</button></div><div className="folder-list">{cats.map(cat => <button key={cat.name} onClick={() => setActive(cat.name)} className={active === cat.name ? "selected-folder" : ""}><span className={`folder-dot ${cat.color}`}><Icon name="folder" size={14}/></span><span>{cat.name}</span><em>{cat.count}</em></button>)}</div>
      <div className="sidebar-bottom"><button className="nav-item"><Icon name="settings"/><span>Settings</span></button><div className="storage"><div className="storage-label"><span>Storage</span><strong>68%</strong></div><div className="progress"><i/></div><small>6.8 GB of 10 GB used</small><button className="upgrade" onClick={() => notify("Upgrade options opened")}>Upgrade storage <Icon name="chevron" size={14}/></button></div><div className="profile"><div className="avatar profile-avatar">AS</div><span><strong>Alex Smith</strong><small>alex@acme.studio</small></span><Icon name="more" size={19}/></div></div>
    </aside>
    <section className="content"><header className="topbar"><div className="breadcrumbs"><span>Workspace</span><Icon name="chevron" size={14}/><strong>{active === "All files" ? "All files" : active}</strong></div><div className="top-actions"><label className="search"><Icon name="search" size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search files..."/><kbd>⌘ K</kbd></label><button className="icon-button"><Icon name="settings" size={19}/></button><button className="help">?</button><button className="user-avatar">AS</button></div></header>
      <div className="page"><div className="page-heading"><div><p className="eyebrow">{active === "All files" ? "OVERVIEW" : "FOLDER"}</p><h1>{active === "All files" ? "All files" : active}</h1><p className="subtitle">{active === "All files" ? "Everything in your workspace, in one place." : `${filtered.length} files in this folder.`}</p></div><button className="upload-button" onClick={() => setShowUpload(true)}><Icon name="upload" size={17}/> Upload files</button></div>
        <div className="stats"><div><span className="stat-icon blue-bg"><Icon name="folder"/></span><span><small>Total files</small><strong>128 <i>+12%</i></strong></span></div><div><span className="stat-icon purple-bg"><Icon name="upload"/></span><span><small>Storage used</small><strong>6.8 GB <i>+4.2%</i></strong></span></div><div><span className="stat-icon orange-bg"><Icon name="clock"/></span><span><small>Added this month</small><strong>24 <i>+18%</i></strong></span></div><div><span className="stat-icon green-bg"><Icon name="star"/></span><span><small>Favorites</small><strong>12</strong></span></div></div>
        <div className="toolbar"><div><h2>{active === "All files" ? "Recent files" : `${active} files`}</h2><span>{filtered.length} items</span></div><div className="toolbar-actions"><select aria-label="Sort files"><option>Last modified</option><option>Name</option><option>Size</option></select><div className="view-toggle"><button className={view === "grid" ? "on" : ""} onClick={() => setView("grid")}><Icon name="grid" size={16}/></button><button className={view === "list" ? "on" : ""} onClick={() => setView("list")}><Icon name="list" size={17}/></button></div></div></div>
        <div className={`file-area ${view}`}>
          {isLoading ? <div className="empty-state"><strong>Loading files...</strong><small>Fetching files from the backend.</small></div> : filtered.map(file => <button className="file-card" key={file.id} onClick={() => setSelected(file)}><div className={`file-preview ${file.color}`}><span className="file-extension">{file.type}</span><span className="preview-lines"><i/><i/><i/></span>{file.favorite && <span className="favorite"><Icon name="star" size={14}/></span>}</div><div className="file-meta"><strong>{file.name}</strong><span>{file.category}<b>•</b>{file.size}<b>•</b>{file.updated}</span></div><span className="card-more"><Icon name="more" size={19}/></span></button>)}
          {!isLoading && <button className="add-card" onClick={() => setShowUpload(true)}><span><Icon name="plus" size={22}/></span><strong>Add new file</strong><small>Upload from your device</small></button>}
        </div>
      </div>
    </section>
    {selected && <div className="overlay" onClick={() => setSelected(null)}><aside className="details" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setSelected(null)}><Icon name="close"/></button><div className={`detail-preview ${selected.color}`}><span>{selected.type}</span><span className="preview-lines"><i/><i/><i/></span></div><p className="eyebrow">FILE DETAILS</p><h2>{selected.name}</h2><p className="detail-location"><span className={`folder-dot ${selected.color}`}><Icon name="folder" size={12}/></span>{selected.category}</p><div className="detail-table"><div><span>Size</span><strong>{selected.size}</strong></div><div><span>Modified</span><strong>{selected.updated}</strong></div><div><span>Owner</span><strong>Alex Smith</strong></div><div><span>File type</span><strong>{selected.type} file</strong></div></div><button className="download" onClick={() => notify("Download started")}><Icon name="download" size={16}/> Download file</button><button className="danger" onClick={() => { setSelected(null); notify("File moved to trash"); }}><Icon name="trash" size={16}/> Move to trash</button></aside></div>}
    {showUpload && <div className="overlay" onClick={() => setShowUpload(false)}><div className="upload-modal" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setShowUpload(false)}><Icon name="close"/></button><div className="upload-icon"><Icon name="upload" size={22}/></div><h2>Upload files</h2><p>Drag and drop files here, or click to browse.</p><button className="browse" onClick={() => notify("File picker opened")}>Choose files</button><small>Maximum file size: 250 MB</small></div></div>}
    {toast && <div className="toast">{toast}</div>}
  </main>;
}
