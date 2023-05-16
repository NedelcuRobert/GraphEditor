import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, \
    QGraphicsTextItem, QGraphicsSceneMouseEvent, QLineEdit, QDialog, QVBoxLayout, QLabel, QPushButton, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QLineF


class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, diameter, parent=None):
        super().__init__(parent)
        self.setRect(x, y, diameter, diameter)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)

        self.key = None
        self.value = None

        self.key_text = QGraphicsTextItem("", self)
        self.key_text.setPos(x + diameter / 2 - self.key_text.boundingRect().width() / 2, y - 20)
        self.value_text = QGraphicsTextItem("", self)
        self.value_text.setPos(x + diameter / 2 - self.value_text.boundingRect().width() / 2, y + diameter + 5)

        self.edit_dialog = None

    def set_key_value(self, key, value):
        self.key = key
        self.value = value
        self.update_text()

    def update_text(self):
        self.key_text.setPlainText(str(self.key))
        self.value_text.setPlainText(str(self.value))

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        if self.edit_dialog is None:
            self.edit_dialog = NodeEditDialog(self)
            self.edit_dialog.show()

        super().mouseDoubleClickEvent(event)


class Edge(QGraphicsLineItem):
    def __init__(self, source_node=None, dest_node=None, parent=None):
        super().__init__(parent)
        self.source_node = source_node
        self.dest_node = dest_node

        self.key = None
        self.value = None

        self.key_text = QGraphicsTextItem("", self)
        self.update_text()

    def set_nodes(self, source_node, dest_node):
        self.source_node = source_node
        self.dest_node = dest_node
        self.update_line()

    def update_line(self):
        if self.source_node is not None and self.dest_node is not None:
            source_pos = self.source_node.rect().center()
            dest_pos = self.dest_node.rect().center()
            self.setLine(QLineF(source_pos, dest_pos))
            self.update_text()

    def set_key_value(self, key, value):
        self.key = key
        self.value = value
        self.update_text()

    def update_text(self):
        self.key_text.setPlainText(str(self.key))
        self.key_text.setPos(self.line().center().x() - self.key_text.boundingRect().width() / 2,
                             self.line().center().y() - 20)


class NodeEditDialog(QDialog):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Node")
        self.layout = QVBoxLayout()

        self.key_label = QLabel("Key:")
        self.key_input = QLineEdit(str(node.key))
        self.layout.addWidget(self.key_label)
        self.layout.addWidget(self.key_input)

        self.value_label = QLabel("Value:")
        self.value_input = QLineEdit(str(node.value))
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.value_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.node = node

    def save_changes(self):
        self.node.key = self.key_input.text()
        self.node.value = self.value_input.text()
        self.node.update_text()
        self.close()


class GraphEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graph Editor")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.node_size = 60
        self.nodes = []
        self.edges = []

        self.create_node_button = QPushButton("Create Node")
        self.create_node_button.clicked.connect(self.create_node_button_clicked)
        self.create_edge_button = QPushButton("Create Edge")
        self.create_edge_button.clicked.connect(self.create_edge_button_clicked)

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addWidget(self.create_node_button)
        self.toolbar.addWidget(self.create_edge_button)

        self.selected_nodes = []

    def create_node_button_clicked(self):
        pos = self.mapFromGlobal(self.cursor().pos())
        node = self.create_node(pos.x() - self.node_size / 2, pos.y() - self.node_size / 2)
        if len(self.selected_nodes) == 2:
            node1, node2 = self.selected_nodes
            self.create_edge(node1, node2)
            self.selected_nodes = []

        self.selected_nodes.append(node)

    def create_edge_button_clicked(self):
        if len(self.selected_nodes) == 2:
            node1, node2 = self.selected_nodes
            self.create_edge(node1, node2)
            self.selected_nodes = []

    def create_node(self, x, y):
        node = Node(x, y, self.node_size)
        self.scene.addItem(node)
        self.nodes.append(node)
        return node

    def create_edge(self, source_node, dest_node):
        edge = Edge()
        edge.set_nodes(source_node, dest_node)
        self.scene.addItem(edge)
        self.edges.append(edge)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_nodes = [node for node in self.nodes if node.isSelected()]
            for node in selected_nodes:
                self.scene.removeItem(node)
                self.nodes.remove(node)
                self.selected_nodes.remove(node)
            selected_edges = [edge for edge in self.edges if edge.isSelected()]
            for edge in selected_edges:
                self.scene.removeItem(edge)
                self.edges.remove(edge)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.scene.clearSelection()
        super().mousePressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = GraphEditor()
    editor.show()
    sys.exit(app.exec_())
