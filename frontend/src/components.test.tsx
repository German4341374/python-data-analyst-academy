import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DataTable, PlotPreview } from './components'

describe('DataFrame preview', () => {
  it('sorts numeric values without changing the source table', () => {
    const frame = { columns: ['city', 'revenue'], data: [['Riga', 100], ['Paris', 20]] }
    render(<DataTable frame={frame}/>)
    fireEvent.click(screen.getByRole('button', { name: /revenue/ }))
    const rows = screen.getAllByRole('row')
    expect(rows[1]).toHaveTextContent('Paris')
    expect(frame.data[0][0]).toBe('Riga')
  })
  it('renders an accessible plot from submitted data', () => {
    render(<PlotPreview output={{ type: 'plot', title: 'Revenue', xlabel: 'Month', ylabel: 'EUR', lines: [{ x: ['Jan', 'Feb'], y: [10, 30] }] }}/>)
    expect(screen.getByRole('img')).toHaveAccessibleName(/10, 30/)
  })
})
