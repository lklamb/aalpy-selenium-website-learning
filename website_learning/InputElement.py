from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from abc import abstractmethod

from website_learning.Constants import DELIMITER_FOR_LETTER
from website_learning.Enums import ElementType, InteractionType
import website_learning.Util as Util


class InputElement:
    element_type_to_xpath = {ElementType.HREF: "//*[@href and not(self::link[contains(@rel, 'stylesheet')])]",
                             ElementType.ONCLICK: "//*[@onclick]",
                             ElementType.ONCHANGE: "//*[@onchange]",
                             ElementType.ONMOUSEENTER: "//*[@onmouseenter]",
                             ElementType.ONMOUSEOVER: "//*[@onmouseover]",
                             ElementType.ONMOUSELEAVE: "//*[@onmouseleave]",
                             ElementType.ONMOUSEOUT: "//*[@onmouseout]"
                             }

    def __init__(self, url: str, element_type: ElementType, index, name):
        self.url = url
        self.element_type = element_type
        self.index = index
        self.name = name

    @property
    @abstractmethod
    def interaction_type(self):
        pass

    def log_interaction_start(self):
        Util.logger.info(
            "trying to interact with " + str(self.element_type.name) + " element with index " + str(
                self.index) + " on page " + self.url + ", name: " + str(self.name) + ", interaction: " + str(
                self.interaction_type.name))

    def get_html_reference(self, wi):
        html_references = wi.driver.find_elements(By.XPATH, self.element_type_to_xpath[self.element_type])
        html_reference = html_references[self.index]
        wi.driver.execute_script("arguments[0].removeAttribute('target');", html_reference)  # never open in new tab
        wi.driver.execute_script("arguments[0].scrollIntoView();",
                                 html_reference)  # align element so that it is fully in view
        return html_reference

    def get_letter_string(self):
        return (self.url + DELIMITER_FOR_LETTER + str(self.element_type.name) + DELIMITER_FOR_LETTER + str(
            self.index) + DELIMITER_FOR_LETTER + str(self.name) + DELIMITER_FOR_LETTER + str(
            self.interaction_type.name))

    @abstractmethod
    def interact(self, html_reference, wi):
        pass


class Clickable(InputElement):  # move to element, then click
    def __init__(self, url: str, element_type: ElementType, index, name):
        assert element_type is ElementType.HREF or element_type is ElementType.ONCLICK or ElementType.ONCHANGE
        super().__init__(url, element_type, index, name)

    @property
    def interaction_type(self):
        return InteractionType.CLICK

    def interact(self, html_reference, wi):  # move to element, then click
        actions = ActionChains(wi.driver)
        position = wi.get_center_of_element_pos(html_reference)
        try:
            actions.move_to_element(html_reference).perform()
            wi.set_current_mouse_pos_to_position(position)
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException while moving")
        try:
            html_reference.click()
            Util.logger.info(str(self.interaction_type.name) + " " + str(self.element_type.name) + " element")
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException while clicking")


class ChangeableSelectOption(InputElement):
    def __init__(self, url: str, element_type: ElementType, index, name, option_index, option_value):
        assert element_type is ElementType.ONCHANGE
        self.option_index = option_index
        self.option_value = option_value
        super().__init__(url, element_type, index, name)


    @property
    def interaction_type(self):
        return InteractionType.SELECT_OPTION

    def interact(self, html_reference, wi):  # move to element, then click, then change option programmatically
        actions = ActionChains(wi.driver)
        position = wi.get_center_of_element_pos(html_reference)
        try:
            actions.move_to_element(html_reference).perform()
            wi.set_current_mouse_pos_to_position(position)
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException while moving")
        try:
            html_reference.click()
            Select(html_reference).select_by_index(self.option_index)  # does not change position of virtual mouse
            Util.logger.info(
                str(self.interaction_type.name) + " " + str(self.option_index) + " for " + str(self.element_type.name))
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException while changing select option")

    def get_letter_string(self):
        string = super().get_letter_string() + DELIMITER_FOR_LETTER + str(self.option_index)
        if self.option_value is None:
            return string
        else:
            return string + DELIMITER_FOR_LETTER + str(self.option_value)


class HoverStart(InputElement):

    def __init__(self, url: str, element_type: ElementType, index, name):
        assert element_type is ElementType.ONMOUSEOVER or element_type is ElementType.ONMOUSEENTER
        super().__init__(url, element_type, index, name)

    @property
    def interaction_type(self):
        return InteractionType.START_HOVER

    def interact(self, html_reference, wi):  # move mouse to hover over element
        actions = ActionChains(wi.driver)
        position = wi.get_center_of_element_pos(html_reference)
        try:
            actions.move_to_element(html_reference).perform()
            wi.set_current_mouse_pos_to_position(position)
            Util.logger.info("moved mouse to hover over element")
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException while moving")


class HoverEnd(InputElement):

    def __init__(self, url: str, element_type: ElementType, index, name):
        assert element_type is ElementType.ONMOUSELEAVE or element_type is ElementType.ONMOUSEOUT
        super().__init__(url, element_type, index, name)

    @property
    def interaction_type(self):
        return InteractionType.END_HOVER

    def interact(self, html_reference, wi):  # only move the mouse if it is currently above this element
        try:
            if self.is_mouse_hovering(html_reference, wi):
                wi.reset_mouse()  # mouse position tracking included in reset
            else:
                Util.logger.info("not currently over this element, mouse not moved")
        except StaleElementReferenceException:
            Util.logger.debug("StaleElementReferenceException in interaction sequence")

    def is_mouse_hovering(self, html_reference, wi):
        rect = wi.get_bounding_rect(html_reference)
        Util.logger.debug("bounding rect at hover check: ")
        Util.logger.debug(rect)
        if rect['left'] <= wi.current_mouse_pos['x'] <= rect['right'] and rect['top'] <= wi.current_mouse_pos['y'] <= rect['bottom']:
            return True
        else:
            return False
