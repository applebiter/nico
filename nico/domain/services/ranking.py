"""Fractional ranking utilities for ordering items in lists."""

from typing import Optional


def generate_rank_key(before: Optional[str] = None, after: Optional[str] = None) -> str:
    """
    Generate a fractional rank key for ordering items.
    
    This allows for efficient reordering without renumbering entire lists.
    
    Args:
        before: The rank key of the item before this one (None if first)
        after: The rank key of the item after this one (None if last)
    
    Returns:
        A string rank key that sorts lexicographically between before and after
    
    Examples:
        >>> generate_rank_key(None, None)  # First item
        'm'
        >>> generate_rank_key(None, 'm')  # Insert before first
        'g'
        >>> generate_rank_key('m', None)  # Insert after last
        't'
        >>> generate_rank_key('g', 'm')  # Insert between
        'j'
    """
    # Base-26 alphabet (lowercase letters)
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    MID_POINT = len(ALPHABET) // 2  # 13, corresponding to 'm'
    
    if before is None and after is None:
        # First item in empty list
        return ALPHABET[MID_POINT]
    
    if before is None:
        # Insert at beginning
        return _rank_before(after)
    
    if after is None:
        # Insert at end
        return _rank_after(before)
    
    # Insert between two items
    return _rank_between(before, after)


def _rank_before(after: str) -> str:
    """Generate a rank key before the given key."""
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    
    # Get the first character of 'after'
    first_char = after[0]
    first_idx = ALPHABET.index(first_char)
    
    if first_idx > 0:
        # We can just decrement the first character
        mid_idx = first_idx // 2
        return ALPHABET[mid_idx]
    else:
        # First char is 'a', we need to add a suffix
        # Return something like "a" + midpoint of next char
        if len(after) > 1:
            return after[0] + _rank_before(after[1:])
        else:
            # Edge case: after is "a", return something before it
            return ALPHABET[0] + ALPHABET[len(ALPHABET) // 2]


def _rank_after(before: str) -> str:
    """Generate a rank key after the given key."""
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    
    # Get the first character of 'before'
    first_char = before[0]
    first_idx = ALPHABET.index(first_char)
    
    if first_idx < len(ALPHABET) - 1:
        # We can increment toward the end
        mid_idx = (first_idx + len(ALPHABET)) // 2
        return ALPHABET[mid_idx]
    else:
        # First char is 'z', we need to add a suffix
        if len(before) > 1:
            return before[0] + _rank_after(before[1:])
        else:
            # Edge case: before is "z", extend it
            return ALPHABET[-1] + ALPHABET[len(ALPHABET) // 2]


def _rank_between(before: str, after: str) -> str:
    """Generate a rank key between two given keys."""
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    
    # Find the first position where they differ
    min_len = min(len(before), len(after))
    
    for i in range(min_len):
        before_char = before[i]
        after_char = after[i]
        
        if before_char != after_char:
            before_idx = ALPHABET.index(before_char)
            after_idx = ALPHABET.index(after_char)
            
            # If there's room between them
            if after_idx - before_idx > 1:
                mid_idx = (before_idx + after_idx) // 2
                return before[:i] + ALPHABET[mid_idx]
            else:
                # They're adjacent (e.g., 'a' and 'b')
                # Use the before prefix and recurse on the rest
                if i + 1 < len(before):
                    rest_before = before[i + 1:]
                    return before[:i + 1] + _rank_after(rest_before)
                else:
                    # Add a suffix
                    return before + ALPHABET[len(ALPHABET) // 2]
    
    # One is a prefix of the other
    if len(before) < len(after):
        # before is shorter, insert between before and its extension
        return before + ALPHABET[len(ALPHABET) // 2]
    else:
        # Shouldn't normally happen if before < after, but handle it
        return before + ALPHABET[len(ALPHABET) // 2]
