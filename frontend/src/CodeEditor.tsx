import { lazy, Suspense } from "react";
const Editor = lazy(() => import("./EditorImplementation"));

export default function CodeEditor(props: {
  value: string;
  onChange: (code: string) => void;
  sql?: boolean;
  editable?: boolean;
  height?: string;
}) {
  return (
    <Suspense
      fallback={<div className="result-empty">Загружаем редактор…</div>}
    >
      <Editor {...props} />
    </Suspense>
  );
}
