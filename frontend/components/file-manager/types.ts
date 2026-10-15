export type FileItem = {
  id: number;
  name: string;
  url: string;
  categoryId: number;
  category: string;
  type: string;
  size: string;
  updated: string;
  color: string;
  favorite?: boolean;
};

export type FileResponse = { id: number; category_id: number; url: string; size: number };
export type CategoryResponse = { id: number; name: string };
export type FileSetResponse = { id: number; name: string };
export type FileSetItem = FileSetResponse & { color: string };
