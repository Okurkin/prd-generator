import difflib
import re

def generate_html_diff(old_text: str, new_text: str) -> str:
    """Generate HTML diff with green/red highlighting"""
    
    # Split text into lines for better diff
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    
    # Generate diff
    diff = difflib.unified_diff(
        old_lines, 
        new_lines, 
        fromfile='Previous Version', 
        tofile='Current Version',
        lineterm=''
    )
    
    html_diff = []
    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            continue
        elif line.startswith('@@'):
            html_diff.append(f'<div style="color: #666; font-weight: bold; margin: 10px 0;">{line}</div>')
        elif line.startswith('+'):
            html_diff.append(f'<div style="background-color: #d4edda; color: #155724; padding: 2px 5px; border-left: 3px solid #28a745;">{line[1:]}</div>')
        elif line.startswith('-'):
            html_diff.append(f'<div style="background-color: #f8d7da; color: #721c24; padding: 2px 5px; border-left: 3px solid #dc3545;">{line[1:]}</div>')
        else:
            html_diff.append(f'<div style="padding: 2px 5px;">{line}</div>')
    
    return ''.join(html_diff)

def generate_side_by_side_diff(old_text: str, new_text: str) -> str:
    """Generate side-by-side diff view"""
    
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    # Use difflib to get opcodes for better diff
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    html = ['<div style="display: flex; gap: 20px;">']
    html.append('<div style="flex: 1;"><h4>Previous Version</h4>')
    html.append('<div style="border: 1px solid #ddd; padding: 10px; background: #f8f9fa; max-height: 400px; overflow-y: auto;">')
    
    # Process old lines with opcodes
    old_processed = set()
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i in range(i1, i2):
                html.append(f'<div style="padding: 2px;">{old_lines[i] if i < len(old_lines) else ""}</div>')
                old_processed.add(i)
        elif tag in ['delete', 'replace']:
            for i in range(i1, i2):
                html.append(f'<div style="background-color: #f8d7da; color: #721c24; padding: 2px; border-left: 3px solid #dc3545;">{old_lines[i] if i < len(old_lines) else ""}</div>')
                old_processed.add(i)
    
    # Add any remaining old lines
    for i, line in enumerate(old_lines):
        if i not in old_processed:
            html.append(f'<div style="padding: 2px;">{line}</div>')
    
    html.append('</div></div>')
    
    # Process new lines
    html.append('<div style="flex: 1;"><h4>Current Version</h4>')
    html.append('<div style="border: 1px solid #ddd; padding: 10px; background: #f8f9fa; max-height: 400px; overflow-y: auto;">')
    
    new_processed = set()
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for j in range(j1, j2):
                html.append(f'<div style="padding: 2px;">{new_lines[j] if j < len(new_lines) else ""}</div>')
                new_processed.add(j)
        elif tag in ['insert', 'replace']:
            for j in range(j1, j2):
                html.append(f'<div style="background-color: #d4edda; color: #155724; padding: 2px; border-left: 3px solid #28a745;">{new_lines[j] if j < len(new_lines) else ""}</div>')
                new_processed.add(j)
    
    # Add any remaining new lines
    for j, line in enumerate(new_lines):
        if j not in new_processed:
            html.append(f'<div style="padding: 2px;">{line}</div>')
    
    html.append('</div></div></div>')
    
    return ''.join(html)

def get_change_stats(old_text: str, new_text: str) -> dict:
    """Get statistics about changes between two texts"""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    added = 0
    removed = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'delete':
            removed += i2 - i1
        elif tag == 'insert':
            added += j2 - j1
        elif tag == 'replace':
            removed += i2 - i1
            added += j2 - j1
    
    return {
        'lines_added': added,
        'lines_removed': removed,
        'lines_changed': added + removed,
        'similarity_ratio': matcher.ratio()
    }
