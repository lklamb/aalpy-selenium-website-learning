class WebsiteURLs:

    def __init__(self, initial_url: str, urls_in_scope: [str]):
        # URL to starting point of learning algorithm
        # recommended to use a specific html page (e.g. /index.html)
        # if main website URL is used, it typically defaults to home page anyway,
        # but might appear as two different states in learned automaton depending on the URL that is displayed
        self.initial_url = initial_url

        # collection of URLs used to generate the input alphabet, initial URL is always in scope, will be deduplicated
        # if webpages outside the scope are reached exploration will not continue from there
        self.urls_in_scope = urls_in_scope
        self.urls_in_scope.append(initial_url)


class TestWebsite(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/index.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/index.html",
                         "https://lklamb.github.io/Test_Website/basics.html",
                         "https://lklamb.github.io/Test_Website/map_areas.html",
                         "https://lklamb.github.io/Test_Website/dropdowns.html",
                         "https://lklamb.github.io/Test_Website/checkboxes.html",
                         "https://lklamb.github.io/Test_Website/selections_choices.html",
                         "https://lklamb.github.io/Test_Website/attribute_combinations.html",
                         "https://lklamb.github.io/Test_Website/tabs_windows.html",
                         "https://lklamb.github.io/Test_Website/empty.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteIndex(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/index.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/index.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteBasics(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/basics.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/basics.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteMapAreas(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/map_areas.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/map_areas.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteDropdowns(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/dropdowns.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/dropdowns.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteCheckboxes(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/checkboxes.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/checkboxes.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteSelectionsChoices(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/selections_choices.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/selections_choices.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteAttributeCombinations(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/attribute_combinations.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/attribute_combinations.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class TestWebsiteTabsWindows(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/tabs_windows.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/tabs_windows.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class OutputExample(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/output-example_page1.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/output-example_page1.html",
                         "https://lklamb.github.io/Test_Website/output-example_page2.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class RunningExample(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/running-example_page1.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/running-example_page1.html",
                         "https://lklamb.github.io/Test_Website/running-example_page2.html",
                         "https://lklamb.github.io/Test_Website/running-example_page3.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class HoverExample(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/hover-example_page1.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/hover-example_page1.html",
                         "https://lklamb.github.io/Test_Website/hover-example_page2.html",
                         "https://lklamb.github.io/Test_Website/hover-example_page3.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class MovingElementsExample(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/Test_Website/moving-elements-example_page1.html"
        urls_in_scope = ["https://lklamb.github.io/Test_Website/moving-elements-example_page1.html",
                         ]
        super().__init__(initial_url, urls_in_scope)


class CarAlarmWebsite(WebsiteURLs):
    def __init__(self):
        initial_url = "https://lklamb.github.io/CarAlarmSystem_Demo/index.html"
        urls_in_scope = ["https://lklamb.github.io/CarAlarmSystem_Demo/index.html",
                         "https://lklamb.github.io/CarAlarmSystem_Demo/armed.html",
                         "https://lklamb.github.io/CarAlarmSystem_Demo/alarm.html"
                         ]
        super().__init__(initial_url, urls_in_scope)
