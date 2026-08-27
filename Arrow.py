# -*- coding: utf-8 -*-
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPolygonF, QColor
from PySide6.QtWidgets import QGraphicsLineItem


class Arrow(QGraphicsLineItem):
    def __init__(self, parent_node, child_node):
        super().__init__()
        self.parent_node = parent_node
        self.child_node = child_node

        self.arrow_size = 10.0
        self.setPen(QPen(QColor("#50422c"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(-1)

        self.parent_node.arrows.append(self)
        self.child_node.arrows.append(self)

        self.update_position()

    def update_position(self):
        p_center = self.parent_node.sceneBoundingRect().center()
        c_center = self.child_node.sceneBoundingRect().center()

        rect = self.child_node.sceneBoundingRect()

        dx = c_center.x() - p_center.x()
        dy = c_center.y() - p_center.y()

        if dx == 0 and dy == 0:
            self.setLine(p_center.x(), p_center.y(), c_center.x(), c_center.y())
            return

        scale = min(
            (rect.width() / 2) / abs(dx) if dx else float("inf"),
            (rect.height() / 2) / abs(dy) if dy else float("inf")
        )

        arrow_end = QPointF(
            c_center.x() - dx * scale,
            c_center.y() - dy * scale
        )

        self.setLine(p_center.x(), p_center.y(), arrow_end.x(), arrow_end.y())

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        line = self.line()
        if line.length() < 1:
            return

        angle = math.atan2(-line.dy(), line.dx())
        arrow_tip = line.p2()

        arrow_p1 = arrow_tip - QPointF(
            math.cos(angle + math.pi / 6) * self.arrow_size,
            -math.sin(angle + math.pi / 6) * self.arrow_size
        )

        arrow_p2 = arrow_tip - QPointF(
            math.cos(angle - math.pi / 6) * self.arrow_size,
            -math.sin(angle - math.pi / 6) * self.arrow_size
        )

        arrow_head = QPolygonF([arrow_tip, arrow_p1, arrow_p2])

        painter.setBrush(self.pen().color())
        painter.drawPolygon(arrow_head)

