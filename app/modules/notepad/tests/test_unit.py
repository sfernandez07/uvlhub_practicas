import pytest
from app.modules.conftest import login, logout
from app.modules.notepad.models import Notepad


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"


def test_list_empty_notepad_get(test_client):
    """
    Tests access to the empty notepad list via GET request.
    """
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/notepad")
    assert response.status_code == 200, "The notepad page could not be accessed."
    assert b"You have no notepads." in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_get_notepad_by_id(test_client):
    """
    Tests access to the view of a notepad via GET request.
    """
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    test_client.post("/notepad/create", data={"title": "Example", "body": "This is an example"}, follow_redirects=True)
    with test_client.application.app_context():
        note = Notepad.query.filter_by(title="Example").first()

    response = test_client.get(f"/notepad/{note.id}")
    assert response.status_code == 200
    assert b"Example" in response.data
    logout(test_client)


def test_create_notepad_post(test_client):
    """
    Tests the correct creation of a notepad via POST request.
    """
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post("/notepad/create", data={"title": "Example", "body": "This is an example"},
                                follow_redirects=True)
    assert response.status_code == 200

    page = test_client.get("notepad", follow_redirects=True)
    assert page.status_code == 200
    assert b"Example" in page.data
    logout(test_client)


def test_edit_notepad(test_client):
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200

    create_response = test_client.post("/notepad/create", data={"title": "Examle", "body": "This is an example"},
                                       follow_redirects=True)
    assert create_response.status_code == 200

    with test_client.application.app_context():
        notepad = Notepad.query.filter_by(title="Example").first()
        assert notepad is not None
        notepad_id = notepad.id

    edit_response = test_client.post(
        f"/notepad/edit/{notepad_id}",
        data={"title": "Example 2", "body": "This is not an example"},
        follow_redirects=True
    )
    assert edit_response.status_code == 200

    response_after = test_client.get("/notepad", follow_redirects=True)
    assert b"Example 2" in response_after.data


def test_delete_notepad(test_client):
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200

    create_response = test_client.post(
        "/notepad/create",
        data={"title": "Hola", "body": "This is an example"},
        follow_redirects=True
    )
    assert create_response.status_code == 200

    with test_client.application.app_context():
        notepad = Notepad.query.filter_by(title="Hola").first()
        assert notepad is not None
        notepad_id = notepad.id

    delete_response = test_client.post(
        f"/notepad/delete/{notepad_id}",
        follow_redirects=True
    )
    assert delete_response.status_code == 200

    response_after = test_client.get("/notepad", follow_redirects=True)
    assert b"Hola" not in response_after.data
