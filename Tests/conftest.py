import math
import os
import platform
import re
import sys
import time
import pluggy
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--myVerbose",
        action="store",
        default=1,
        help="my verbose level"
    )
    parser.addoption(
        "--port",
        action="store",
        default=None,
        help="port to test"
    )

def line_separator(interrupter: str, symbol: str = "-", length: int = 80) -> str:
    if not interrupter:
        return symbol * length
    interrupterNoColor = re.sub(r'\033\[[0-9;]*m', '', interrupter)
    side = (length - 2 - len(interrupterNoColor)) / 2
    return symbol * math.ceil(side) + " " + interrupter + " " + symbol * math.floor(side)

def setup_logger(port):
    # set up fie location for output logs
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%m-%d-%Y__%H-%M-%S")
    subfolder = os.path.join(log_folder, timestamp)
    os.makedirs(subfolder, exist_ok=True)
    log_file_path = os.path.join(subfolder, f"test_{port}.log")

    from Classes.Logger import Logger
    return Logger(port, "Test Printer", consoleLogger=sys.stdout, fileLogger=log_file_path, showFile=False, showLevel=False)

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session) -> None:
    session.config.start_time = time.time()
    session.config.passed_count = 0
    session.config.failed_count = 0
    session.config.skipped_count = 0
    session.config.xfailed_count = 0
    session.config.xpassed_count = 0
    session.config.failNames = []
    session.config.fails = {}
    session.config.logger = setup_logger(session.config.port)

    if session.config.verbosity > 0:
        logger = session.config.logger
        logger.logMessageOnly("\033[1m" + line_separator("test session starts", symbol="=") + "\033[0m")
        verinfo = platform.python_version()
        msg = f"platform {sys.platform} -- Python {verinfo}"
        pypy_version_info = getattr(sys, "pypy_version_info", None)
        if pypy_version_info:
            verinfo = ".".join(map(str, pypy_version_info[:3]))
            msg += f"[pypy-{verinfo}-{pypy_version_info[3]}]"
        msg += f", pytest-{pytest.__version__}, pluggy-{pluggy.__version__}"
        logger.logMessageOnly(msg)
        logger.logMessageOnly(f"rootdir: {session.config.rootdir}")

def pytest_collection_modifyitems(session, config, items):
    session.config.logger.logMessageOnly(f"\033[1m...collected {len(items)} items...", end="\n")

def pytest_sessionfinish(session, exitstatus) -> None:
    session_duration = time.time() - session.config.start_time
    passes  = session.config.passed_count
    fails   = session.config.failed_count
    skips   = session.config.skipped_count
    xfails  = session.config.xfailed_count
    xpasses = session.config.xpassed_count
    logger  = session.config.logger

    summary = ""
    stats = []
    if passes > 0: stats.append(f"\033[32m\033[1m{passes} passed")
    if fails > 0: stats.append(f"\033[31m\033[1m{fails} failed")
    if skips > 0: stats.append(f"\033[33m{skips} skipped")
    if xfails > 0: stats.append(f"\033[33m{xfails} xfailed")
    if xpasses > 0: stats.append(f"\031[33m{xpasses} xpassed")

    if len(stats) > 0:
        summary = ", ".join(stats)
    else:
        summary = "\033[33mno tests ran"

    summary += f"\033[32m in {session_duration:.2f}s"
    if session_duration > 3600:
        summary += f" ({session_duration // 3600:.0f}:{session_duration % 3600 // 60:.0f}:{session_duration % 60:.2f})"
    elif session_duration > 60:
        summary += f" ({session_duration // 60:.0f}:{session_duration % 60:.2f})"

    if session.config.failed_count > 0:
        headerText = "\n" + line_separator("FAILURES", symbol="=")
        logger.logMessageOnly(headerText, logLevel=logger.ERROR)
        for failTest in session.config.failNames:
            logger.logMessageOnly(line_separator(failTest, symbol="_"), end="\n", logLevel=logger.ERROR)
            #todo: break this out into something that can be called anywhere for the Logger class
            things = list(session.config.fails[failTest].reprtraceback.reprentries[0].reprfuncargs.args)
            for args in things:
                logger.logMessageOnly(f"{args[0]} = {args[1]}")
            logger.logMessageOnly("")
            for line in list(session.config.fails[failTest].reprtraceback.reprentries[0].lines):
                if line.startswith("E") or line.startswith(">"):
                    logger.logMessageOnly(line.__str__(), logLevel=logger.ERROR)
                else:
                    logger.logMessageOnly(line.__str__())
            loc = session.config.fails[failTest].reprtraceback.reprentries[0].reprfileloc
            logger.logMessageOnly("\n" + loc.path + ":" + loc.lineno.__str__() + ": " + loc.message, logLevel=logger.ERROR)

    logger.logMessageOnly("\n\033[32m" + line_separator(summary, symbol="="))

def pytest_configure(config):
    for arg in config.invocation_params.args:
        if not hasattr(config, "verbosity") and arg.startswith("--myVerbose="):
            config.verbosity = int(arg.split("=")[1])
        elif not hasattr(config, "port") and arg.startswith("--port="):
            config.port = arg.split("=")[1]
        elif not hasattr(config, "testLevel") and arg.startswith("--testLevel="):
            config.testLevel = int(arg.split("=")[1])
    if config.verbosity > 2:
        config.verbosity = 2

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()  # Retrieve the TestReport object
    # Only check the outcome after the "call" phase (i.e., after the test ran)

    if (report.when == "setup" and report.skipped) or (report.when == "call"):
        if report.passed:
            if hasattr(report, "wasxfail"):
                report.outcome = "xpassed"
                report.xpassed = True
                item.config.xpassed_count += 1
            else:
                item.config.passed_count += 1
        elif report.failed:
            item.config.failed_count += 1
            failName = report.nodeid.split("::")[1] + "." + item.name
            item.config.failNames.append(failName)
            item.config.fails[failName] = report.longrepr
        elif report.skipped:
            if hasattr(report, "wasxfail"):
                report.outcome = "xfailed"
                report.xfailed = True
                item.config.xfailed_count += 1
            else:
                item.config.skipped_count += 1
    report.port = item.config.port
    report.verbosity = item.config.verbosity
    report.logger = item.config.logger

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_logreport(report):
    verbosity = report.verbosity
    yield
    logger = report.logger
    port = report.port
    if (report.when == "setup" and report.skipped) or (report.when == "call"):
        if port is None and "test_runner.py::TestFabricator::" in report.nodeid:
            # Retrieve port from the test function if it's set as an attribute
            from test_runner import fabricator_setup
            port = fabricator_setup(os.getenv("PORT")).devicePort

        if verbosity == 0:
            if report.passed:
                logger.info("\033[32m.\033[0m")
            elif report.failed:
                logger.info("\033[31mF\033[0m")
            elif report.skipped:
                logger.info("\033[33ms\033[0m")
            elif hasattr(report, "xfailed") and report.xfailed:
                logger.info("\033[33mX\033[0m")
            elif hasattr(report, "xpassed") and report.xpassed:
                logger.info("\033[31mx\033[0m")
        elif verbosity == 1:
            loc = report.nodeid.split("::")[-1]
            testString = f"{loc}[{port}]{' ' * (27 - len(loc) - len(str(port)) - 2)}"
            if report.passed:
                logger.info(f"{testString} \033[32mPASSED\033[0m")
            elif report.failed:
                logger.info(f"{testString} \033[31mFAILED\033[0m")
            elif report.skipped:
                logger.info(f"{testString} \033[33mSKIPPED\033[0m")
            elif hasattr(report, "xfailed") and report.xfailed:
                logger.info(f"{testString} \033[33mXFAILED\033[0m")
            elif hasattr(report, "xpassed") and report.xpassed:
                logger.info(f"{testString} \033[31mXPASSED\033[0m")
        elif verbosity >= 2:
            loc = report.nodeid
            testString = f"{loc}[{port}]{' ' * (59 - len(loc) - len(str(port)) - 2)}"
            if report.passed:
                logger.info(f"{testString} \033[32mPASSED\033[0m")
            elif report.failed:
                logger.info(f"{testString} \033[31mFAILED\033[0m:\n\n {report.longrepr}")
            elif report.skipped:
                logger.info(f"{testString} \033[33mSKIPPED\033[0m: {report.longrepr[-1].split('Skipped: ')[-1]}")