#!/usr/bin/env python3
"""
Local dev server for My Memory Vault.
Serves static files + CRUD API for vault.md.

MD format:
  ## Category: <name>
  ### Topic: <name>
  #### Subtopic: <name>      (optional, nested under a topic)
  - **YYYY-MM-DD** — summary
    - optional detail lines

Usage: python3 server.py [port]   (default: 8000)
"""
import http.server
import json
import re
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
LEARNINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vault.md')

IS_CATEGORY = re.compile(r'^##\s+Category:\s*(.+)')
IS_TOPIC    = re.compile(r'^###\s+Topic:\s*(.+)')
IS_SUBTOPIC = re.compile(r'^####\s+Subtopic:\s*(.+)')
IS_ENTRY    = re.compile(r'^[-*]\s+\*\*(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?)\*\*')
IS_H2       = re.compile(r'^##\s')


# ── File helpers ──────────────────────────────────────────────────────────────

def _read():
    with open(LEARNINGS_FILE, 'r') as f:
        return f.readlines()

def _write(lines):
    with open(LEARNINGS_FILE, 'w') as f:
        f.writelines(lines)

def _find_category(lines, category_name):
    start = end = None
    for i, line in enumerate(lines):
        m = IS_CATEGORY.match(line)
        if m:
            if start is not None:
                end = i
                break
            if m.group(1).strip() == category_name:
                start = i
    if start is not None and end is None:
        end = len(lines)
    return start, end

def _find_topic(lines, topic_name):
    start = end = None
    for i, line in enumerate(lines):
        if IS_TOPIC.match(line):
            m = IS_TOPIC.match(line)
            if start is not None:
                end = i
                break
            if m.group(1).strip() == topic_name:
                start = i
        elif IS_H2.match(line) and start is not None:
            end = i
            break
    if start is not None and end is None:
        end = len(lines)
    return start, end

def _find_subtopic(lines, topic_name, subtopic_name):
    """Return (start, end) for a #### Subtopic section within a topic, or (None, None)."""
    t_start, t_end = _find_topic(lines, topic_name)
    if t_start is None:
        return None, None
    start = end = None
    for i in range(t_start + 1, t_end):
        m = IS_SUBTOPIC.match(lines[i])
        if m:
            if start is not None:
                end = i
                break
            if m.group(1).strip() == subtopic_name:
                start = i
    if start is not None and end is None:
        end = t_end
    return start, end

def _find_entry(lines, topic_name, date, subtopic_name=None):
    """Return (entry_start, entry_end, container_idx) or (None, None, None).
    Searches within subtopic if subtopic_name given, else within direct topic entries.
    """
    if subtopic_name:
        s_start, s_end = _find_subtopic(lines, topic_name, subtopic_name)
        if s_start is None:
            return None, None, None
        container_idx = s_start
        search_start, search_end = s_start + 1, s_end
    else:
        t_start, t_end = _find_topic(lines, topic_name)
        if t_start is None:
            return None, None, None
        container_idx = t_start
        search_start = t_start + 1
        # Only scan direct entries — stop at first #### Subtopic
        search_end = t_end
        for i in range(t_start + 1, t_end):
            if IS_SUBTOPIC.match(lines[i]):
                search_end = i
                break

    entry_start = entry_end = None
    i = search_start
    while i < search_end:
        line = lines[i]
        if entry_start is None:
            em = IS_ENTRY.match(line)
            if em and em.group(1) == date:
                entry_start = i
                entry_end = i + 1
        else:
            if line.startswith(' ') or line.startswith('\t'):
                entry_end = i + 1
            else:
                break
        i += 1
    return entry_start, entry_end, container_idx

def _category_is_empty(lines, cat_idx):
    j = cat_idx + 1
    while j < len(lines):
        if IS_H2.match(lines[j]):
            break
        if IS_TOPIC.match(lines[j]):
            return False
        j += 1
    return True

def _delete_category_if_empty(lines, search_from_idx):
    cat_idx = None
    for k in range(search_from_idx - 1, -1, -1):
        if IS_CATEGORY.match(lines[k]):
            cat_idx = k
            break
        if IS_H2.match(lines[k]):
            break
    if cat_idx is None or not _category_is_empty(lines, cat_idx):
        return lines, False
    cat_end = cat_idx + 1
    while cat_end < len(lines) and not IS_H2.match(lines[cat_end]):
        cat_end += 1
    del lines[cat_idx:cat_end]
    return lines, True

def _topic_is_empty(lines, t_start, t_end):
    """True if topic has no direct entries and no subtopics."""
    for j in range(t_start + 1, t_end):
        if IS_ENTRY.match(lines[j]) or IS_SUBTOPIC.match(lines[j]):
            return False
    return True


# ── Mutation functions ────────────────────────────────────────────────────────

def delete_entry(topic_name, date, subtopic_name=None):
    lines = _read()
    entry_start, entry_end, _ = _find_entry(lines, topic_name, date, subtopic_name)
    if entry_start is None:
        return False, False, False, False  # ok, subtopicDeleted, topicDeleted, categoryDeleted

    del lines[entry_start:entry_end]

    subtopic_deleted = False
    topic_deleted = False
    category_deleted = False

    if subtopic_name:
        s_start, s_end = _find_subtopic(lines, topic_name, subtopic_name)
        if s_start is not None:
            has_entries = any(IS_ENTRY.match(lines[j]) for j in range(s_start + 1, s_end))
            if not has_entries:
                del lines[s_start:s_end]
                subtopic_deleted = True

    t_start, t_end = _find_topic(lines, topic_name)
    if t_start is not None and _topic_is_empty(lines, t_start, t_end):
        del lines[t_start:t_end]
        topic_deleted = True
        lines, category_deleted = _delete_category_if_empty(lines, t_start)

    _write(lines)
    return True, subtopic_deleted, topic_deleted, category_deleted


def delete_topic(topic_name):
    lines = _read()
    start, end = _find_topic(lines, topic_name)
    if start is None:
        return False, False
    del lines[start:end]
    lines, category_deleted = _delete_category_if_empty(lines, start)
    _write(lines)
    return True, category_deleted


def rename_topic(old_name, new_name):
    lines = _read()
    for i, line in enumerate(lines):
        m = IS_TOPIC.match(line)
        if m and m.group(1).strip() == old_name:
            lines[i] = line[:m.start(1)] + new_name + '\n'
            _write(lines)
            return True
    return False


def update_entry(topic_name, date, new_summary, new_detail, subtopic_name=None):
    lines = _read()
    entry_start, entry_end, _ = _find_entry(lines, topic_name, date, subtopic_name)
    if entry_start is None:
        return False
    replacement = [f'- **{date}** — {new_summary}\n']
    if new_detail.strip():
        for dl in new_detail.strip().split('\n'):
            replacement.append(f'  {dl}\n')
    lines[entry_start:entry_end] = replacement
    _write(lines)
    return True


def delete_category(category_name):
    lines = _read()
    start, end = _find_category(lines, category_name)
    if start is None:
        return False
    del lines[start:end]
    _write(lines)
    return True


def rename_category(old_name, new_name):
    lines = _read()
    for i, line in enumerate(lines):
        m = IS_CATEGORY.match(line)
        if m and m.group(1).strip() == old_name:
            lines[i] = line[:m.start(1)] + new_name + '\n'
            _write(lines)
            return True
    return False


def reorder_categories(order):
    lines = _read()
    pre = []
    sections = {}
    current = None
    buf = []
    for line in lines:
        m = IS_CATEGORY.match(line)
        if m:
            if current is None and not sections:
                pre = buf
            elif current is not None:
                sections[current] = buf
            current = m.group(1).strip()
            buf = [line]
        else:
            buf.append(line)
    if current is not None:
        sections[current] = buf

    new_lines = list(pre)
    written = set()
    for name in order:
        if name in sections:
            new_lines.extend(sections[name])
            written.add(name)
    for name, block in sections.items():
        if name not in written:
            new_lines.extend(block)
    _write(new_lines)
    return True


def reorder_topics(category_name, order):
    lines = _read()
    cat_start, cat_end = _find_category(lines, category_name)
    if cat_start is None:
        return False

    cat_header = [lines[cat_start]]
    pre_topics = []
    topics = {}
    current = None
    buf = []

    for line in lines[cat_start + 1:cat_end]:
        m = IS_TOPIC.match(line)
        if m:
            if current is None and not topics:
                pre_topics = buf
            elif current is not None:
                topics[current] = buf
            current = m.group(1).strip()
            buf = [line]
        else:
            buf.append(line)
    if current is not None:
        topics[current] = buf

    new_cat = cat_header + pre_topics
    written = set()
    for name in order:
        if name in topics:
            new_cat.extend(topics[name])
            written.add(name)
    for name, block in topics.items():
        if name not in written:
            new_cat.extend(block)

    lines[cat_start:cat_end] = new_cat
    _write(lines)
    return True


def add_category(name):
    lines = _read()
    for line in lines:
        m = IS_CATEGORY.match(line)
        if m and m.group(1).strip() == name:
            return False, 'already exists'
    if lines and lines[-1].strip():
        lines.append('\n')
    lines.append(f'## Category: {name}\n')
    _write(lines)
    return True, None


def add_topic(category_name, topic_name):
    lines = _read()
    start, end = _find_category(lines, category_name)
    if start is None:
        return False, 'category not found'
    for line in lines[start:end]:
        m = IS_TOPIC.match(line)
        if m and m.group(1).strip() == topic_name:
            return False, 'topic already exists'
    lines[end:end] = [f'### Topic: {topic_name}\n']
    _write(lines)
    return True, None


def add_entry(topic_name, date, summary, detail, subtopic_name=None):
    lines = _read()
    if subtopic_name:
        s_start, _ = _find_subtopic(lines, topic_name, subtopic_name)
        if s_start is None:
            return False, 'subtopic not found'
        entry_start, _, _ = _find_entry(lines, topic_name, date, subtopic_name)
        if entry_start is not None:
            return False, 'an entry for this date already exists'
        insert_at = s_start + 1
    else:
        start, _ = _find_topic(lines, topic_name)
        if start is None:
            return False, 'topic not found'
        entry_start, _, _ = _find_entry(lines, topic_name, date)
        if entry_start is not None:
            return False, 'an entry for this date already exists'
        insert_at = start + 1
    new_lines = [f'- **{date}** — {summary}\n']
    if detail.strip():
        for dl in detail.strip().split('\n'):
            new_lines.append(f'  {dl}\n')
    lines[insert_at:insert_at] = new_lines
    _write(lines)
    return True, None


def add_subtopic(topic_name, subtopic_name):
    lines = _read()
    start, end = _find_topic(lines, topic_name)
    if start is None:
        return False, 'topic not found'
    for i in range(start + 1, end):
        m = IS_SUBTOPIC.match(lines[i])
        if m and m.group(1).strip() == subtopic_name:
            return False, 'subtopic already exists'
    lines[end:end] = [f'#### Subtopic: {subtopic_name}\n']
    _write(lines)
    return True, None


def delete_subtopic(topic_name, subtopic_name):
    lines = _read()
    start, end = _find_subtopic(lines, topic_name, subtopic_name)
    if start is None:
        return False, False, False
    del lines[start:end]
    topic_deleted = False
    category_deleted = False
    t_start, t_end = _find_topic(lines, topic_name)
    if t_start is not None and _topic_is_empty(lines, t_start, t_end):
        del lines[t_start:t_end]
        topic_deleted = True
        lines, category_deleted = _delete_category_if_empty(lines, t_start)
    _write(lines)
    return True, topic_deleted, category_deleted


def rename_subtopic(topic_name, old_name, new_name):
    lines = _read()
    start, _ = _find_subtopic(lines, topic_name, old_name)
    if start is None:
        return False
    m = IS_SUBTOPIC.match(lines[start])
    lines[start] = lines[start][:m.start(1)] + new_name + '\n'
    _write(lines)
    return True


def reorder_subtopics(topic_name, order):
    lines = _read()
    t_start, t_end = _find_topic(lines, topic_name)
    if t_start is None:
        return False

    pre_sub = []
    subtopics = {}
    current = None
    buf = []

    for line in lines[t_start + 1:t_end]:
        m = IS_SUBTOPIC.match(line)
        if m:
            if current is None and not subtopics:
                pre_sub = buf
            elif current is not None:
                subtopics[current] = buf
            current = m.group(1).strip()
            buf = [line]
        else:
            buf.append(line)
    if current is not None:
        subtopics[current] = buf

    new_topic = [lines[t_start]] + pre_sub
    written = set()
    for name in order:
        if name in subtopics:
            new_topic.extend(subtopics[name])
            written.add(name)
    for name, block in subtopics.items():
        if name not in written:
            new_topic.extend(block)

    lines[t_start:t_end] = new_topic
    _write(lines)
    return True


# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self._json(400, {'ok': False, 'error': f'Bad request: {e}'}); return

        try:
            p = self.path
            if p == '/api/delete-entry':
                ok, sd, td, cd = delete_entry(
                    body.get('topic', '').strip(),
                    body.get('date', '').strip(),
                    body.get('subtopic', '').strip() or None,
                )
                self._json(200 if ok else 404, {
                    'ok': ok, 'subtopicDeleted': sd, 'topicDeleted': td, 'categoryDeleted': cd,
                })

            elif p == '/api/delete-topic':
                ok, cd = delete_topic(body.get('topic', '').strip())
                self._json(200 if ok else 404, {'ok': ok, 'categoryDeleted': cd})

            elif p == '/api/rename-topic':
                ok = rename_topic(body.get('topic', '').strip(), body.get('newName', '').strip())
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/update-entry':
                ok = update_entry(
                    body.get('topic', '').strip(),
                    body.get('date', '').strip(),
                    body.get('summary', '').strip(),
                    body.get('detail', ''),
                    body.get('subtopic', '').strip() or None,
                )
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/delete-category':
                ok = delete_category(body.get('category', '').strip())
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/rename-category':
                ok = rename_category(body.get('category', '').strip(), body.get('newName', '').strip())
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/reorder-categories':
                ok = reorder_categories(body.get('order', []))
                self._json(200 if ok else 400, {'ok': ok})

            elif p == '/api/reorder-topics':
                ok = reorder_topics(body.get('category', '').strip(), body.get('order', []))
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/add-category':
                ok, err = add_category(body.get('name', '').strip())
                self._json(200 if ok else 409, {'ok': ok, 'error': err})

            elif p == '/api/add-topic':
                ok, err = add_topic(body.get('category', '').strip(), body.get('name', '').strip())
                self._json(200 if ok else 409, {'ok': ok, 'error': err})

            elif p == '/api/add-entry':
                ok, err = add_entry(
                    body.get('topic', '').strip(),
                    body.get('date', '').strip(),
                    body.get('summary', '').strip(),
                    body.get('detail', ''),
                    body.get('subtopic', '').strip() or None,
                )
                self._json(200 if ok else 404, {'ok': ok, 'error': err})

            elif p == '/api/add-subtopic':
                ok, err = add_subtopic(body.get('topic', '').strip(), body.get('name', '').strip())
                self._json(200 if ok else 409, {'ok': ok, 'error': err})

            elif p == '/api/delete-subtopic':
                ok, td, cd = delete_subtopic(body.get('topic', '').strip(), body.get('subtopic', '').strip())
                self._json(200 if ok else 404, {'ok': ok, 'topicDeleted': td, 'categoryDeleted': cd})

            elif p == '/api/rename-subtopic':
                ok = rename_subtopic(
                    body.get('topic', '').strip(),
                    body.get('subtopic', '').strip(),
                    body.get('newName', '').strip(),
                )
                self._json(200 if ok else 404, {'ok': ok})

            elif p == '/api/reorder-subtopics':
                ok = reorder_subtopics(body.get('topic', '').strip(), body.get('order', []))
                self._json(200 if ok else 404, {'ok': ok})

            else:
                self._json(404, {'ok': False, 'error': 'Unknown endpoint'})

        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if args and str(args[1]) not in ('200', '304'):
            super().log_message(fmt, *args)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f'Serving at http://localhost:{PORT}/index.html')
        httpd.serve_forever()
