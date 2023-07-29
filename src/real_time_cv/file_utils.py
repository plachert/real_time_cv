from __future__ import annotations

import tempfile


def save_file(uploaded_file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.getbuffer())
    filename = temp_file.name
    return filename
