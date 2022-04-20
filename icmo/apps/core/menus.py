from menu import Menu, MenuItem

# Add two items to our main menu
from django.core.urlresolvers import reverse

Menu.add_item("main", MenuItem("Start",
                               reverse("start_redirect"),
                               weight=10,
                               icon="play"))

Menu.add_item("main", MenuItem("Revenue Plans",
                               reverse("start_redirect"),
                               weight=20,
                               icon='filter'))

Menu.add_item("main", MenuItem("Lead Mix",
                               reverse("start_redirect"),
                               icon='cogs',
                               weight=20))

Menu.add_item("main", MenuItem("Budget",
                               reverse("start_redirect"),
                               icon='usd',
                               weight=20))

Menu.add_item("main", MenuItem("Resources",
                               reverse("start_redirect"),
                               icon='calendar',
                               weight=20))

Menu.add_item("main", MenuItem("Dashboard",
                               reverse("start_redirect"),
                               icon='tachometer',
                               weight=20))
