from safemodels import safe_hash


def test_hash_two_sources(sf_filename, pt_filename):
    sf_hash = safe_hash(sf_filename)
    pt_hash = safe_hash(pt_filename)
    assert sf_hash == pt_hash
