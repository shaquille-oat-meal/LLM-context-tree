# -*- coding: utf-8 -*-
# Contains the PySide6 view and scene architechture
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QFileDialog
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QKeyEvent
from Node import LogicalNode, GraphicalNode
from Arrow import Arrow

class Scene(QGraphicsScene):
    def __init__(self, root):
        super().__init__()
        node = GraphicalNode(root)
        self.addItem(node)
        self.update_scene_rect()

    def update_scene_rect(self):
        rect = self.itemsBoundingRect()
        padding = 2000
        self.setSceneRect(rect.adjusted(
            -padding, -padding,
            padding, padding
            ))

    def add_node(self, logical_node):
        node = GraphicalNode(logical_node)
        parent_node = self.get_node(logical_node.parent)

        horizontal_spacing = 80
        vertical_spacing = 150

        siblings = [
            item for item in self.items()
            if isinstance(item, GraphicalNode)
            and item.logical_node.parent == logical_node.parent
        ]

        parent_x = parent_node.pos().x()
        parent_y = parent_node.pos().y()

        y = parent_y + parent_node.height + vertical_spacing

        sibling_index = len(siblings)

        if sibling_index == 0:
            x = parent_x
        else:
            # 1, -1, 2, -2, 3, -3...
            distance = (sibling_index + 1) // 2

            if sibling_index % 2:
                direction = 1
            else:
                direction = -1

            x = parent_x + direction * distance * (
                node.width + horizontal_spacing
            )

        node.setPos(QPointF(x, y))

        self.addItem(node)

        arrow = Arrow(parent_node, node)
        self.addItem(arrow)

        self.update_scene_rect()

    def remove_node(self):
        selected_node = self.selectedItems()[0]

        # remove all arrows associated with node
        for arrow in selected_node.arrows[:]:
            arrow.parent_node.arrows.remove(arrow)
            arrow.child_node.arrows.remove(arrow)
            self.removeItem(arrow)

        # create new arrows in its place
        logical_node = selected_node.logical_node
        parent = self.get_node(logical_node.parent)
        for child in logical_node.children:
            node = self.get_node(child)
            arrow = Arrow(parent, node)
            self.addItem(arrow)

        self.removeItem(selected_node)
        self.update()

    def change_mode(self):
        selected_node = self.selectedItems()[0]
        selected_node.change_mode()


    def get_response(self):
        selected_node = self.selectedItems()[0]
        selected_node.get_response()

    def get_node(self, logical_node):
        for item in self.items():
            if isinstance(item, GraphicalNode):
                if item.logical_node == logical_node:
                    return item




class View(QGraphicsView):
    def __init__(self, scene, controller):
        super().__init__(scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.c = controller
        self.cmd = False
        self.file_path = None


    def wheelEvent(self, event):
        focus = self.scene().focusItem()

        if isinstance(focus, QGraphicsProxyWidget):
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y()

        # damping the zoom factor to make it less sensitive
        steps = delta / 120  # Each step is 120 units
        zoom = 1.05
        factor = zoom ** steps

        # clamping the zoom factor to prevent excessive zooming in or out
        current_scale = self.transform().m11()
        if current_scale * factor < 0.1 or current_scale * factor > 10:
            return

        self.scale(factor, factor)


    def keyPressEvent(self, event: QKeyEvent):
        focus = self.scene().focusItem()

        if isinstance(focus, QGraphicsProxyWidget):
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Control:
            self.cmd = True

        if event.key() == Qt.Key_N and self.cmd:
            self.c.add_node()

        if event.key() == Qt.Key_Backspace and self.cmd:
            self.c.remove_node()

        if event.key() == Qt.Key_Return and self.cmd:
            self.scene().get_response()

        if event.key() == Qt.Key_M and self.cmd:
            self.scene().change_mode()

        if event.key() == Qt.Key_S and self.cmd:
            if not self.file_path:
                self.file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "Trees", "JSON Files (*.json)")
            if self.file_path:
                self.c.save_file(self.file_path)

        if event.key() == Qt.Key_O and self.cmd:
            if not self.file_path:
                self.file_path, _ = QFileDialog.getOpenFileName(self, "Choose File", "Trees", "JSON Files (*.json)")
                if self.file_path:
                    self.c.open_file(self.file_path)


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.cmd_pressed = False

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.scene().update_scene_rect()
