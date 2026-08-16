from app.ai.safety import minimise_sensitive_text


def test_redacts_card_like_number():
    cleaned, warnings = minimise_sensitive_text("My card is 4111 1111 1111 1111 and it was charged.")
    assert "4111" not in cleaned
    assert "REDACTED" in cleaned
    assert warnings


def test_leaves_normal_complaint_unchanged():
    text = "My transfer has not arrived and I need the payment traced."
    cleaned, warnings = minimise_sensitive_text(text)
    assert cleaned == text
    assert warnings == []
