from sample_order_system.view import colors


def test_colorize_wraps_text_with_color_and_reset():
    result = colors.colorize("hello", colors.RED)
    assert result == f"{colors.RED}hello{colors.RESET}"


def test_status_text_maps_known_statuses_to_distinct_colors():
    seen_colors = set()
    for status in ("RESERVED", "CONFIRMED", "PRODUCING", "RELEASE", "REJECTED"):
        text = colors.status_text(status)
        assert status in text
        seen_colors.add(colors.STATUS_COLORS[status])
    assert len(seen_colors) == 5


def test_status_text_passes_through_unknown_status_uncolored():
    text = colors.status_text("UNKNOWN")
    assert text == colors.colorize("UNKNOWN", "")


def test_tier_text_maps_known_tiers_to_distinct_colors():
    seen_colors = set()
    for tier in ("여유", "부족", "고갈"):
        text = colors.tier_text(tier)
        assert tier in text
        seen_colors.add(colors.TIER_COLORS[tier])
    assert len(seen_colors) == 3


def test_success_failure_muted_use_different_colors():
    assert colors.success("ok") == colors.colorize("ok", colors.GREEN)
    assert colors.failure("bad") == colors.colorize("bad", colors.RED)
    assert colors.muted("cancelled") == colors.colorize("cancelled", colors.DIM)
    assert colors.GREEN != colors.RED != colors.DIM


def test_enable_windows_ansi_does_not_raise():
    colors.enable_windows_ansi()
