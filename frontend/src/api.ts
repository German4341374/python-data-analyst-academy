export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, { credentials: 'same-origin', ...(body !== undefined ? { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Academy': '1' }, body: JSON.stringify(body) } : {}) })
  const data = await response.json()
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Проверьте введённые данные и попробуйте снова.')
  return data as T
}
