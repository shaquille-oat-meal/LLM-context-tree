# -*- coding: utf-8 -*-
import sys
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
        node = self.scene.selectedItems()[0].logical_node
        if node == self.root:
            return
        
        self.scene.remove_node()
        
        parent = node.parent
        
        for child in node.children:
            child.parent = parent
            parent.children.add(child)
        
        node.children.clear()
        node.parent = None
        


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