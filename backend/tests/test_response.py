import pytest
import httpx



def test_미팅요청을_확인할_수_있다():
    response = httpx.get("http://localhost:8000/meetings/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_미팅요청을_수락할_수_있다():
    pass

def test_미팅요청을_거절할_수_있다():
    pass


