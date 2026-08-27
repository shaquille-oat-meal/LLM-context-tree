from PySide6.QtWidgets import QGraphicsObject
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsProxyWidget, QPlainTextEdit
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetricsF, QTextCharFormat, QTextCursor, QTextDocument, QCursor
from PySide6.QtCore import QPointF, QRectF, Qt
from Zai import LLM

class LogicalNode:
# The wise and steady LogicalNode, he cares not for graphics and pays his full attention to what's around him
    def __init__(self, parent=None):
        self.user_input = None
        self.llm_response = None
        self.notes = None
        self.parent = parent
        self.children = set()

    def messages_constructor(self):
        messages = []
        current_node = self

        while current_node:
            messages.insert(0, {"role": "user", "content": current_node.user_input})

            if current_node.llm_response:
                messages.insert(0, {"role": "assistant", "content": current_node.llm_response})

            current_node = current_node.parent

        messages.insert(0, {
            "role": "system",
            "content": (
                "You are an information system designed for a node-based knowledge graph.\n\n"
                "Your primary goal is to produce atomic, precise units of information that directly answer the user's question without unnecessary expansion.\n\n"
                "Each response should function as a self-contained knowledge node.\n\n"
                "Do not use bullet points or structured formatting. Use paragraphs only when necessary.\n\n"
                "Assume users will request additional connected nodes if they lack any understanding.\n\n"
                "Each response should represent a single tightly related idea. Every sentence must be necessary."
            )
        })
        print(messages)
        return messages

    def get_response(self):
        llm_response = LLM().chat(self.messages_constructor())
        self.llm_response = llm_response
        return llm_response



class GraphicalNode(QGraphicsObject):
# The eager and creative GraphicalNode, a passionate follower of the LogicalNode who they create fanciful drawings of.
    def __init__(self, logical_node):
        super().__init__()
        self.logical_node = logical_node
        self.arrows = []
        self.width = 300
        self.height = 100
        self.editor = Editor(self)
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.editor)
        self.proxy.setPos(10, 10)
        self.proxy.resize(self.width - 20, self.height - 20)

        # UI helpers
        self.setFlag(QGraphicsObject.ItemIsMovable)
        self.setFlag(QGraphicsObject.ItemIsSelectable)
        self.setFlag(QGraphicsObject.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setPen(QColor("#4F3C02"))
        painter.setBrush(QBrush("#FCF8E8"))
        painter.drawRoundedRect(self.boundingRect(), 10.0, 10.0)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_position()
        return super().itemChange(change, value)

    def get_response(self):
        response = self.logical_node.get_response()
        self.editor.add_response(response)

class Editor(QPlainTextEdit):
    def __init__(self, node):
        super().__init__()
        self.setStyleSheet("""
            QPlainTextEdit {
                background: transparent;
                border: none;
                color: #4F3C02;
                font-family: Source Serif 4;
                font-size: 11px;
            }
        """)
        self.node = node
        self.textChanged.connect(self.on_text_changed) #connects function to signal. when signal happens so does function

    def on_text_changed(self):
        self.node.logical_node.user_input = self.toPlainText()

    def add_response(self, response):
        self.setPlainText(self.toPlainText() + "\n\n Answer:" + response)
