import pytest
import mock
from beagle.datasources import SplunkSPLSearch


@mock.patch.object(SplunkSPLSearch, "setup_session")
def test_init(mock_method):
    SplunkSPLSearch(spl="search index=main | head 10")
    assert mock_method.called


@pytest.mark.parametrize(
    "spl,expected",
    [
        ("index=main | head 10", "search index=main | head 10"),
        ("search index=main | head 10", "search index=main | head 10"),
        ("|inputlookup foo.csv", "|inputlookup foo.csv"),
    ],
)
@mock.patch.object(SplunkSPLSearch, "setup_session")
def test_forces_search_appended(mock_method, spl, expected):
    op = SplunkSPLSearch(spl=spl)
    assert op.spl == expected
