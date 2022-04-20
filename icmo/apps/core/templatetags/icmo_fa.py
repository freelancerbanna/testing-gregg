from django import template

register = template.Library()


class SpinnerNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string

    def render(self, context):
        if self.format_string == "small":
            size = "fa-2x"
        elif self.format_string == "medium":
            size = "fa-4x"
        elif self.format_string == "large":
            size = "fa-5x"
        else:
            size = ''
        tag = "<i class=\"fa fa-spinner fa-spin %s\"></i>" % size
        return tag


def do_spinner(parser, token):
    """Creates a Font Awesome spinner. Token should be spinner size"""
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1]
            and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name)
    return SpinnerNode(format_string[1:-1])


register.tag('fa_spinner', do_spinner)
