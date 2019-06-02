def test_missing_params(client):
    resp = client.post("/api/new", data={})
    assert resp.status_code == 400


def test_non_real_datasource(client):
    resp = client.post(
        "/api/new",
        data={"datasource": "foobar", "transformer": "GenericTrasnformer", "comment": "test"},
    )
    assert resp.status_code == 400
    assert "is invalid" in resp.json["message"]


def test_misisng_params(client):
    resp = client.post(
        "/api/new",
        data={"datasource": "HXTriage", "transformer": "GenericTransformer", "comment": "test"},
    )
    assert resp.status_code == 400
    assert "Missing" in resp.json["message"]
