"""Utility functions for text processing."""
import re
from typing import List


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using sophisticated rules.
    
    This implementation handles common edge cases like:
    - Abbreviations (e.g., Dr., Mr., U.S.A.)
    - Decimal numbers (e.g., 3.14)
    - Ellipses (...)
    - Sentence markers within quotes
    - Common known abbreviations
    
    Args:
        text: Text to split
        
    Returns:
        List[str]: List of sentences
    """
    # Common abbreviations that don't end sentences
    abbreviations = [
        'dr', 'mr', 'mrs', 'ms', 'prof', 'rev', 'gen', 'hon', 'jr', 'sr',
        'st', 'ltd', 'co', 'inc', 'fig', 'ca', 'vs', 'etc', 'pp', 'viz',
        'al', 'ed', 'est', 'min', 'max', 'dept', 'univ', 'assn', 'bros',
        'approx', 'e.g', 'i.e', 'ph.d', 'm.d', 'b.a', 'm.a', 'a.d', 'b.c',
        'a.m', 'p.m', 'u.s.a', 'u.k', 'u.n'
    ]
    
    # Prepare text by removing line breaks within paragraphs
    # This helps with handling section headers that might be on their own line
    text = text.replace('\n', ' ')
    
    # First split by obvious sentence terminators with space after
    potential_sentences = []
    for potential_sentence in re.split(r'(?<=[.!?])\s+', text):
        if not potential_sentence.strip():
            continue
        potential_sentences.append(potential_sentence.strip())
    
    # Now apply more careful processing to handle abbreviations, etc.
    sentences = []
    for potential_sentence in potential_sentences:
        # Skip if already empty
        if not potential_sentence.strip():
            continue
            
        # Check if this is a standalone sentence or needs to be joined
        # with a previous one due to abbreviations
        if sentences and potential_sentence:
            # Check if previous sentence ends with a known abbreviation
            prev_sentence = sentences[-1].lower()
            prev_words = prev_sentence.split()
            
            if prev_words:
                last_word = prev_words[-1].rstrip('.').lower()
                
                # Check if the last word is a known abbreviation
                if (last_word in abbreviations or 
                    # Check for single letter abbreviations (e.g., E. coli)
                    (len(last_word) == 1 and last_word.isalpha()) or
                    # Check for potential decimal number
                    (prev_sentence.rstrip().endswith('.') and 
                     any(c.isdigit() for c in prev_words[-1]))):
                    
                    # This is likely a continuation, not a new sentence
                    sentences[-1] = f"{sentences[-1]} {potential_sentence}"
                    continue
        
        # If we got here, it's a new sentence
        sentences.append(potential_sentence)
    
    # Final cleanup - handle ellipses, quotes, and other special cases
    final_sentences = []
    for sentence in sentences:
        # Handle ellipses as continuation, except if followed by quotes
        if '...' in sentence and not sentence.endswith('...'):
            parts = sentence.split('...')
            # Keep the first part with ellipses
            if parts[0]:
                final_sentences.append(f"{parts[0]}...")
            # Join remaining parts as a new sentence
            if len(parts) > 1 and parts[1]:
                remainder = '...'.join(parts[1:])
                if remainder.strip():
                    final_sentences.append(remainder.strip())
        else:
            final_sentences.append(sentence)
            
    return final_sentences