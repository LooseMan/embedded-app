import { Icon } from "./Icon";
import type { FileSetItem, FileSetResponse } from "./types";

type Props = {
  active: string;
  setActive: (value: string) => void;
  fileSets: FileSetItem[];
  selectedFileSet?: FileSetResponse;
  activeFileSetId: number | null;
  setActiveFileSetId: (value: number | null) => void;
  notify: (message: string) => void;
};

export function Sidebar({ active, setActive, fileSets, selectedFileSet, activeFileSetId, setActiveFileSetId, notify }: Props) {
  const nav = [{ icon: "grid", label: "Files", count: "128" }, { icon: "clock", label: "Recent", count: "" }, { icon: "star", label: "Favorites", count: "12" }, { icon: "trash", label: "Trash", count: "3" }];
  return <aside className="sidebar"><div className="brand"><span className="brand-mark">V</span><span>vault</span></div><div className="workspace"><div className="avatar">FS</div><div><strong>{selectedFileSet?.name ?? "All files"}</strong><small>{selectedFileSet ? "File set" : "All files"}</small></div><span className="workspace-chevron">⌄</span></div>
    <nav className="nav-list">{nav.map(item => <button className={`nav-item ${active === item.label ? "active" : ""}`} key={item.label} onClick={() => { setActive(item.label); if (item.label === "Files") setActiveFileSetId(null); }}><Icon name={item.icon}/><span>{item.label}</span>{item.count && <em>{item.count}</em>}</button>)}</nav>
    <div className="section-label">File sets <button onClick={() => notify("File set creation coming soon")}>+</button></div><div className="folder-list">{fileSets.map(fileSet => <button key={fileSet.id} onClick={() => { setActiveFileSetId(fileSet.id); setActive("File set"); }} className={activeFileSetId === fileSet.id ? "selected-folder" : ""}><span className={`folder-dot ${fileSet.color}`}><Icon name="folder" size={14}/></span><span>{fileSet.name}</span></button>)}</div>
    <div className="sidebar-bottom"><button className="nav-item"><Icon name="settings"/><span>Settings</span></button><div className="storage"><div className="storage-label"><span>Storage</span><strong>68%</strong></div><div className="progress"><i/></div><small>6.8 GB of 10 GB used</small><button className="upgrade" onClick={() => notify("Upgrade options opened")}>Upgrade storage <Icon name="chevron" size={14}/></button></div><div className="profile"><div className="avatar profile-avatar">AS</div><span><strong>Alex Smith</strong><small>alex@acme.studio</small></span><Icon name="more" size={19}/></div></div>
  </aside>;
}
