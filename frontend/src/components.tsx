import { useState } from 'react'
import { ArrowDownUp, Check, ChevronLeft, ChevronRight, Database } from 'lucide-react'
import type { Frame, Output } from './types'

export function Code({ children }: { children: string }) { return <pre className="code-block"><code>{children}</code></pre> }
export function Tag({ children, green = false }: { children: React.ReactNode; green?: boolean }) { return <span className={`tag ${green ? 'green' : ''}`}>{children}</span> }
export function Checkmark({ checked }: { checked: boolean }) { return <span className={`checkmark ${checked ? 'checked' : ''}`}>{checked && <Check size={12} />}</span> }

export function DataTable({ frame, title = 'DataFrame preview' }: { frame: Frame; title?: string }) {
  const [sort, setSort] = useState<{ column: number; asc: boolean } | null>(null)
  const [page, setPage] = useState(0)
  const rows = frame.data.map((row, index) => ({ row, index }))
  if (sort) rows.sort((a, b) => {
    const av = a.row[sort.column], bv = b.row[sort.column]
    const comparison = typeof av === 'number' && typeof bv === 'number' ? av - bv : String(av ?? '').localeCompare(String(bv ?? ''))
    return comparison * (sort.asc ? 1 : -1)
  })
  const pages = Math.max(1, Math.ceil(rows.length / 10))
  const currentPage = Math.min(page, pages - 1)
  return <div className="data-viewer"><div className="data-title"><span><Database size={14} /> {title}</span><span>{rows.length} строк × {frame.columns.length} колонок</span></div><div className="table-scroll"><table><thead><tr><th>#</th>{frame.columns.map((column, index) => <th key={column}><button onClick={() => { setSort({ column: index, asc: sort?.column === index ? !sort.asc : true }); setPage(0) }} title="Сортировка только preview">{column}<ArrowDownUp size={11}/></button></th>)}</tr></thead><tbody>{rows.slice(currentPage * 10, currentPage * 10 + 10).map(({ row, index }) => <tr key={index}><td>{index}</td>{row.map((value, i) => <td key={i} className={typeof value === 'number' ? 'numeric' : ''}>{value === null ? <span className="muted">NaN</span> : String(value)}</td>)}</tr>)}</tbody></table>{!rows.length && <p className="empty">Пустая таблица · 0 строк</p>}</div><div className="table-footer"><span>Сортировка preview не меняет входные данные</span><span><button aria-label="Предыдущие строки" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}><ChevronLeft size={14}/></button> {currentPage + 1} / {pages} <button aria-label="Следующие строки" disabled={currentPage + 1 >= pages} onClick={() => setPage(currentPage + 1)}><ChevronRight size={14}/></button></span></div></div>
}

export function PlotPreview({ output }: { output: Output }) {
  const line = output.lines?.[0]
  if (!line || !line.y.length) return <p>На графике нет точек.</p>
  const min = Math.min(0, ...line.y), max = Math.max(1, ...line.y), span = max - min || 1
  const x = (i: number) => 65 + (i / Math.max(1, line.y.length - 1)) * 560
  const y = (v: number) => 245 - ((v - min) / span) * 190
  return <figure className="plot"><figcaption>{output.title}</figcaption><svg viewBox="0 0 700 310" role="img" aria-label={`${output.title}. ${output.xlabel}: ${line.x.join(', ')}. ${output.ylabel}: ${line.y.join(', ')}`}>
    {[0, 1, 2, 3, 4].map(i => <g key={i}><line x1="65" x2="640" y1={55 + i * 47.5} y2={55 + i * 47.5} stroke="currentColor" opacity=".12"/><text x="55" y={59 + i * 47.5} textAnchor="end" fontSize="11" fill="currentColor">{Math.round(max - i * span / 4)}</text></g>)}
    <polyline fill="none" stroke="#b9f58a" strokeWidth="3" points={line.y.map((v, i) => `${x(i)},${y(v)}`).join(' ')}/>
    {line.y.map((v, i) => <g key={i}><circle cx={x(i)} cy={y(v)} r="4" fill="#b9f58a"/><text x={x(i)} y="268" textAnchor="middle" fontSize="10" fill="currentColor">{line.x[i]}</text></g>)}
    <text x="350" y="299" textAnchor="middle" fontSize="12" fill="currentColor">{output.xlabel}</text><text x="17" y="150" textAnchor="middle" transform="rotate(-90 17 150)" fontSize="12" fill="currentColor">{output.ylabel}</text>
  </svg><p className="muted">Preview по реальным точкам и подписям возвращённого Matplotlib Figure.</p></figure>
}
