# Tests for user schema validation.

import pytest

from app.schemas.user import validate_password_policy


@pytest.mark.parametrize(
    "password,error_message",
    [
        ("alllowercase123!", "uppercase"),
        ("ALLUPPERCASE123!", "lowercase"),
        ("NoNumbersHere!", "number"),
        ("NoSpecialChars123", "special character"),
        ("Contains Space1!", "must not contain spaces"),
    ],
)
def test_validate_password_policy_rejects_invalid_patterns(password: str, error_message: str):
    with pytest.raises(ValueError, match=error_message):
        validate_password_policy(password)
