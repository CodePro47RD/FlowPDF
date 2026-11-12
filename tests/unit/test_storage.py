import pytest
from engine.storage.local import LocalStorage
from engine.core.exceptions import StorageError


def test_local_storage_lifecycle(tmp_path):
    storage = LocalStorage(base_dir=tmp_path / "reports", base_url="/media/reports/")

    # 1. Save
    key = storage.save("invoices/2026/inv_01.pdf", b"%PDF-1.4 test content")
    assert key == "invoices/2026/inv_01.pdf"
    assert storage.exists(key)

    # 2. Read
    with storage.open(key) as f:
        content = f.read()
    assert content == b"%PDF-1.4 test content"

    # 3. URL
    url = storage.get_url(key)
    assert url == "/media/reports/invoices/2026/inv_01.pdf"

    # 4. Security: traversal
    with pytest.raises(StorageError):
        storage.save("../evil.pdf", b"bad")

    # 5. Delete
    assert storage.delete(key) is True
    assert storage.exists(key) is False
