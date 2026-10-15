import { Icon } from "./Icon";
import { FileDetailsModal, UploadModal } from "./FileModals";
import { FileGrid } from "./FileGrid";
import { Sidebar } from "./Sidebar";
import type { CategoryResponse, FileItem, FileSetItem, FileSetResponse } from "./types";

type Props = {
  active: string;
  setActive: (value: string) => void;
  query: string;
  setQuery: (value: string) => void;
  view: "grid" | "list";
  setView: (value: "grid" | "list") => void;
  filtered: FileItem[];
  categories: CategoryResponse[];
  fileSets: FileSetItem[];
  selectedFileSet?: FileSetResponse;
  activeFileSetId: number | null;
  setActiveFileSetId: (value: number | null) => void;
  activeCategoryId: number | null;
  setActiveCategoryId: (value: number | null) => void;
  isLoading: boolean;
  selected: FileItem | null;
  setSelected: (value: FileItem | null) => void;
  showUpload: boolean;
  setShowUpload: (value: boolean) => void;
  notify: (message: string) => void;
  toast: string;
};

export function FileManagerView({
  active, setActive, query, setQuery, view, setView, filtered, categories,
  fileSets, selectedFileSet, activeFileSetId, setActiveFileSetId, activeCategoryId,
  setActiveCategoryId, isLoading, selected, setSelected, showUpload, setShowUpload,
  notify, toast,
}: Props) {
  return <main className="app-shell">
    <Sidebar active={active} setActive={setActive} fileSets={fileSets} selectedFileSet={selectedFileSet} activeFileSetId={activeFileSetId} setActiveFileSetId={setActiveFileSetId} notify={notify} />
    <section className="content"><header className="topbar"><div className="breadcrumbs"><span>{selectedFileSet ? "File set" : "Files"}</span><Icon name="chevron" size={14}/><strong>{selectedFileSet?.name ?? "Files"}</strong></div><div className="top-actions"><label className="search"><Icon name="search" size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search files..."/><kbd>⌘ K</kbd></label><button className="icon-button"><Icon name="settings" size={19}/></button><button className="help">?</button><button className="user-avatar">AS</button></div></header>
      <div className="page"><div className="page-heading"><div><p className="eyebrow">{selectedFileSet ? "FILE SET" : "FILES"}</p><h1>{selectedFileSet?.name ?? "Files"}</h1><p className="subtitle">{selectedFileSet ? `${filtered.length} files in this file set.` : "All files from every file set."}</p></div><button className="upload-button" onClick={() => setShowUpload(true)}><Icon name="upload" size={17}/> Upload files</button></div>
        <div className="stats"><div><span className="stat-icon blue-bg"><Icon name="folder"/></span><span><small>Total files</small><strong>128 <i>+12%</i></strong></span></div><div><span className="stat-icon purple-bg"><Icon name="upload"/></span><span><small>Storage used</small><strong>6.8 GB <i>+4.2%</i></strong></span></div><div><span className="stat-icon orange-bg"><Icon name="clock"/></span><span><small>Added this month</small><strong>24 <i>+18%</i></strong></span></div><div><span className="stat-icon green-bg"><Icon name="star"/></span><span><small>Favorites</small><strong>12</strong></span></div></div>
        <div className="toolbar"><div><h2>{selectedFileSet?.name ?? "Files"}</h2><span>{filtered.length} items</span></div><div className="toolbar-actions"><select aria-label="Filter by file category" value={activeCategoryId ?? "all"} onChange={e => setActiveCategoryId(e.target.value === "all" ? null : Number(e.target.value))}><option value="all">All categories</option>{categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select><select aria-label="Sort files"><option>Last modified</option><option>Name</option><option>Size</option></select><div className="view-toggle"><button className={view === "grid" ? "on" : ""} onClick={() => setView("grid")}><Icon name="grid" size={16}/></button><button className={view === "list" ? "on" : ""} onClick={() => setView("list")}><Icon name="list" size={17}/></button></div></div></div>
        <FileGrid view={view} filtered={filtered} isLoading={isLoading} setSelected={setSelected} onAddFile={() => setShowUpload(true)} />
      </div>
    </section>
    {selected && <FileDetailsModal file={selected} setFile={setSelected} notify={notify} />}
    {showUpload && <UploadModal setOpen={setShowUpload} notify={notify} />}
    {toast && <div className="toast">{toast}</div>}
  </main>;
}
