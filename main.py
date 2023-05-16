import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, \
    QGraphicsTextItem, QGraphicsSceneMouseEvent, QLineEdit, QDialog, QVBoxLayout, QLabel, QPushButton, QGraphicsLineItem
from PyQt5.QtCore import Qt, QLineF


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

        self.edit_dialog = EditDialog(self)
        self.edit_dialog.show()

    def set_key_value(self, key, value):
        self.key = key
        self.value = value
        self.update_text()

    def update_text(self):
        self.key_text.setPlainText(str(self.key))
        self.value_text.setPlainText(str(self.value))

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)
        for edge in self.scene().items():
            if isinstance(edge, Edge) and (edge.source_node is self or edge.dest_node is self):
                edge.adjust()

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        self.edit_dialog.show()

        super().mouseDoubleClickEvent(event)


class Edge(QGraphicsLineItem):
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.setFlag(self.ItemIsSelectable, True)
        self.source_node = source_node
        self.dest_node = dest_node
        self.source_node_pos = source_node.pos()
        self.dest_node_pos = dest_node.pos()
        self.key = None
        self.value = None

        self.key_text = QGraphicsTextItem("", self)
        self.value_text = QGraphicsTextItem("", self)

        self.key_text.setPos(self.x() - self.key_text.boundingRect().width() / 2, self.y() - 20)
        self.value_text.setPos(self.x() - self.value_text.boundingRect().width() / 2, self.y() + 5)

        self.edit_dialog = EditDialog(self)
        self.edit_dialog.show()

    def adjust(self):
        source_shape = self.source_node.shape()
        dest_shape = self.dest_node.shape()

        source_point = source_shape.pointAtPercent(1)
        dest_point = dest_shape.pointAtPercent(0)

        source_pos = self.source_node.mapToScene(source_point)
        dest_pos = self.dest_node.mapToScene(dest_point)

        line = QLineF(source_pos, dest_pos)
        self.setLine(line)

        center_pos = line.pointAt(0.5)
        center_x = center_pos.x()
        center_y = center_pos.y()

        self.key_text.setPos(center_x - self.key_text.boundingRect().width() / 2, center_y - 20)
        self.value_text.setPos(center_x - self.value_text.boundingRect().width() / 2, center_y + 5)

    def set_key_value(self, key, value):
        self.key = key
        self.value = value
        self.update_text()

    def update_text(self):
        self.key_text.setPlainText(str(self.key))
        self.value_text.setPlainText(str(self.value))

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        self.edit_dialog.show()

        super().mouseDoubleClickEvent(event)


class EditDialog(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item")
        self.layout = QVBoxLayout()

        self.key_label = QLabel("Key:")
        self.key_input = QLineEdit(str(item.key))
        self.layout.addWidget(self.key_label)
        self.layout.addWidget(self.key_input)

        self.value_label = QLabel("Value:")
        self.value_input = QLineEdit(str(item.value))
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.value_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.item = item

    def save_changes(self):
        self.item.key = self.key_input.text()
        self.item.value = self.value_input.text()
        self.item.update_text()
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

    def create_node_button_clicked(self):
        pos = self.mapFromGlobal(self.cursor().pos())
        node = self.create_node(pos.x() - self.node_size / 2, pos.y() - self.node_size / 2)

    def create_edge_button_clicked(self):
        selected_nodes = [node for node in self.nodes if node.isSelected()]
        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes
            self.create_edge(node1, node2)

    def create_node(self, x, y):
        node = Node(x, y, self.node_size)
        self.scene.addItem(node)
        self.nodes.append(node)
        return node

    def remove_node(self, node):
        if node in self.nodes:
            self.scene.removeItem(node)
            self.nodes.remove(node)

            connected_edges = [edge for edge in self.edges if edge.source_node == node or edge.dest_node == node]
            for edge in connected_edges:
                self.scene.removeItem(edge)
                self.edges.remove(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.scene.removeItem(edge)
            self.edges.remove(edge)
            self.scene.removeItem(edge.key_text)
            self.scene.removeItem(edge.value_text)

    def create_edge(self, source_node, dest_node):
        edge = Edge(source_node, dest_node)
        edge.adjust()
        self.scene.addItem(edge)
        self.edges.append(edge)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_nodes = [node for node in self.nodes if node.isSelected()]
            for node in selected_nodes:
                self.remove_node(node)

            selected_edges = [edge for edge in self.edges if edge.isSelected()]
            for edge in selected_edges:
                self.remove_edge(edge)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.scene.clearSelection()
        super().mousePressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = GraphEditor()
    editor.show()
    sys.exit(app.exec_())
