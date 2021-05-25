from typing import List, Tuple, Dict, Any

from indra.assemblers.html.assembler import DEFAULT_SOURCE_COLORS, loader
from indra.assemblers.html.css_assembler import SourceBadgeStyleSheet, \
    StmtsViewStyleSheet, BaseTemplateStyleSheet


def index_yielder(string: str, find: str):
    """Yield indices of matched string, -1 if no match"""
    match = 0
    while string:
        match = string.find(find, match)
        if match <= -1:
            raise StopIteration
        yield match
        match += len(find)


def _source_badge_in_str(css_str: str,
                         source_colors: List[Tuple[str, Dict[str, Any]]]) ->\
        bool:
    # Loop all the colors and test if they are in the generated stylesheet str
    for category, data in source_colors:
        for source, font_color in data['sources'].items():
            style_str = f".source-{source} " \
                        "{\n" \
                        f"    background-color: {font_color};\n" \
                        f"    color: {data['color']};\n" \
                        "}"
            assert style_str in css_str
    return True


def test_source_badge_sheet():
    sbss = SourceBadgeStyleSheet()
    css_str = sbss.make_model()
    assert _source_badge_in_str(css_str, DEFAULT_SOURCE_COLORS)


def test_base_template_sheet():
    btss_simple = BaseTemplateStyleSheet(simple=False)
    css_str = btss_simple.make_model()
    assert _source_badge_in_str(css_str, DEFAULT_SOURCE_COLORS)

    # Test base template styling
    template, _, _ = loader.get_source(None, 'template_stylesheet_macros.css')
    assert isinstance(template, str)
    iy_macro = index_yielder(template, '%}\n')
    _ = next(iy_macro)
    macro_start = next(iy_macro) + len('%}\n')

    css_str.startswith(template[macro_start:macro_start+900])

    iy_simple_start = template.find('{% if not simple %}\n')
    assert iy_simple_start > 0
    iy_simple_start += len('{% if not simple %}\n')
    iy_simple_end = template.find('{% endif %}\n')
    assert iy_simple_end > 0

    not_simple_str = template[iy_simple_start:iy_simple_end]
    assert not_simple_str in css_str
