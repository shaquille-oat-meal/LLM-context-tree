# -*- coding: utf-8 -*-
import sys
import json
from PySide6.QtWidgets import QApplication, QGraphicsView
from PySide6.QtGui import QBrush
from PySide6.QtCore import Qt
from Canvas import Scene, View
from Node import LogicalNode, GraphicalNode

class Controller:
    def __init__(self, logical_root, scene):
        self.scene = scene
        self.root = logical_root
        self.scene = scene

    def add_node(self):
        parent = self.scene.selectedItems()[0].logical_node
        logical_node = LogicalNode(parent)
        parent.children.add(logical_node)
        self.scene.add_node(logical_node)
        return logical_node

    def remove_node(self):
        selected_item = self.scene.selectedItems()[0]
        node = selected_item.logical_node
        if node == self.root:
            return

        self.scene.remove_node()

        parent = node.parent
        parent.children.remove(node)

        for child in node.children:
            child.parent = parent
            parent.children.add(child)

        node.children.clear()
        node.parent = None

    def save_file(self, filename):
        def convert(node):
            return {
                "q": node.user_input,
                "a": node.llm_response,
                "n": node.note,
                "children": [convert(child) for child in node.children]
            }

        with open(filename, "w") as file:
            json.dump(convert(self.root), file, indent=2)

    def open_file(self, path):
        def give_birth(parent, json_kids):
            for child in json_kids:
                node = LogicalNode(parent)
                node.user_input = child["q"]
                node.llm_response = child["a"]
                node.note = child["n"]
                parent.children.add(node)
                scene.add_node(node)
                give_birth(node, child["children"])
        data = None
        with open(path, "r") as file:
            data = json.load(file)
        self.root.user_input = data["q"]
        self.root.llm_response = data["a"]
        self.root.note = data["n"]
        self.scene.get_node(self.root).editor.refresh()
        give_birth(self.root, data["children"])



if __name__ == '__main__':
    app = QApplication(sys.argv)

    root_node = LogicalNode()
    scene = Scene(root_node)
    controller = Controller(root_node, scene)

    view = View(scene, controller)
    view.resize(600, 400) # sets the inital size of the window, its way too small if this isnt done
    view.setBackgroundBrush(QBrush("#FCF8E8"))
    initial_rect = scene.itemsBoundingRect()
    initial_rect = initial_rect.adjusted(-50, -50, 50, 50)
    view.fitInView(initial_rect, Qt.KeepAspectRatio)
    view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate) # anytime there is a change the entire scene is redrawn


    view.show()

    app.exec()
