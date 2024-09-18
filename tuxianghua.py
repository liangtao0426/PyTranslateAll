import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QPushButton, QLineEdit, QFileDialog, QVBoxLayout,
                             QFormLayout, QDialog, QProgressBar)
from PyQt5.QtCore import QTimer
import configparser
from new_fanyi import process_excel


class TranslationApp(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('翻译工具')
        self.setGeometry(100, 100, 400, 300)

        # 创建表单布局
        self.layout = QFormLayout()

        # 翻译服务选项
        self.service_label = QLabel("选择翻译服务:")
        self.service_combo = QComboBox(self)
        self.service_combo.addItems(["请选择翻译服务", "腾讯翻译", "火山翻译"])  # 初始默认项
        self.service_combo.currentIndexChanged.connect(self.update_key_value_input)

        # 将翻译服务选项框添加到布局
        self.layout.addRow(self.service_label, self.service_combo)

        # 秘钥输入框：key 和 value（初始隐藏）
        self.key_label = QLabel("输入 Key:")
        self.key_input = QLineEdit(self)

        self.value_label = QLabel("输入 Value:")
        self.value_input = QLineEdit(self)

        # 初始隐藏 key 和 value 输入框
        self.key_label.hide()
        self.key_input.hide()
        self.value_label.hide()
        self.value_input.hide()

        # 需要翻译的文件路径选择按钮
        self.input_file_label = QLabel("选择要翻译的文件:")
        self.input_file_button = QPushButton("浏览...", self)
        self.input_file_button.clicked.connect(self.browse_input_file)

        self.input_file_display = QLabel("")  # 显示已选择的文件路径

        # 保存文件的路径选择按钮
        self.output_file_label = QLabel("选择保存文件路径:")
        self.output_file_button = QPushButton("浏览...", self)
        self.output_file_button.clicked.connect(self.browse_output_file)

        self.output_file_display = QLabel("")  # 显示已选择的保存文件路径

        # 确认按钮
        self.submit_button = QPushButton("开始翻译", self)
        self.submit_button.clicked.connect(self.start_translation)

        # 添加文件路径选择和保存路径选择组件到布局中
        self.layout.addRow(self.input_file_label, self.input_file_button)
        self.layout.addRow("", self.input_file_display)
        self.layout.addRow(self.output_file_label, self.output_file_button)
        self.layout.addRow("", self.output_file_display)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

        # 添加进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 300, 400, 25)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)  # 进度条范围0到100
        self.progress_bar.setValue(0)   # 初始值为0
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat('%p%')

        # 布局中加入进度条
        self.layout.addWidget(self.progress_bar)

    # 更新翻译服务选项时显示或隐藏 key 和 value 的输入框
    def update_key_value_input(self):
        service = self.service_combo.currentText()

        # 动态显示/隐藏 key 和 value 输入框
        if service == "请选择翻译服务":
            self.key_label.hide()
            self.key_input.hide()
            self.value_label.hide()
            self.value_input.hide()
        else:
            self.key_label.show()
            self.key_input.show()
            self.value_label.show()
            self.value_input.show()

            # 如果输入框没有在下拉框下方，则插入它们
            if self.layout.indexOf(self.key_label) == -1:
                # 将 key 和 value 输入框插入到服务选择框下方
                self.layout.insertRow(1, self.key_label, self.key_input)
                self.layout.insertRow(2, self.value_label, self.value_input)

    # 浏览选择需要翻译的文件
    def browse_input_file(self):
        self.input_file, _ = QFileDialog.getOpenFileName(self, "选择要翻译的文件", "",
                                                         "Excel Files (*.xlsx);;All Files (*)")
        if self.input_file:
            self.input_file_display.setText(f"已选择文件: {self.input_file}")  # 展示选择的文件路径

    # 浏览选择保存的文件路径
    def browse_output_file(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self, "选择保存文件路径", "",
                                                          "Excel Files (*.xlsx);;All Files (*)")
        if self.output_file:
            self.output_file_display.setText(f"保存路径: {self.output_file}")  # 展示选择的保存文件路径

    # 弹出2秒后自动消失的自定义弹窗
    def show_error_message(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("错误")

        # 设置错误提示的 QLabel
        error_label = QLabel(message, error_dialog)
        error_label.setStyleSheet("color: red")

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        error_dialog.setLayout(layout)

        # 显示弹窗
        error_dialog.show()

        # 2秒后关闭弹窗
        QTimer.singleShot(2000, error_dialog.close)

    # 开始翻译操作
    def start_translation(self):
        service = self.service_combo.currentText()
        key = self.key_input.text()
        value = self.value_input.text()

        # 检查用户是否输入了所有必要的字段
        if service == "请选择翻译服务" or not key or not value or not hasattr(self, 'input_file') or not hasattr(self,
                                                                                                                 'output_file'):
            self.show_error_message("请完整填写所有信息")  # 弹出错误提示窗
        else:
            self.update_config_file(service, key, value)

            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            print(f"选择的翻译服务: {service}")
            print(f"Key: {key}")
            print(f"Value: {value}")
            print(f"需要翻译的文件: {self.input_file}")
            print(f"保存的文件路径: {self.output_file}")

            # 调用翻译函数，传递相应的参数
            try:
                if service == "腾讯翻译":
                    process_excel('tx_api', self.update_progress_bar)
                elif service == "火山翻译":
                    process_excel('hs_api', self.update_progress_bar)
                else:
                    raise ValueError("未知的翻译服务")
                self.progress_bar.setValue(100)  # 强制设置进度条到100%
                self.show_info_message("翻译已完成")
            except Exception as e:
                print(f"翻译过程中出现错误: {e}")

    def update_config_file(self, service, key, value):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if service == "腾讯翻译":
            config['tx_api']['secret_id'] = key
            config['tx_api']['secret_key'] = value
            config['tx_api']['input_file_path'] = self.input_file
            config['tx_api']['output_file_path'] = self.output_file
        elif service == "火山翻译":
            config['hs_api']['access_key'] = key
            config['hs_api']['secret_key'] = value
            config['hs_api']['input_file_path'] = self.input_file
            config['hs_api']['output_file_path'] = self.output_file

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("配置文件已更新")

    # 更新进度条的方法
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")
        QApplication.processEvents()


    def show_info_message(self, message):
        info_dialog = QDialog(self)
        info_dialog.setWindowTitle("提示")

        # 设置提示的 QLabel
        info_label = QLabel(message, info_dialog)
        info_label.setStyleSheet("color: green")

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(info_label)
        info_dialog.setLayout(layout)

        # 显示弹窗
        info_dialog.exec_()  # 使用 exec_() 确保弹窗在完成后关闭


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec_())
