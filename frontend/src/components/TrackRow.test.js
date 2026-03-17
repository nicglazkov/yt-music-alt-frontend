import { describe, it, expect, vi } from 'vitest'
import { render, fireEvent } from '@testing-library/svelte'
import TrackRow from './TrackRow.svelte'

const track = { videoId: 'aaa', title: 'Song A', artists: [{ name: 'Artist A' }], album: { name: 'Album A' } }

describe('TrackRow', () => {
  it('renders title and artist', () => {
    const { getByText } = render(TrackRow, { props: { track, selected: false } })
    expect(getByText('Song A')).toBeTruthy()
    expect(getByText('Artist A')).toBeTruthy()
  })

  it('checkbox checked when selected=true', () => {
    const { container } = render(TrackRow, { props: { track, selected: true } })
    expect(container.querySelector('input[type="checkbox"]').checked).toBe(true)
  })

  it('fires select event on checkbox click', async () => {
    const handler = vi.fn()
    const { component, container } = render(TrackRow, { props: { track, selected: false } })
    component.$on('select', handler)
    await fireEvent.click(container.querySelector('input[type="checkbox"]'))
    expect(handler).toHaveBeenCalled()
  })
})
