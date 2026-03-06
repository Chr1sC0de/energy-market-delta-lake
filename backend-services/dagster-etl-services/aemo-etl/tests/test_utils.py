from unittest.mock import Mock

import pytest
from requests import HTTPError, Response

from aemo_etl.utils import request_get


def test_request_get_success() -> None:
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    mock_getter = Mock(return_value=mock_response)

    result = request_get("https://example.com", getter=mock_getter)

    assert result == mock_response
    mock_getter.assert_called_once_with("https://example.com")
    mock_response.raise_for_status.assert_called_once()


def test_request_get_raises_http_error() -> None:
    mock_response = Mock(spec=Response)
    mock_response.status_code = 404
    mock_response.raise_for_status = Mock(side_effect=HTTPError("Not Found"))

    mock_getter = Mock(return_value=mock_response)

    with pytest.raises(HTTPError):
        request_get("https://example.com/notfound", getter=mock_getter)

    mock_getter.assert_called_once_with("https://example.com/notfound")
    mock_response.raise_for_status.assert_called_once()
