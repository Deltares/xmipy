import logging
import os.path

import xmipy.logger
from xmipy import XmiWrapper


def test_logger_defaults(caplog, modflow_lib_path):
    mf6 = XmiWrapper(modflow_lib_path)

    assert mf6.logger.level == logging.NOTSET
    assert mf6.logger.name == os.path.basename(modflow_lib_path)

    mf6.logger.debug("not shown")
    assert len(caplog.record_tuples) == 0

    mf6.logger.info("also not shown")
    assert len(caplog.record_tuples) == 0

    mf6.logger.warning("warnings or higher are shown")
    assert len(caplog.record_tuples) == 1
    assert "warnings or higher are shown" in caplog.text


def test_logger_level(caplog, modflow_lib_path):
    mf6 = XmiWrapper(modflow_lib_path, logger_level="INFO")

    assert mf6.logger.level == logging.INFO

    mf6.logger.debug("not shown")
    assert len(caplog.record_tuples) == 0

    mf6.logger.info("this is shown")
    assert len(caplog.record_tuples) == 1
    assert "this is shown" in caplog.text


def test_show_logger_message(caplog, modflow_lib_path):
    mf6 = XmiWrapper(modflow_lib_path)

    with xmipy.logger.show_logger_message(mf6.logger):
        mf6.logger.debug("debug not shown")
        assert len(caplog.record_tuples) == 0

        mf6.logger.info("info now shown")
        assert len(caplog.record_tuples) == 1
        assert "info now shown" in caplog.text

    caplog.clear()

    mf6.logger.info("info not shown")
    assert len(caplog.record_tuples) == 0


def test_show_logger_message_lower_level(caplog, modflow_lib_path):
    mf6 = XmiWrapper(modflow_lib_path)

    mf6.logger.debug("debug not shown")
    assert len(caplog.record_tuples) == 0

    with xmipy.logger.show_logger_message(mf6.logger, logging.DEBUG):
        mf6.logger.debug("debug shown")
        assert len(caplog.record_tuples) == 1
        assert "debug shown" in caplog.text

    caplog.clear()

    mf6.logger.debug("debug not shown")
    assert len(caplog.record_tuples) == 0

    caplog.clear()

    # Use ignore_disabled=True which does not change outcome
    with xmipy.logger.show_logger_message(mf6.logger, logging.DEBUG, True):
        mf6.logger.debug("debug still shown")
        assert len(caplog.record_tuples) == 1
        assert "debug still shown" in caplog.text


def test_show_disabled_logger_message(caplog, modflow_lib_path):
    mf6 = XmiWrapper(modflow_lib_path)

    mf6.logger.disabled = True

    mf6.logger.warning("no warning")
    assert len(caplog.record_tuples) == 0

    # Use default ignore_disabled=False to never show messages
    with xmipy.logger.show_logger_message(mf6.logger, logging.WARNING):
        mf6.logger.info("info not shown")
        assert len(caplog.record_tuples) == 0

        mf6.logger.warning("warning not shown")
        assert len(caplog.record_tuples) == 0

    mf6.logger.critical("nothing critical")
    assert len(caplog.record_tuples) == 0

    # Use ignore_disabled=True to sometimes show messages
    with xmipy.logger.show_logger_message(mf6.logger, ignore_disabled=True):
        mf6.logger.debug("debug not shown")
        assert len(caplog.record_tuples) == 0

        mf6.logger.info("info shown")
        assert len(caplog.record_tuples) == 1
        assert "info shown" in caplog.text
