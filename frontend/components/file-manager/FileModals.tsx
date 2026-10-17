import { useState } from "react";
import { Icon } from "./Icon";
import type { CategoryResponse, FileEditValues, FileItem } from "./types";

type FileModalProps = {
  file: FileItem;
  categories: CategoryResponse[];
  setFile: (file: FileItem | null) => void;
  notify: (message: string) => void;
  onUpdate: (file: FileItem, values: FileEditValues) => Promise<void>;
  onDelete: (file: FileItem) => Promise<void>;
};

export function FileDetailsModal({ file, categories, setFile, notify, onUpdate, onDelete }: FileModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  return <div className="overlay" onClick={() => setFile(null)}><aside className="details" onClick={event => event.stopPropagation()}><button className="close" onClick={() => setFile(null)}><Icon name="close" /></button><FilePreview file={file} />{isEditing ? <EditForm file={file} categories={categories} onCancel={() => setIsEditing(false)} onSave={async values => { await onUpdate(file, values); setFile(null); notify("File updated"); }} notify={notify} /> : <FileSummary file={file} onEdit={() => setIsEditing(true)} onDelete={async () => { await onDelete(file); setFile(null); notify("File deleted"); }} notify={notify} />}</aside></div>;
}

function FilePreview({ file }: { file: FileItem }) {
  return <div className={`detail-preview ${file.color}`}><span>{file.type}</span><span className="preview-lines"><i /><i /><i /></span></div>;
}

function FileSummary({ file, onEdit, onDelete, notify }: { file: FileItem; onEdit: () => void; onDelete: () => Promise<void>; notify: (message: string) => void }) {
  const [isDeleting, setIsDeleting] = useState(false);
  async function handleDelete() { if (!window.confirm(`Delete ${file.name}?`)) return; setIsDeleting(true); try { await onDelete(); } catch (error) { notify(error instanceof Error ? error.message : "Could not delete the file"); setIsDeleting(false); } }
  return <><p className="eyebrow">FILE DETAILS</p><h2>{file.name}</h2><p className="detail-location"><span className={`folder-dot ${file.color}`}><Icon name="folder" size={12} /></span>{file.category}</p><div className="detail-table"><DetailRow label="Size" value={file.size} /><DetailRow label="Modified" value={file.updated} /><DetailRow label="Owner" value="Alex Smith" /><DetailRow label="File type" value={`${file.type} file`} /></div><button className="download" onClick={() => notify("Download started")}><Icon name="download" size={16} /> Download file</button><button className="secondary full" onClick={onEdit}>Edit file</button><button className="danger" disabled={isDeleting} onClick={() => void handleDelete()}><Icon name="trash" size={16} />{isDeleting ? "Deleting..." : "Delete file"}</button></>;
}

function DetailRow({ label, value }: { label: string; value: string }) { return <div><span>{label}</span><strong>{value}</strong></div>; }

function EditForm({ file, categories, onCancel, onSave, notify }: { file: FileItem; categories: CategoryResponse[]; onCancel: () => void; onSave: (values: FileEditValues) => Promise<void>; notify: (message: string) => void }) {
  const [url, setUrl] = useState(file.url);
  const [size, setSize] = useState(String(parseSize(file.size)));
  const [categoryId, setCategoryId] = useState(String(file.categoryId));
  const [isSaving, setIsSaving] = useState(false);
  async function handleSave() { const parsedSize = Number(size); if (!url.trim() || !Number.isFinite(parsedSize) || parsedSize < 0 || !categoryId) { notify("Enter a valid file name, size, and category"); return; } setIsSaving(true); try { await onSave({ url: url.trim(), size: parsedSize, categoryId: Number(categoryId) }); } catch (error) { notify(error instanceof Error ? error.message : "Could not update the file"); setIsSaving(false); } }
  return <><p className="eyebrow">EDIT FILE</p><label className="form-field">File name or URL<input value={url} onChange={event => setUrl(event.target.value)} /></label><label className="form-field">Category<select value={categoryId} onChange={event => setCategoryId(event.target.value)}>{categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label><label className="form-field">Size in bytes<input type="number" min="0" value={size} onChange={event => setSize(event.target.value)} /></label><div className="form-actions"><button className="secondary" onClick={onCancel}>Cancel</button><button className="download" disabled={isSaving} onClick={() => void handleSave()}>{isSaving ? "Saving..." : "Save changes"}</button></div></>;
}

export function UploadModal({ categories, activeFileSetId, setOpen, notify, onUpload }: { categories: CategoryResponse[]; activeFileSetId: number | null; setOpen: (open: boolean) => void; notify: (message: string) => void; onUpload: (files: File[], categoryId: number, fileSetId: number | null) => Promise<void> }) {
  const [categoryId, setCategoryId] = useState(categories[0] ? String(categories[0].id) : "");
  const [isUploading, setIsUploading] = useState(false);
  async function handleSelect(files: FileList | null) { if (!files?.length) return; if (!categoryId) { notify("Create a file category before uploading"); return; } setIsUploading(true); try { await onUpload(Array.from(files), Number(categoryId), activeFileSetId); setOpen(false); notify(`${files.length} file${files.length === 1 ? "" : "s"} added`); } catch (error) { notify(error instanceof Error ? error.message : "Could not add the files"); setIsUploading(false); } }
  return <div className="overlay" onClick={() => setOpen(false)}><div className="upload-modal" onClick={event => event.stopPropagation()}><button className="close" onClick={() => setOpen(false)}><Icon name="close" /></button><div className="upload-icon"><Icon name="upload" size={22} /></div><h2>Upload files</h2><p>Choose one or more files to add to the workspace.</p><label className="form-field upload-category">Category<select value={categoryId} onChange={event => setCategoryId(event.target.value)}>{categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label><label className={`browse ${isUploading ? "disabled" : ""}`}>{isUploading ? "Adding files..." : "Choose files"}<input type="file" multiple disabled={isUploading} onChange={event => void handleSelect(event.target.files)} /></label><small>Maximum file size: 250 MB</small></div></div>;
}

function parseSize(value: string) { const match = value.match(/^([\d.]+)\s*(B|KB|MB|GB)$/i); if (!match) return 0; const units = { B: 0, KB: 1, MB: 2, GB: 3 } as const; return Math.round(Number(match[1]) * 1024 ** units[match[2].toUpperCase() as keyof typeof units]); }
