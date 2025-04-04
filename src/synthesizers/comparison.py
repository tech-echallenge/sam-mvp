"""
Comparison module for creating side-by-side views of original text and summaries.

This module provides functionality to generate HTML comparisons that make it
easy to review how the summary relates to the original text.
"""
import os
import re
from typing import List, Tuple, Dict, Any
import html

from src.models.document import Document


def _split_into_sections(text: str) -> List[Tuple[str, str]]:
    """
    Split text into sections based on headers.
    
    Args:
        text: The text to split
        
    Returns:
        List[Tuple[str, str]]: List of (section_title, section_content) tuples
    """
    # Look for patterns like "## Section Name" or "Section Name\n--"
    section_pattern = r'(?:^|\n)(?:#{1,6}\s+([^\n]+)|([^\n]+)\n[-=]+)'

    # Find all section headers
    matches = list(re.finditer(section_pattern, text))
    sections = []

    # Process each section
    for i, match in enumerate(matches):
        # Get the section title (from either capture group)
        title = match.group(1) if match.group(1) else match.group(2)

        # Get the start of the section content
        start = match.end()

        # Get the end of the section (start of next section or end of text)
        end = matches[i + 1].start() if i < len(matches) - 1 else len(text)

        # Get the section content
        content = text[start:end].strip()

        sections.append((title, content))

    # If no sections found or first section doesn't start at beginning,
    # add an "Introduction" section for the initial content
    if not sections or matches[0].start() > 0:
        intro_content = text[:matches[0].start()].strip(
        ) if matches else text.strip()
        if intro_content:
            sections.insert(0, ("Introduction", intro_content))

    return sections


def create_comparison_html(document: Document, synthesis: str) -> str:
    """
    Create an HTML comparison between the original document and the synthesis.
    
    Args:
        document: The processed document
        synthesis: The synthesized summary
        
    Returns:
        str: HTML content with side-by-side comparison
    """
    # Get the original text
    original_text = "\n\n".join(p.text for p in document.paragraphs)

    # Split both texts into sections
    original_sections = _split_into_sections(original_text)
    synthesis_sections = _split_into_sections(synthesis)

    # Prepare JSON for debugging view
    import json
    doc_dict = {
        "metadata":
        document.metadata,
        "paragraphs": [{
            "id":
            p.id,
            "text":
            p.text,
            "structural_tag":
            p.structural_tag.name,
            "argument_role":
            p.argument_role.name,
            "gist":
            p.gist,
            "word_count":
            len(p.text.split()),
            "gist_sentences": [{
                "text": s.text,
                "image_tag": s.image_tag
            }
                               for s in p.gist_sentences] if hasattr(
                                   p, 'gist_sentences') else []
        } for p in document.paragraphs],
        "synthesis":
        synthesis
    }
    json_data = json.dumps(doc_dict, indent=2)

    # Calculate statistics
    original_words = len(original_text.split())
    synthesis_words = len(synthesis.split())
    reduction_pct = round((1 - synthesis_words / original_words) *
                          100, 1) if original_words > 0 else 0

    # Start building HTML with Tailwind CSS
    html_parts = [
        """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document Comparison</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            primary: '#3b82f6',
                            secondary: '#10b981',
                            dark: {
                                100: '#374151',
                                200: '#1f2937',
                                300: '#111827',
                            }
                        }
                    }
                }
            }
        </script>
        <style type="text/tailwind">
            @layer components {
                .btn {
                    @apply px-4 py-2 rounded font-medium focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-colors;
                }
                .btn-primary {
                    @apply bg-primary text-white hover:bg-blue-600 focus:ring-blue-500;
                }
                .btn-secondary {
                    @apply bg-gray-700 text-white hover:bg-gray-800 focus:ring-gray-600;
                }
                pre.json {
                    @apply p-4 rounded-lg bg-gray-800 text-gray-100 overflow-x-auto text-sm;
                }
            }
        </style>
        <script>
            function toggleView() {
                const comparisonView = document.getElementById('comparison-view');
                const jsonView = document.getElementById('json-view');
                const toggleBtn = document.getElementById('toggle-btn');
                
                if (comparisonView.classList.contains('hidden')) {
                    comparisonView.classList.remove('hidden');
                    jsonView.classList.add('hidden');
                    toggleBtn.textContent = 'View JSON';
                } else {
                    comparisonView.classList.add('hidden');
                    jsonView.classList.remove('hidden');
                    toggleBtn.textContent = 'View Comparison';
                }
            }
        </script>
    </head>
    <body class="bg-gray-900 text-gray-100 min-h-screen flex flex-col">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-grow">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-3xl font-bold text-white">Document Comparison</h1>
                <button id="toggle-btn" onclick="toggleView()" class="btn btn-secondary">
                    View JSON
                </button>
            </div>
            
            <!-- Metadata Card -->
            <div class="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <h2 class="text-xl font-semibold text-white mb-2">Document Info</h2>
                        <p class="text-gray-300"><span class="font-medium text-gray-200">Title:</span> """
        + html.escape(document.metadata.get('title', 'Untitled')) + """</p>
                        <p class="text-gray-300"><span class="font-medium text-gray-200">Source:</span> """
        + html.escape(document.metadata.get('source_path', 'Unknown')) +
        """</p>
                    </div>
                    <div>
                        <h2 class="text-xl font-semibold text-white mb-2">Statistics</h2>
                        <div class="grid grid-cols-3 gap-2">
                            <div class="bg-gray-700 rounded p-3">
                                <p class="text-sm text-gray-300">Original</p>
                                <p class="text-xl font-bold text-white">""" +
        str(original_words) + """</p>
                                <p class="text-xs text-gray-400">words</p>
                            </div>
                            <div class="bg-gray-700 rounded p-3">
                                <p class="text-sm text-gray-300">Summary</p>
                                <p class="text-xl font-bold text-white">""" +
        str(synthesis_words) + """</p>
                                <p class="text-xs text-gray-400">words</p>
                            </div>
                            <div class="bg-indigo-800 rounded p-3">
                                <p class="text-sm text-gray-300">Reduction</p>
                                <p class="text-xl font-bold text-white">""" +
        str(reduction_pct) + """%</p>
                                <p class="text-xs text-gray-400">saved</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Comparison View -->
            <div id="comparison-view" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Original Document Column -->
                <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                    <div class="bg-gray-700 p-4 border-b border-gray-600">
                        <h2 class="text-xl font-bold text-white">Original Document</h2>
                    </div>
                    <div class="p-5 overflow-y-auto" style="max-height: 70vh;">
    """
    ]

    # Add original sections
    for title, content in original_sections:
        html_parts.append(f'<div class="mb-8 pb-6 border-b border-gray-700">')
        html_parts.append(
            f'<h3 class="text-lg font-semibold text-blue-400 mb-3">{html.escape(title)}</h3>'
        )
        html_parts.append(
            f'<div class="text-gray-300 whitespace-pre-line">{html.escape(content)}</div>'
        )
        html_parts.append(f'</div>')

    # Add divider and start synthesis column
    html_parts.append("""
                    </div>
                </div>
                
                <!-- Synthesized Summary Column -->
                <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                    <div class="bg-gray-700 p-4 border-b border-gray-600">
                        <h2 class="text-xl font-bold text-white">Synthesized Summary</h2>
                    </div>
                    <div class="p-5 overflow-y-auto" style="max-height: 70vh;">
    """)

    # Add synthesis sections
    for title, content in synthesis_sections:
        html_parts.append(f'<div class="mb-8 pb-6 border-b border-gray-700">')
        html_parts.append(
            f'<h3 class="text-lg font-semibold text-green-400 mb-3">{html.escape(title)}</h3>'
        )
        html_parts.append(
            f'<div class="text-gray-300 whitespace-pre-line">{html.escape(content)}</div>'
        )
        html_parts.append(f'</div>')

    # Add JSON view (hidden by default)
    html_parts.append("""
                    </div>
                </div>
            </div>
            
            <!-- JSON Debug View (Hidden by Default) -->
            <div id="json-view" class="hidden">
                <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                    <div class="bg-gray-700 p-4 border-b border-gray-600">
                        <h2 class="text-xl font-bold text-white">JSON Data</h2>
                    </div>
                    <div class="p-5 overflow-y-auto" style="max-height: 80vh;">
                        <pre class="json">""" + html.escape(json_data) +
                      """</pre>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="bg-gray-800 py-4 w-full mt-auto">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <p class="text-center text-gray-400 text-sm">
                    Generated with Document Synthesis Tool
                </p>
            </div>
        </footer>
    </body>
    </html>
    """)

    return "\n".join(html_parts)


def save_comparison(document: Document, synthesis: str,
                    output_path: str) -> None:
    """
    Generate and save an HTML comparison between original text and summary.
    
    Args:
        document: The processed document
        synthesis: The synthesized summary
        output_path: Path where to save the HTML file
    """
    html_content = create_comparison_html(document, synthesis)

    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Save HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
