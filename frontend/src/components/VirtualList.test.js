import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import VirtualList from './VirtualList.svelte'

const items = Array.from({ length: 200 }, (_, i) => ({ videoId: String(i), title: `Item ${i}` }))

describe('VirtualList', () => {
  it('renders without crashing', () => {
    const { container } = render(VirtualList, { props: { items, rowHeight: 60, height: 300 } })
    expect(container).toBeTruthy()
  })

  it('renders fewer rows than total items', () => {
    const { container } = render(VirtualList, { props: { items, rowHeight: 60, height: 300 } })
    const rows = container.querySelectorAll('[data-index]')
    expect(rows.length).toBeLessThan(items.length)
  })
})
