import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { sql } from "@codemirror/lang-sql";

export default function Editor(props: {
  value: string;
  onChange: (code: string) => void;
  sql?: boolean;
  editable?: boolean;
  height?: string;
}) {
  return (
    <CodeMirror
      value={props.value}
      height={props.height || "350px"}
      theme={
        document.documentElement.dataset.theme === "light" ? "light" : "dark"
      }
      extensions={[props.sql ? sql() : python()]}
      onChange={props.onChange}
      aria-label="Редактор решения"
      editable={props.editable !== false}
      basicSetup={{
        lineNumbers: true,
        foldGutter: true,
        highlightActiveLine: true,
        autocompletion: true,
      }}
    />
  );
}
