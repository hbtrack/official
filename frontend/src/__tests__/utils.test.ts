import { describe, it, expect } from 'vitest';
import { cn } from '../lib/utils';

describe('cn()', () => {
  it('merges class names', () => {
    expect(cn('px-2', 'py-2')).toBe('px-2 py-2');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'skip', 'end')).toBe('base end');
  });

  it('resolves tailwind conflicts — last wins', () => {
    // tailwind-merge resolves conflicting utilities
    const result = cn('px-2', 'px-4');
    expect(result).toBe('px-4');
  });

  it('handles undefined and empty strings', () => {
    expect(cn(undefined, '', 'real')).toBe('real');
  });
});
