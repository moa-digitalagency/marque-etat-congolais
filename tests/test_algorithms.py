import pytest
from algorithms.text_splitter import split_unit_name


def test_split_single_word():
    """Test with single word input"""
    result = split_unit_name("Ambassade")
    assert result == ["AMBASSADE"]


def test_split_two_words():
    """Test with two words"""
    result = split_unit_name("Ambassade RDC")
    assert result == ["AMBASSADE", "RDC"]


def test_split_long_name():
    """Test with long name (should split with up to 2 words per line)"""
    result = split_unit_name("Ambassade de la République Démocratique du Congo en France")
    assert len(result) <= 5
    assert result[0] == "AMBASSADE"
    assert "DE LA" in result[1]


def test_split_max_lines():
    """Test that output never exceeds 5 lines"""
    long_name = " ".join(["word"] * 20)
    result = split_unit_name(long_name)
    assert len(result) <= 5


def test_split_empty_string():
    """Test empty string returns empty list"""
    result = split_unit_name("")
    assert result == []


def test_split_whitespace_only():
    """Test whitespace-only string returns empty list"""
    result = split_unit_name("   ")
    assert result == []


def test_split_uppercase():
    """Test input is converted to uppercase"""
    result = split_unit_name("ambassade de france")
    assert all(line.isupper() for line in result)


def test_split_special_chars():
    """Test with special characters"""
    result = split_unit_name("Direction-Générale d'État")
    assert len(result) > 0
    assert any("DIRECTION" in line for line in result)
