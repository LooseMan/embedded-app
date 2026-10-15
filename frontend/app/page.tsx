"use client";

import { useEffect, useMemo, useState } from "react";
import { FileManagerView } from "../components/file-manager/FileManagerView";
import type { CategoryResponse, FileItem, FileResponse, FileSetItem, FileSetResponse } from "../components/file-manager/types";
import { API_BASE_URL, mapFiles } from "../components/file-manager/utils";

export default function Home() {
  const [active, setActive] = useState("Files");
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [fileItems, setFileItems] = useState<FileItem[]>([]);
  const [allFileItems, setAllFileItems] = useState<FileItem[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [fileSets, setFileSets] = useState<FileSetResponse[]>([]);
  const [activeFileSetId, setActiveFileSetId] = useState<number | null>(null);
  const [activeCategoryId, setActiveCategoryId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState<FileItem | null>(null);
  const [toast, setToast] = useState("");
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    const loadFiles = async () => {
      try {
        const [filesResponse, fileSetsResponse, categoriesResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/files`),
          fetch(`${API_BASE_URL}/file-sets`),
          fetch(`${API_BASE_URL}/file-categories`),
        ]);
        if (!filesResponse.ok) throw new Error(`Files API returned ${filesResponse.status}`);
        const apiFiles: FileResponse[] = await filesResponse.json();
        const apiFileSets: FileSetResponse[] = fileSetsResponse.ok ? await fileSetsResponse.json() : [];
        const apiCategories: CategoryResponse[] = categoriesResponse.ok ? await categoriesResponse.json() : [];
        const mappedFiles = mapFiles(apiFiles, apiCategories);
        setFileSets(apiFileSets);
        setCategories(apiCategories);
        setAllFileItems(mappedFiles);
        setFileItems(mappedFiles);
      } catch {
        setToast(`Could not connect to the file API at ${API_BASE_URL}`);
      } finally {
        setIsLoading(false);
      }
    };
    void loadFiles();
  }, []);

  useEffect(() => {
    if (activeFileSetId === null) {
      setFileItems(allFileItems);
      return;
    }
    const loadFileSet = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/file-sets/${activeFileSetId}/files`);
        if (!response.ok) throw new Error(`File set API returned ${response.status}`);
        const apiFiles: FileResponse[] = await response.json();
        setFileItems(mapFiles(apiFiles, categories));
      } catch {
        setToast(`Could not load the selected file set from ${API_BASE_URL}`);
      }
    };
    void loadFileSet();
  }, [activeFileSetId, allFileItems, categories]);

  const filtered = useMemo(
    () => fileItems.filter(file => (activeCategoryId === null || file.categoryId === activeCategoryId) && file.name.toLowerCase().includes(query.toLowerCase())),
    [activeCategoryId, fileItems, query],
  );
  const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2600); };
  const selectedFileSet = fileSets.find(fileSet => fileSet.id === activeFileSetId);
  const folderColors = ["orange", "purple", "green", "blue"];
  const setItems: FileSetItem[] = useMemo(() => fileSets.map((fileSet, index) => ({
    ...fileSet,
    color: folderColors[index % folderColors.length],
  })), [fileSets]);

  return <FileManagerView
    active={active}
    setActive={setActive}
    query={query}
    setQuery={setQuery}
    view={view}
    setView={setView}
    filtered={filtered}
    categories={categories}
    fileSets={setItems}
    selectedFileSet={selectedFileSet}
    activeFileSetId={activeFileSetId}
    setActiveFileSetId={setActiveFileSetId}
    activeCategoryId={activeCategoryId}
    setActiveCategoryId={setActiveCategoryId}
    isLoading={isLoading}
    selected={selected}
    setSelected={setSelected}
    showUpload={showUpload}
    setShowUpload={setShowUpload}
    notify={notify}
    toast={toast}
  />;
}
