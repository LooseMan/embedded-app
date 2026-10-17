"use client";

import { useEffect, useMemo, useState } from "react";
import { FileManagerView } from "../components/file-manager/FileManagerView";
import type { CategoryResponse, FileEditValues, FileItem, FileResponse, FileSetItem, FileSetResponse } from "../components/file-manager/types";
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

  const refreshFiles = async () => {
    const response = await fetch(`${API_BASE_URL}/files`);
    if (!response.ok) throw new Error("Could not refresh the file list");
    const mappedFiles = mapFiles(await response.json() as FileResponse[], categories);
    setAllFileItems(mappedFiles);
    setFileItems(mappedFiles);
  };

  const onUpload = async (files: File[], categoryId: number, fileSetId: number | null) => {
    for (const file of files) {
      const response = await fetch(`${API_BASE_URL}/files`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ category_id: categoryId, url: file.name, size: file.size }) });
      if (!response.ok) throw new Error(`Could not add ${file.name}`);
      const created = await response.json() as FileResponse;
      if (fileSetId !== null) {
        const attachResponse = await fetch(`${API_BASE_URL}/file-sets/${fileSetId}/files/${created.id}`, { method: "PUT" });
        if (!attachResponse.ok) throw new Error(`Could not add ${file.name} to the selected file set`);
      }
    }
    await refreshFiles();
  };

  const onUpdate = async (file: FileItem, values: FileEditValues) => {
    const response = await fetch(`${API_BASE_URL}/files/${file.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ category_id: values.categoryId, url: values.url, size: values.size }) });
    if (!response.ok) throw new Error("Could not update the file");
    await refreshFiles();
  };

  const onDelete = async (file: FileItem) => {
    const response = await fetch(`${API_BASE_URL}/files/${file.id}`, { method: "DELETE" });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Could not delete the file (${response.status})`);
    }
    await refreshFiles();
  };

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
    onUpload={onUpload}
    onUpdate={onUpdate}
    onDelete={onDelete}
  />;
}
