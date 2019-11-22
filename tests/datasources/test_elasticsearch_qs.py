import pytest
import mock
from beagle.datasources import ElasticSearchQSSerach


@mock.patch.object(ElasticSearchQSSerach, "setup_session")
def test_init(mock_method):
    ElasticSearchQSSerach(index="logs-*", query="*")
    assert mock_method.called