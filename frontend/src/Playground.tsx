import { useState } from "react";
import { Code2, Loader2, Play, RotateCcw, Terminal } from "lucide-react";
import { api } from "./api";
import CodeEditor from "./CodeEditor";
import { Code, DataTable, PlotPreview, Tag } from "./components";
import type { Output } from "./types";

interface Execution {
  stdout: string;
  stderr: string;
  error?: string;
  message?: string;
  result?: Output;
  duration: number;
}
const examples: Record<string, string> = {
  "Первый Python":
    'price = 12.5\nquantity = 4\nrevenue = price * quantity\nprint("Выручка:", revenue)\n',
  DataFrame:
    "import pandas as pd\n\n# Учебная таблица продаж уже доступна как df\nprint(df.shape)\nresult = df.assign(revenue=df.quantity * df.price)\n",
  NumPy:
    'import numpy as np\n\nvalues = np.array([12, 18, 25, 9, 40])\nprint("Среднее:", values.mean())\nresult = values[values > 15]\n',
  Matplotlib:
    'import matplotlib.pyplot as plt\n\nsummary = df.groupby("city", as_index=False).agg(revenue=("price", "sum"))\nfig, ax = plt.subplots()\nax.bar(summary.city, summary.revenue)\nax.set(title="Сумма цен по городам", xlabel="Город", ylabel="Сумма цен, EUR")\nresult = fig\n',
  Seaborn:
    'import matplotlib.pyplot as plt\nimport seaborn as sns\n\nfig, ax = plt.subplots()\nsns.histplot(data=df, x="price", bins=5, ax=ax)\nax.set(title="Распределение цен", xlabel="Цена, EUR", ylabel="Позиции")\nresult = fig\n',
};

export default function Playground() {
  const [code, setCode] = useState(
    localStorage.getItem("academy-playground") || examples["Первый Python"],
  );
  const [busy, setBusy] = useState(false);
  const [output, setOutput] = useState<Execution | null>(null);
  const [error, setError] = useState("");
  function change(value: string) {
    setCode(value);
    localStorage.setItem("academy-playground", value);
  }
  async function run() {
    setBusy(true);
    setError("");
    setOutput(null);
    try {
      setOutput(await api<Execution>("/playground", { code }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">YOUR DATA LAB</div>
          <h1>Место для экспериментов</h1>
          <p>
            Запускайте Python, исследуйте DataFrame и стройте графики. Здесь
            можно спокойно пробовать.
          </p>
        </div>
        <Tag green>Python · pandas · NumPy</Tag>
      </div>
      <div className="filter-tabs playground-examples">
        {Object.keys(examples).map((name) => (
          <button
            key={name}
            disabled={busy}
            onClick={() => {
              change(examples[name]);
              setOutput(null);
            }}
          >
            {name}
          </button>
        ))}
      </div>
      <div className="playground-layout">
        <section className="editor-panel">
          <div className="editor-top">
            <span>
              <Code2 size={16} />
              experiment.py
            </span>
            <button
              className="icon-button"
              aria-label="Сбросить эксперимент"
              disabled={busy}
              onClick={() => change(examples["Первый Python"])}
            >
              <RotateCcw size={15} />
            </button>
          </div>
          <CodeEditor
            value={code}
            onChange={change}
            editable={!busy}
            height="420px"
          />
          <div className="editor-actions">
            <span className="editor-language">12 сек · 256 MB · без сети</span>
            <button className="primary" disabled={busy} onClick={run}>
              {busy ? (
                <Loader2 size={16} className="spin" />
              ) : (
                <Play size={16} />
              )}
              Запустить эксперимент
            </button>
          </div>
        </section>
        <section className="panel padded">
          <div className="section-heading">
            <h2>Результат</h2>
            <Terminal size={18} />
          </div>
          {!output && !error && (
            <div className="result-empty">
              {busy ? (
                <Loader2 className="spin" size={25} />
              ) : (
                <Terminal size={25} />
              )}
              <p>
                {busy
                  ? "Выполняем код в отдельном контейнере…"
                  : "Используйте print() для текста и переменную result для таблицы, массива, числа или Figure."}
              </p>
            </div>
          )}
          {error && (
            <p className="text-amber" role="alert">
              {error}
            </p>
          )}
          {output && (
            <>
              <Tag>{output.duration.toFixed(2)} сек</Tag>
              {output.error && (
                <div className="feedback incorrect">
                  <strong>{output.error}</strong>
                  <p>{output.message}</p>
                </div>
              )}
              {output.stdout && <Code>{output.stdout}</Code>}
              {output.stderr && <Code>{output.stderr}</Code>}
              {output.result?.type === "dataframe" && (
                <DataTable
                  frame={{
                    columns: output.result.columns || [],
                    data: output.result.data || [],
                  }}
                />
              )}{" "}
              {output.result?.type === "plot" && (
                <PlotPreview output={output.result} />
              )}{" "}
              {output.result &&
                ["array", "scalar"].includes(output.result.type) && (
                  <Code>{JSON.stringify(output.result.data, null, 2)}</Code>
                )}
              {!output.error &&
                output.result?.type === "none" &&
                !output.stdout && (
                  <p className="muted">
                    Код выполнен без вывода. Добавьте print() или сохраните
                    результат в result.
                  </p>
                )}
            </>
          )}
        </section>
      </div>
      <div className="info-banner">
        <Terminal size={22} />
        <p>
          Каждый запуск начинается с чистого состояния. Доступны pd, np и
          учебная таблица df с city, quantity, price. Эксперименты не
          оцениваются и не изменяют учебный прогресс.
        </p>
      </div>
    </div>
  );
}
