import xml.etree.ElementTree as ET
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize(
    "path,content_type",
    [
        ("/newest.rss", "application/rss+xml"),
        ("/newest.atom", "application/atom+xml"),
        ("/hottest.rss", "application/rss+xml"),
        ("/hottest.atom", "application/atom+xml"),
        ("/t/python,java.rss", "application/rss+xml"),
        ("/t/python,java.atom", "application/atom+xml"),
    ],
)
def test_feed_endpoints_return_correct_content_type(client, stories, path, content_type):
    with patch("main.fetch_stories", AsyncMock(return_value=stories)):
        r = client.get(path)
    assert r.status_code == 200
    assert content_type in r.headers["content-type"]


def test_invalid_format_returns_422(client):
    r = client.get("/newest.xml")
    assert r.status_code == 422


def test_min_comments_reduces_item_count(client, stories):
    with patch("main.fetch_stories", AsyncMock(return_value=stories)):
        r_all = client.get("/newest.rss")
        r_filtered = client.get("/newest.rss?min_comments=10")

    all_items = len(ET.fromstring(r_all.content).findall(".//item"))
    filtered_items = len(ET.fromstring(r_filtered.content).findall(".//item"))
    assert filtered_items < all_items


def test_min_score_reduces_item_count(client, stories):
    with patch("main.fetch_stories", AsyncMock(return_value=stories)):
        r_all = client.get("/newest.rss")
        r_filtered = client.get("/newest.rss?min_score=30")

    all_items = len(ET.fromstring(r_all.content).findall(".//item"))
    filtered_items = len(ET.fromstring(r_filtered.content).findall(".//item"))
    assert filtered_items < all_items


def test_q_reduces_item_count(client, stories):
    with patch("main.fetch_stories", AsyncMock(return_value=stories)):
        r_all = client.get("/newest.rss")
        r_filtered = client.get("/newest.rss?q=python")

    all_items = len(ET.fromstring(r_all.content).findall(".//item"))
    filtered_items = len(ET.fromstring(r_filtered.content).findall(".//item"))
    assert filtered_items < all_items


def test_healthz(client):
    assert client.get("/healthz").status_code == 200
