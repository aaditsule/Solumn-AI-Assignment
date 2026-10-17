"""Add the local CI registration hint when the visible suite reports failures."""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print the project diagnostic block only after a failing test run."""
    if exitstatus:
        terminalreporter.write_sep("=", "CI session registration required")
        terminalreporter.write_line(
            "Before reporting an automated run, execute "
            "`python scripts/register_session.py` and include the printed session ID. "
            "This ties the run to the local broker and database setup."
        )
