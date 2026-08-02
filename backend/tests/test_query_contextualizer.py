import pytest
from app.retrieval.query_contextualizer import contextualize_query


def test_contextualize_query_no_history():
    query = "Who is Brian Chesky?"
    res = contextualize_query(query, history=None)
    assert res == "Who is Brian Chesky?"


def test_contextualize_query_with_pronoun_his():
    history = [
        {"role": "user", "content": "Who is Brian Chesky?"},
        {"role": "assistant", "content": "Brian Chesky is the co-founder and CEO of Airbnb."},
    ]
    query = "Summarize his advice."
    res = contextualize_query(query, history=history)
    assert "Brian Chesky" in res
    assert "Summarize his advice" in res


def test_contextualize_query_with_pronoun_he():
    history = [
        {"role": "user", "content": "Tell me about Brian Chesky"},
        {"role": "assistant", "content": "Brian Chesky leading Airbnb"},
    ]
    query = "What did he say about product design?"
    res = contextualize_query(query, history=history)
    assert "Brian Chesky" in res
    assert "What did he say about product design?" in res


def test_contextualize_query_self_contained():
    history = [
        {"role": "user", "content": "Who is Brian Chesky?"},
        {"role": "assistant", "content": "Brian Chesky is CEO of Airbnb."},
    ]
    query = "How does growth work at Airbnb?"
    res = contextualize_query(query, history=history)
    assert res == "How does growth work at Airbnb?"


def test_contextualize_query_lowercase_user_prompt():
    history = [
        {"role": "user", "content": "who is brian chesky"},
        {"role": "assistant", "content": "Brian Chesky is the co-founder and CEO of Airbnb."},
    ]
    query = "summarize his advice"
    res = contextualize_query(query, history=history)
    assert "brian chesky" in res.lower()
    assert "summarize his advice" in res.lower()
