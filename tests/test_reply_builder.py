from tony.core.reply_builder import ReplyBuilder


def test_reply_builder_blocked_reply_is_natural():
    reply = ReplyBuilder().blocked("reading .env files is not allowed")

    assert "I blocked that" in reply
    assert "reading .env files" in reply


def test_reply_builder_approval_reply_is_natural():
    reply = ReplyBuilder().approval("git push")

    assert "needs your approval" in reply
    assert "Type yes" in reply


def test_reply_builder_completed_reply_is_natural():
    reply = ReplyBuilder().completed("On branch main")

    assert "Done, Muhammad Afzal" in reply
    assert "On branch main" in reply


def test_reply_builder_clarification_reply_is_natural():
    reply = ReplyBuilder().clarification("which project folder should I use?")

    assert "I need one detail" in reply
    assert "which project folder" in reply
