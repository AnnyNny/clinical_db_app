from unittest.mock import MagicMock, patch

from database_utils import get_db_connection


def test_get_db_connection_success():
    with patch("database_utils.psycopg2.connect", return_value=MagicMock()) as mock_connect:
        conn = get_db_connection()
        mock_connect.assert_called_once()
        assert conn is not None, "Connection should not be None"


