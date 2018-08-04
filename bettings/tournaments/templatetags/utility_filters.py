import re
from django import template

register = template.Library()


def get_fraction_html(value):
    if value == 0:
        return ""
    elif value == 0.25:
        return "<sup>1</sup>&frasl;<sub>4</sub>"
    elif value == 0.5:
        return "<sup>1</sup>&frasl;<sub>2</sub>"
    else:
        return "<sup>3</sup>&frasl;<sub>4</sub>"


@register.filter(name="display_odds")
def display_odds_filter(value: float):
    if value == 0:
        return "0 : 0"
    else:
        positive_value = abs(value)
        whole = int(positive_value)
        fraction = round(positive_value - whole, 2)
        fraction_html = get_fraction_html(fraction)
        if value > 0:
            if whole == 0:
                return "0 : {}".format(fraction_html)
            return "0 : {}{}".format(whole, fraction_html)
        else:
            if whole == 0:
                return "{} : 0".format(fraction_html)
            return "{}{} : 0".format(whole, fraction_html)


@register.filter(name="display_result")
def display_result_filter(match_result):
    if match_result:
        return "{} - {}".format(match_result.home_goals, match_result.guest_goals)
    else:
        return "-- : --"


@register.filter(name="remove_page")
def get_url_with_query_paging(url):
    url = str(url)
    url = re.sub("&page=\d+", "", url, 1)
    if "?" not in url:
        url += "?"
    return url
