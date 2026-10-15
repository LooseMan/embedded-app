import { Icon } from "./Icon";
import type { FileItem } from "./types";

export function FileDetailsModal({ file, setFile, notify }: { file: FileItem; setFile: (value: FileItem | null) => void; notify: (message: string) => void }) {
  return <div className="overlay" onClick={() => setFile(null)}><aside className="details" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setFile(null)}><Icon name="close"/></button><div className={`detail-preview ${file.color}`}><span>{file.type}</span><span className="preview-lines"><i/><i/><i/></span></div><p className="eyebrow">FILE DETAILS</p><h2>{file.name}</h2><p className="detail-location"><span className={`folder-dot ${file.color}`}><Icon name="folder" size={12}/></span>{file.category}</p><div className="detail-table"><div><span>Size</span><strong>{file.size}</strong></div><div><span>Modified</span><strong>{file.updated}</strong></div><div><span>Owner</span><strong>Alex Smith</strong></div><div><span>File type</span><strong>{file.type} file</strong></div></div><button className="download" onClick={() => notify("Download started")}><Icon name="download" size={16}/> Download file</button><button className="danger" onClick={() => { setFile(null); notify("File moved to trash"); }}><Icon name="trash" size={16}/> Move to trash</button></aside></div>;
}

export function UploadModal({ setOpen, notify }: { setOpen: (value: boolean) => void; notify: (message: string) => void }) {
  return <div className="overlay" onClick={() => setOpen(false)}><div className="upload-modal" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setOpen(false)}><Icon name="close"/></button><div className="upload-icon"><Icon name="upload" size={22}/></div><h2>Upload files</h2><p>Drag and drop files here, or click to browse.</p><button className="browse" onClick={() => notify("File picker opened")}>Choose files</button><small>Maximum file size: 250 MB</small></div></div>;
}
