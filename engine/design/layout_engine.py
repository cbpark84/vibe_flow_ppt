LAYOUT_RULES: dict[str, dict] = {
    "title": {
        "title_area":    (0.05, 0.28, 0.90, 0.28),
        "subtitle_area": (0.05, 0.60, 0.90, 0.16),
        "background":    "primary",
    },
    "bullets": {
        "title_area":    (0.04, 0.02, 0.92, 0.15),
        "content_area":  (0.06, 0.22, 0.88, 0.70),
        "max_items":     6,
        "title_bar":     (0.0,  0.0,  1.0,  0.18),
    },
    "two_column": {
        "title_area":    (0.04, 0.04, 0.92, 0.14),
        "left_area":     (0.03, 0.20, 0.44, 0.72),
        "right_area":    (0.53, 0.20, 0.44, 0.72),
    },
    "quote": {
        "deco_area":     (0.05, 0.08, 0.15, 0.20),
        "quote_area":    (0.10, 0.22, 0.80, 0.48),
        "source_area":   (0.10, 0.74, 0.80, 0.10),
        "background":    "primary",
        "font_size":     28,
    },
    "closing": {
        "title_area":    (0.05, 0.30, 0.90, 0.25),
        "contact_area":  (0.05, 0.60, 0.90, 0.14),
        "background":    "primary",
    },
}


def get_rules() -> dict:
    """전체 레이아웃 규칙 반환"""
    return LAYOUT_RULES
