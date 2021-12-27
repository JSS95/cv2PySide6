from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QSlider, QStyleOptionSlider, QStyle


__all__ = [
    "ClickableSlider",
]


class ClickableSlider(QSlider):
    """
    QSlider whose groove can be clicked to move to position.

    """
    # https://stackoverflow.com/questions/52689047
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.position())
            self.setValue(val)
        super().mousePressEvent(event)

    def pixelPosToRangeValue(self, pos: QPointF) -> int:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt,
                                         QStyle.SC_SliderGroove,
                                         self)
        sr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt,
                                         QStyle.SC_SliderHandle,
                                         self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(),
                                              self.maximum(),
                                              p - sliderMin,
                                              sliderMax - sliderMin,
                                              opt.upsideDown)

