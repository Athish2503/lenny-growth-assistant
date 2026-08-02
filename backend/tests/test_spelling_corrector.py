import pytest
from app.retrieval.spelling_corrector import spelling_corrector


def test_spelling_corrector_ami_cora():
    query = "Who in Ami Cora"
    corrected, corrections = spelling_corrector.correct_query(query)
    assert "Ami Vora" in corrected
    assert "who is" in corrected.lower()
    assert "Ami Cora" in corrections or "Ami" in str(corrections)


def test_spelling_corrector_brian_cheskyy():
    query = "tell me about brian cheskyy"
    corrected, corrections = spelling_corrector.correct_query(query)
    assert "Brian" in corrected or "Chesky" in corrected


def test_spelling_corrector_guilermo_rauch():
    query = "what did guilermo rauch say about nextjs"
    corrected, corrections = spelling_corrector.correct_query(query)
    assert "Guillermo Rauch" in corrected or "Rauch" in corrected


def test_spelling_corrector_exact_query():
    query = "Who is Brian Chesky?"
    corrected, corrections = spelling_corrector.correct_query(query)
    assert "Brian Chesky" in corrected
