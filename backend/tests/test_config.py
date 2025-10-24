import os
import config


def test_mongodb_db_name_resolution(monkeypatch):
    # Ensure clean state
    monkeypatch.delenv('MONGODB_DB', raising=False)
    monkeypatch.delenv('MONGODB_DB_DEV', raising=False)
    monkeypatch.delenv('MONGODB_DB_PROD', raising=False)

    # Default when nothing is set
    monkeypatch.setenv('ENV', 'dev')
    # Reset any previously-loaded class attributes (tests may run in the same
    # interpreter where config was already imported). Ensure class attrs reflect
    # the intended empty env state.
    config.Config.MONGODB_DB = None
    config.Config.MONGODB_DB_DEV = None
    config.Config.MONGODB_DB_PROD = None
    config.Config.ENV = 'dev'
    assert config.Config.MONGODB_DB_NAME() == 'rhac_db'

    # MONGODB_DB set should be used
    monkeypatch.setenv('MONGODB_DB', 'common_db')
    config.Config.MONGODB_DB = 'common_db'
    assert config.Config.MONGODB_DB_NAME() == 'common_db'

    # Per-env overrides
    monkeypatch.setenv('MONGODB_DB_DEV', 'dev_db')
    monkeypatch.setenv('MONGODB_DB_PROD', 'prod_db')
    config.Config.MONGODB_DB_DEV = 'dev_db'
    config.Config.MONGODB_DB_PROD = 'prod_db'
    config.Config.ENV = 'dev'
    assert config.Config.MONGODB_DB_NAME() == 'dev_db'
    config.Config.ENV = 'prod'
    assert config.Config.MONGODB_DB_NAME() == 'prod_db'
