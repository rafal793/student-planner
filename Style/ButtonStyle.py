
from dataclasses import dataclass
from typing import Optional, Union, List
from kivy.utils import get_color_from_hex
from Style.ButtonState import ButtonState
from abc import ABC, abstractmethod

class BasicButtonStyle(ABC):

    @abstractmethod
    def get_bg_color(self, state: ButtonState) -> list:
        pass

    @abstractmethod
    def get_border_color(self, state: ButtonState) -> list:
        pass

    @abstractmethod
    def get_text_color(self, state: ButtonState) -> list:
        pass

@dataclass
class ButtonStyle(BasicButtonStyle):
    shape: str = "rounded"
    border_radius: Union[int, List[int]] = 10 
    border_color: Optional[str] = "#FFFFFF"
    border_width: int = 0

    bg_color: Optional[str] = "#FFFFFF"
    text_color: Optional[str] = "#FFFFFF"

    hover_bg_color: Optional[str] = None
    hover_text_color: Optional[str] = None

    pressed_bg_color: Optional[str] = None
    pressed_text_color: Optional[str] = None

    disabled_bg_color: Optional[str] = "#555555"
    disabled_text_color: Optional[str] = "#888888"

    font_size: str = "14sp"
    font_name: str = "Roboto"
    bold: bool = False

    def get_bg_color(self, state: ButtonState) -> list:
        base_color = get_color_from_hex(self.bg_color)
        
        if state == ButtonState.DISABLED:
            return get_color_from_hex(self.disabled_bg_color)
        elif state == ButtonState.HOVER:
            if self.hover_bg_color: 
                return get_color_from_hex(self.hover_bg_color)
            return [base_color[0] * 0.8, base_color[1] * 0.8, base_color[2] * 0.8, 1]
        elif state == ButtonState.PRESSED:
            if self.pressed_bg_color: 
                return get_color_from_hex(self.pressed_bg_color)
            return [base_color[0], base_color[1], base_color[2], 1]
       
        return base_color

    def get_border_color(self, state: ButtonState) -> list:
        if self.border_width <= 0:
            return [0, 0, 0, 0]
        if state == ButtonState.PRESSED:
            return get_color_from_hex(self.border_color)
        return [0, 0, 0, 0]

    def get_text_color(self, state: ButtonState) -> list:
        if state == ButtonState.DISABLED:
            return get_color_from_hex(self.disabled_text_color)
        if state == ButtonState.HOVER and self.hover_text_color:
            return get_color_from_hex(self.hover_text_color)
        if state == ButtonState.PRESSED and self.pressed_text_color:
            return get_color_from_hex(self.pressed_text_color)
        return get_color_from_hex(self.text_color)