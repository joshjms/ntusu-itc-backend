from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import re
import os
from SUITC_Backend.settings import BASE_DIR


STORAGE_PATH = os.path.join(BASE_DIR, 'static/api-guide')


def list_entries():
    '''
    Returns a list of all names of api guide entries
    '''
    _, filenames = default_storage.listdir(STORAGE_PATH)
    return list(sorted(re.sub(r"\.md$", "", filename)
        for filename in filenames if filename.endswith(".md")))


def get_entry(title):
    '''
    Retrieves an api guide entry by its title.
    Returns None if not exist.
    '''
    try:
        f = default_storage.open(f"{STORAGE_PATH}/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def save_entry(title, content):
    '''
    Saves an api guide entry, given its title and Markdown content.
    Replace existing entry if same title already exists.
    '''
    filename = f"{STORAGE_PATH}/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))
