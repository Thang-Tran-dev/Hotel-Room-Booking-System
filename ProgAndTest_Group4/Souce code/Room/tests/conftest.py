import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config, app

def _fresh_database(tmp_path, monkeypatch):
    monkeypatch.setattr(config.Config, 'DB', str(tmp_path / 'test.db'))     # every test gets its own empty, seeded database
    app.hotel.db.setup()

@pytest.fixture
def h(tmp_path, monkeypatch):
    """The `Hotel` object (repositories + services) inside a request context – for unit tests of actors / services."""
    _fresh_database(tmp_path, monkeypatch)
    with app.A.test_request_context(): yield app.hotel

@pytest.fixture
def client(tmp_path, monkeypatch):
    """A browser-like test client – for tests of the HTML pages."""
    _fresh_database(tmp_path, monkeypatch); return app.A.test_client()
