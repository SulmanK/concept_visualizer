"""Tests for JWT utility functions."""

import base64
import json
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt
from jose.exceptions import JWTError

from app.utils.jwt_utils import create_supabase_jwt, create_supabase_jwt_for_storage, decode_token, extract_user_id_from_token, verify_jwt


class TestJwtUtils:
    """Tests for JWT utility functions."""

    @patch("app.utils.jwt_utils.settings")
    @patch("app.utils.jwt_utils.jwt.encode")
    @patch("app.utils.jwt_utils.time.time")
    def test_create_supabase_jwt(self, mock_time: MagicMock, mock_encode: MagicMock, mock_settings: MagicMock) -> None:
        """Test create_supabase_jwt function."""
        # Setup
        mock_time.return_value = 1000000000
        mock_settings.SUPABASE_JWT_SECRET = "test_jwt_secret"
        mock_encode.return_value = "encoded_jwt_token"
        user_id = "test_user_123"
        expiry_seconds = 3600  # 1 hour

        # Execute
        result = create_supabase_jwt(user_id, expiry_seconds)

        # Assert
        expected_payload = {
            "iat": 1000000000,
            "exp": 1000000000 + expiry_seconds,
            "sub": user_id,
            "role": "authenticated",
            "aud": "authenticated",
            "user_metadata": {
                "user_id": user_id,
            },
            "user_id": user_id,
        }
        mock_encode.assert_called_once_with(expected_payload, mock_settings.SUPABASE_JWT_SECRET, algorithm="HS256")
        assert result == "encoded_jwt_token"

    @patch("app.utils.jwt_utils.settings")
    @patch("app.utils.jwt_utils.jwt.decode")
    def test_verify_jwt_valid(self, mock_decode: MagicMock, mock_settings: MagicMock) -> None:
        """Test verify_jwt with valid token."""
        # Setup
        mock_settings.SUPABASE_JWT_SECRET = "test_jwt_secret"
        expected_claims = {"user_id": "test_user_123", "exp": 9999999999}
        mock_decode.return_value = expected_claims

        # Execute
        result = verify_jwt("valid_token")

        # Assert
        mock_decode.assert_called_once_with("valid_token", mock_settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
        assert result == expected_claims

    @patch("app.utils.jwt_utils.settings")
    @patch("app.utils.jwt_utils.jwt.decode")
    def test_verify_jwt_expired(self, mock_decode: MagicMock, mock_settings: MagicMock) -> None:
        """Test verify_jwt with expired token."""
        # Setup
        mock_settings.SUPABASE_JWT_SECRET = "test_jwt_secret"
        mock_decode.side_effect = jwt.ExpiredSignatureError()

        # Execute and Assert
        with pytest.raises(ValueError, match="JWT token has expired"):
            verify_jwt("expired_token")

    @patch("app.utils.jwt_utils.settings")
    @patch("app.utils.jwt_utils.jwt.decode")
    def test_verify_jwt_invalid(self, mock_decode: MagicMock, mock_settings: MagicMock) -> None:
        """Test verify_jwt with invalid token."""
        # Setup
        mock_settings.SUPABASE_JWT_SECRET = "test_jwt_secret"
        mock_decode.side_effect = JWTError("Invalid token")

        # Execute and Assert
        with pytest.raises(ValueError, match="Invalid JWT token"):
            verify_jwt("invalid_token")

    @patch("app.utils.jwt_utils.verify_jwt")
    def test_extract_user_id_from_token_with_validate_sub_claim(self, mock_verify_jwt: MagicMock) -> None:
        """Test extract_user_id_from_token with validation and sub claim."""
        # Setup
        mock_verify_jwt.return_value = {"sub": "test_user_123"}

        # Execute
        result = extract_user_id_from_token("valid_token", validate=True)

        # Assert
        mock_verify_jwt.assert_called_once_with("valid_token")
        assert result == "test_user_123"

    @patch("app.utils.jwt_utils.verify_jwt")
    def test_extract_user_id_from_token_with_validate_user_id_claim(self, mock_verify_jwt: MagicMock) -> None:
        """Test extract_user_id_from_token with validation and user_id claim."""
        # Setup
        mock_verify_jwt.return_value = {"user_id": "test_user_123"}

        # Execute
        result = extract_user_id_from_token("valid_token", validate=True)

        # Assert
        mock_verify_jwt.assert_called_once_with("valid_token")
        assert result == "test_user_123"

    @patch("app.utils.jwt_utils.verify_jwt")
    def test_extract_user_id_from_token_with_validate_metadata_claim(self, mock_verify_jwt: MagicMock) -> None:
        """Test extract_user_id_from_token with validation and user_metadata claim."""
        # Setup
        mock_verify_jwt.return_value = {"user_metadata": {"user_id": "test_user_123"}}

        # Execute
        result = extract_user_id_from_token("valid_token", validate=True)

        # Assert
        mock_verify_jwt.assert_called_once_with("valid_token")
        assert result == "test_user_123"

    @patch("app.utils.jwt_utils.verify_jwt")
    def test_extract_user_id_from_token_with_validate_no_id(self, mock_verify_jwt: MagicMock) -> None:
        """Test extract_user_id_from_token with validation but no user ID."""
        # Setup
        mock_verify_jwt.return_value = {"other_claim": "value"}

        # Execute
        result = extract_user_id_from_token("valid_token", validate=True)

        # Assert
        mock_verify_jwt.assert_called_once_with("valid_token")
        assert result is None

    @patch("app.utils.jwt_utils.decode_token")
    def test_extract_user_id_from_token_without_validate(self, mock_decode_token: MagicMock) -> None:
        """Test extract_user_id_from_token without validation."""
        # Setup
        mock_decode_token.return_value = {"user_id": "test_user_123"}

        # Execute
        result = extract_user_id_from_token("valid_token", validate=False)

        # Assert
        mock_decode_token.assert_called_once_with("valid_token")
        assert result == "test_user_123"

    @patch("app.utils.jwt_utils.settings")
    @patch("app.utils.jwt_utils.jwt.encode")
    @patch("app.utils.jwt_utils.time.time")
    def test_create_supabase_jwt_for_storage(self, mock_time: MagicMock, mock_encode: MagicMock, mock_settings: MagicMock) -> None:
        """Test create_supabase_jwt_for_storage function."""
        # Setup
        mock_time.return_value = 1000000000
        mock_settings.SUPABASE_JWT_SECRET = "test_jwt_secret"
        mock_encode.return_value = "encoded_storage_jwt"
        path = "/storage/path/test.jpg"
        expiry_timestamp = 1000086400  # 1 day later

        # Execute
        result = create_supabase_jwt_for_storage(path, expiry_timestamp)

        # Assert
        expected_payload = {"url": path, "iat": 1000000000, "exp": expiry_timestamp}
        mock_encode.assert_called_once_with(expected_payload, mock_settings.SUPABASE_JWT_SECRET, algorithm="HS256")
        assert result == "encoded_storage_jwt"

    def test_decode_token_valid(self) -> None:
        """Test decode_token with valid token."""
        # Setup - create a valid token structure manually
        payload = {"user_id": "test_user_123", "exp": 9999999999}
        payload_json = json.dumps(payload)
        payload_base64 = base64.b64encode(payload_json.encode()).decode().rstrip("=")
        token = f"header.{payload_base64}.signature"

        # Execute
        result = decode_token(token)

        # Assert
        assert result == payload

    def test_decode_token_invalid_format(self) -> None:
        """Test decode_token with invalid token format."""
        # Execute
        result = decode_token("invalid_token_format")

        # Assert
        assert result is None

    def test_decode_token_invalid_base64(self) -> None:
        """Test decode_token with invalid base64 encoding."""
        # Setup - create a token with invalid base64
        token = "header.not_base64.signature"

        # Execute
        result = decode_token(token)

        # Assert
        assert result is None

    def test_decode_token_invalid_json(self) -> None:
        """Test decode_token with invalid JSON payload."""
        # Setup - create a token with valid base64 but invalid JSON
        invalid_json = "not json"
        payload_base64 = base64.b64encode(invalid_json.encode()).decode()
        token = f"header.{payload_base64}.signature"

        # Execute
        result = decode_token(token)

        # Assert
        assert result is None
