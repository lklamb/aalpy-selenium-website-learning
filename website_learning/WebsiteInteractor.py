from selenium.common import InvalidSelectorException, ElementClickInterceptedException, ElementNotInteractableException
from selenium import webdriver
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import website_learning.Settings as Settings
import website_learning.Util as Util
from website_learning.Constants import INTERACTION_INTERCEPTED_STR, NOT_INTERACTABLE_STR, DELIMITER_FOR_LETTER, SLASH
from website_learning.Interactor import Interactor
from website_learning.InputElement import Clickable, ChangeableSelectOption, InputElement, HoverStart, HoverEnd
from website_learning.Enums import ElementType


class WebsiteInteractor(Interactor):

    def __init__(self):
        super().__init__()
        self.input_alphabet_map = {}
        self.current_mouse_pos = dict()  # relative to viewport
        self.driver = None

    def analysis_phase(self):
        options = Options()
        prefs = {
            "profile.managed_default_content_settings.javascript": 2  # 2 means block
        }
        options.add_experimental_option("prefs", prefs)
        if Settings.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)
        # disable alerts before any page script runs
        # set all links to open in same window
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                                    window.alert = function() {};
                                    window.confirm = function() { return true; };
                                    window.prompt = function() { return null; };
                                    window.open = function(url, name, features) { window.location.href = url; }; 
                                """
            }
        )
        self.preprocess_urls()
        self.generate_input_alphabet()
        self.driver.quit()
        Util.logger.info("website analysis complete")

    def configure_for_learning(self):
        options_for_learning = Options()
        if Settings.headless:
            options_for_learning.add_argument("--headless")
            options_for_learning.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options_for_learning)
        # disable alerts before any page script runs
        # set all links to open in same window
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    window.alert = function() {};
                    window.confirm = function() { return true; };
                    window.prompt = function() { return null; };
                    window.open = function(url, name, features) { window.location.href = url; }; 
                """
            }
        )
        self.driver.implicitly_wait(Settings.wait_time)

    def preprocess_urls(self):
        self.reset_system(Settings.website_to_learn.initial_url)
        Util.initial_url = Util.make_url_safe_for_display(self.driver.current_url)
        urls_without_duplicates = list(dict.fromkeys(Settings.website_to_learn.urls_in_scope))  # from Raymond Hettinger, https://twitter.com/raymondh/status/944125570534621185
        for url in urls_without_duplicates:
            self.reset_system(url)
            Util.urls_in_scope.add(Util.make_url_safe_for_display(self.driver.current_url))
        Util.write_scope_to_file()

    def generate_input_alphabet(self):
        for url in Util.urls_in_scope:
            self.reset_system(url)
            nr_interactive_elements = 0
            nr_interactive_elements += self.find_interactive_elements(url, ElementType.HREF)
            nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONCLICK)
            nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONCHANGE)
            if Settings.include_hover:
                nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONMOUSEENTER)
                nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONMOUSEOVER)
                nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONMOUSELEAVE)
                nr_interactive_elements += self.find_interactive_elements(url, ElementType.ONMOUSEOUT)
            if nr_interactive_elements > 0:
                Util.webpage_has_interactive_elements[url] = True
            else:
                Util.webpage_has_interactive_elements[url] = False
            Util.logger.debug(str(nr_interactive_elements) + " interactive elements")
        Util.input_alphabet = sorted(list(self.input_alphabet_map.keys()))
        Util.write_input_alphabet_to_file()

    def find_interactive_elements(self, url, element_type):
        html_references = self.driver.find_elements(By.XPATH, InputElement.element_type_to_xpath[element_type])
        nr_elements = 0
        for index, html_reference in enumerate(html_references):
            nr_elements += 1
            try:  # display all parent elements, so that names are accessible
                current_element = html_reference
                while True:
                    self.driver.execute_script("arguments[0].style.display = 'initial';", current_element)
                    current_element = current_element.find_element(By.XPATH, "./..")
            except InvalidSelectorException:
                pass
            try:
                name = html_reference.accessible_name
                # remove all occurrences of the delimiter that will be used internally
                name = name.replace(DELIMITER_FOR_LETTER, "")
                name = name.replace(SLASH, "")
            except:
                name = None
            input_letters = []
            match element_type:
                case ElementType.HREF | ElementType.ONCLICK:
                    input_letters.append(Clickable(url, element_type, index, name))
                case ElementType.ONCHANGE:
                    if html_reference.tag_name == 'select':
                        for option in Select(html_reference).options:
                            option_value = None
                            try:
                                option_value = option.get_attribute('value')
                            except:
                                pass
                            input_letters.append(ChangeableSelectOption(url, element_type, index, name, option.get_attribute('index'), option_value))
                    else:
                        input_letters.append(Clickable(url, element_type, index, name))
                case ElementType.ONMOUSEENTER | ElementType.ONMOUSEOVER:
                    input_letters.append(HoverStart(url, element_type, index, name))
                case ElementType.ONMOUSELEAVE | ElementType.ONMOUSEOUT:
                    input_letters.append(HoverEnd(url, element_type, index, name))
                case _:
                    assert False
            for letter in input_letters:
                self.input_alphabet_map[letter.get_letter_string()] = letter

        Util.logger.debug(str(nr_elements) + " " + str(element_type))
        return nr_elements

    def reset_system(self, url_to_load=None):
        if url_to_load is None:
            url_to_load = Util.make_url_safe_for_interaction(Util.initial_url)
        else:
            url_to_load = Util.make_url_safe_for_interaction(url_to_load)
        self.reset_mouse()  # especially necessary if hover events are tracked, move mouse to top left corner of page
        self.log_cookies("before deletion:")
        self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})  # deletes cookies for whole session
        # this only deletes cookies for the current domain, if multiple domains -> leftover cookies
        # self.driver.delete_all_cookies()
        Util.logger.debug("trying to load " + url_to_load)
        self.driver.get(url_to_load)
        Util.logger.debug("loaded " + self.driver.current_url)
        self.log_cookies("after deletion and reset:")
        if url_to_load != self.driver.current_url:
            Util.logger.error("reset failed")
            assert False
        self.show_mouse_cursor()

    def get_current_url(self):
        return Util.make_url_safe_for_display(self.driver.current_url)

    def process_input_letter(self, input_letter):
        element = self.input_alphabet_map[input_letter]
        output = None
        try:
            self.log_cookies("before interaction:")
            self.interact_with_element(element)
            output = self.driver.current_url
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            if isinstance(e, ElementClickInterceptedException):
                Util.logger.debug("click was intercepted")
                output = INTERACTION_INTERCEPTED_STR
            elif isinstance(e, ElementNotInteractableException):
                Util.logger.debug("element is currently not interactable")
                output = NOT_INTERACTABLE_STR
        self.log_cookies("after interaction:")
        self.show_mouse_cursor()
        return output

    def final_cleanup(self):
        self.driver.quit()

    def interact_with_element(self, element):
        element.log_interaction_start()
        html_reference = element.get_html_reference(self)
        element.interact(html_reference, self)

    def reset_mouse(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        action = ActionBuilder(self.driver)
        action.pointer_action.move_to_location(1, 1)
        action.perform()
        Util.logger.debug("reset mouse position")
        self.current_mouse_pos['x'] = 1.0
        self.current_mouse_pos['y'] = 1.0
        self.check_mouse_tracker()

    def set_current_mouse_pos_to_position(self, pos):
        self.current_mouse_pos = pos
        self.check_mouse_tracker()

    def get_center_of_element_pos(self, element):
        rect = self.get_bounding_rect(element)
        pos = dict()
        pos['x'] = rect['left'] + rect['width'] / 2
        pos['y'] = rect['top'] + rect['height'] / 2
        return pos

    def get_bounding_rect(self, element):
        if element.tag_name == 'area':
            return self.get_area_bounding_rect(element)

        return self.driver.execute_script("""
                 const el = arguments[0];
                 const rect = el.getBoundingClientRect();
                 return { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height};
               """, element)

    def check_mouse_tracker(self):
        scroll_x = self.driver.execute_script("return window.scrollX;")
        scroll_y = self.driver.execute_script("return window.scrollY;")
        Util.logger.debug(f"scroll x {scroll_x:.2f} / y {scroll_y:.2f}")
        Util.logger.debug(f"mouse tracked at x {self.current_mouse_pos['x']:.2f} / y {self.current_mouse_pos['y']:.2f}")

    def get_area_bounding_rect(self, area):
        map_element = self.driver.execute_script("""
            let el = arguments[0];
            while (el && el.tagName.toLowerCase() !== 'map') {
                el = el.parentElement;
            }
            return el;
        """, area)

        if not map_element:
            raise Exception("<area> without <map> ancestor on page.")

        map_rect = self.get_bounding_rect(map_element)
        coords = area.get_attribute("coords")
        shape = area.get_attribute("shape").lower()

        coords = list(map(int, coords.split(",")))

        if shape == "rect":
            x1, y1, x2, y2 = coords
        elif shape == "circle":
            cx, cy, r = coords
            x1, y1 = cx - r, cy - r
            x2, y2 = cx + r, cy + r
        elif shape == "poly":
            xs = coords[::2]
            ys = coords[1::2]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)
        else:
            raise ValueError("Unsupported area shape:", shape)

        return {
            "left": map_rect['left'] + x1,
            "right": map_rect['left'] + x2,
            "top": map_rect['top'] + y1,
            "bottom": map_rect['top'] + y2,
            "width": x2 - x1,
            "height": y2 - y1
        }

    def does_mouse_cursor_exist(self):
        return self.driver.execute_script("return document.getElementById('selenium-mouse') !== null;")

    def show_mouse_cursor(self):
        if not Settings.display_cursor:
            return
        if self.does_mouse_cursor_exist():
            return
        # adapted from https://stackoverflow.com/questions/67453285/the-way-to-show-mouse-cursor-using-selenium-in-python
        cursor_script = '''
        var cursor = document.createElement('mouse-pointer');
        cursor.id = 'selenium-mouse';
        cursor.style.position = 'absolute';
        cursor.style.zIndex = '9999';
        cursor.style.width = '10px';
        cursor.style.height = '10px';
        cursor.style.borderRadius = '50%';
        cursor.style.backgroundColor = 'red';
        cursor.style.pointerEvents = 'none';
        document.body.appendChild(cursor);
        cursor.style.left = '-4px';
        cursor.style.top = '-4px'; 

        document.addEventListener('mousemove', function(e) {
          cursor.style.left = e.pageX - 5 + 'px';
          cursor.style.top = e.pageY - 5 + 'px';
        });
        '''
        self.driver.execute_script(cursor_script)
        Util.logger.debug("made cursor visible")

    def log_cookies(self, msg):
        cookies = self.driver.get_cookies()
        Util.logger.debug("Cookies for current domain " + msg)
        for cookie in cookies:
            Util.logger.debug(str(cookie["name"]) + ": " + str(cookie["value"]))

