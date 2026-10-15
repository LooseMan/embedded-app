import type { CategoryResponse, FileItem, FileResponse } from "./types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes;
  let unit = -1;
  do { value /= 1024; unit += 1; } while (value >= 1024 && unit < units.length - 1);
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unit]}`;
}

export function fileType(url: string) {
  const extension = url.split("?")[0].split(".").pop();
  return extension ? extension.toUpperCase().slice(0, 4) : "FILE";
}

export function fileColor(type: string) {
  if (["PDF", "TXT"].includes(type)) return "red";
  if (["FIG", "SVG", "PSD"].includes(type)) return "orange";
  if (["XLS", "CSV"].includes(type)) return "green";
  if (["MP4", "MOV", "MP3"].includes(type)) return "purple";
  return "blue";
}

export function mapFiles(files: FileResponse[], categories: CategoryResponse[]): FileItem[] {
  const categoryNames = new Map(categories.map(category => [category.id, category.name]));
  return files.map(file => {
    const name = file.url.split("?")[0].split("/").pop() || file.url;
    const type = fileType(file.url);
    return {
      id: file.id,
      name,
      url: file.url,
      categoryId: file.category_id,
      category: categoryNames.get(file.category_id) ?? `Category ${file.category_id}`,
      type,
      size: formatSize(file.size),
      updated: "Recently added",
      color: fileColor(type),
    };
  });
}
