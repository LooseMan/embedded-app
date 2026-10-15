import { Icon } from "./Icon";
import type { FileItem } from "./types";

type Props = {
  view: "grid" | "list";
  filtered: FileItem[];
  isLoading: boolean;
  setSelected: (value: FileItem | null) => void;
  onAddFile: () => void;
};

export function FileGrid({ view, filtered, isLoading, setSelected, onAddFile }: Props) {
  return <div className={`file-area ${view}`}>
    {isLoading ? <div className="empty-state"><strong>Loading files...</strong><small>Fetching files from the backend.</small></div> : filtered.map(file => <button className="file-card" key={file.id} onClick={() => setSelected(file)}><div className={`file-preview ${file.color}`}><span className="file-extension">{file.type}</span><span className="preview-lines"><i/><i/><i/></span>{file.favorite && <span className="favorite"><Icon name="star" size={14}/></span>}</div><div className="file-meta"><strong>{file.name}</strong><span>{file.category}<b>•</b>{file.size}<b>•</b>{file.updated}</span></div><span className="card-more"><Icon name="more" size={19}/></span></button>)}
    {!isLoading && <button className="add-card" onClick={onAddFile}><span><Icon name="plus" size={22}/></span><strong>Add new file</strong><small>Upload from your device</small></button>}
  </div>;
}
