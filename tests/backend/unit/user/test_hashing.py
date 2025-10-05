# tests/unit/services/test_hashing.py
import pytest

from backend.src.services import user as user_service

#UNI-052/005
def test_hash_and_verify_normal_password():
    """
    Sanity check: hash a normal password and verify it.
    """
    password = "My$ecret123"
    hashed = user_service._hash_password(password)
    
    assert hashed, "_hash_password returned empty"
    assert user_service._verify_password(password, hashed) is True
    assert user_service._verify_password("wrongpass", hashed) is False

#UNI-052/006
def test_verify_with_invalid_inputs():
    """
    _verify_password should safely return False for invalid types.
    """
    hashed = user_service._hash_password("Normal1!")
    
    assert user_service._verify_password(None, hashed) is False
    assert user_service._verify_password("Normal1!", None) is False
    assert user_service._verify_password(None, None) is False

#UNI-052/007
def test_hash_password_type_error():
    """
    _hash_password should raise TypeError for non-string input.
    """
    with pytest.raises(TypeError):
        user_service._hash_password(None)
    with pytest.raises(TypeError):
        user_service._hash_password(12345)
