import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MyMainWindow(QMainWindow):
    def __init__(self, parent=None):

        super(MyMainWindow, self).__init__(parent)
        self.setWindowTitle('肾小球滤过屏障病理处理系统')  # 设置主窗口的标题
        self.setWindowIcon(QIcon('./icon/main.png'))
        self.resize(1400, 800)  # 设置窗口的尺寸
        self.status = self.statusBar()  # 设置状态栏
        self.status.showMessage('欢迎使用本软件', 5000)  # 状态栏只显示5秒

        import MyWidgets  # 用来初始化菜单栏
        self.menubar = MyWidgets.MyMenuBar(self)
        # self.toolbar = MyWidgets.MyToolBar(self)
        self.setMenuBar(self.menubar)  # 设置MenuBar
        self.setDockWindow()  # 生成所有的停靠窗口
        self.setWindowStyle()  # 设置所有窗口布局
        self.initAll()

    # 生成所有的停靠窗口
    def setDockWindow(self):
        import RegionDockWidget
        self.scan_region = RegionDockWidget.ScanRegionDockWidget('文件浏览区', self)
        self.history_region = RegionDockWidget.HistoryRegionDockWidget('历史记录区', self)
        self.draw_region = RegionDockWidget.DrawRegionDockWidget('绘图区', self)
        self.tool_region = RegionDockWidget.ToolRegionDockWidget('工具管理区', self)
        self.algorithm_region = RegionDockWidget.AlgorithmRegionDockWidget('方法区', self)
        self.layer_region = RegionDockWidget.LayerRegionDockWidget('图层管理区', self)
        self.tips_region = RegionDockWidget.TipsRegionDockWidget('文本提示区', self)
        self.draw2_region=RegionDockWidget.Draw2RegionDockWidget('展示区',self)

    # 初始化全部
    def initAll(self):
        self.initFile()  # 初始化相关全局变量
        self.initLabelLayer()
        self.initHistory()
        self.scan_region.clearAll()  # 清理文件
        self.draw_region.clearAll()  # 清理图片
        self.updateAll()

    # 初始化相关全局变量
    def initFile(self):
        # 下面三个在region中赋值
        self.file_path = None  # 文件（图片）路径
        self.img = None  # 加入图像
        self.denoisy_img = None  # 载入图像去噪后图像，便于区域生长

        self.shape = self.tool_region.pen_dict[self.tool_region.pen_bg.checkedId()]  # 画笔类型
        self.pen_width = self.tool_region.width.value()  # 画笔宽度
        self.pen_transparency = self.tool_region.transparency_qpb.value()  # 画笔透明度

        self.final_save = False  # 是否需要保存

    # 初始化MyLabel层
    def initLabelLayer(self):
        self.scale_file={}#比例尺字典
        self.meg_statue=False  #用来控制放大镜的
        self.current_label_index = 0  # 指向当前置顶的label层
        self.label_more = [[]for i in range (20)]#不同图片的label层集合,注意列表的写法 https://blog.csdn.net/cxj540947672/article/details/85257589
        self.pred_more=[[]for i in range (20)]#电子致密物的返回数组
        self.label_layers = []#label层
        self.temp_label_layers=[[]for i in range(3)]#临时在看框架时装这个
        self.label_namelist=[] # 照片文件名列表
        self.label_now=None#当前文件名
        self.layer_region.clearAll()  # 清理图层表格，直接行数置零
        self.label_new=0#是否已打开图片
        self.label_scale=0#比例系数
        self.dintance=[]

    # 初始化历史
    def initHistory(self):
        self.history_list = []  # 历史列表置空
        self.current_history_index = 0  # 当前历史的索引
        self.history_region.clearAll()  # 历史树清零

    # 设置所有窗口布局
    def setWindowStyle(self):
        self.draw_region.setFeatures(QDockWidget.NoDockWidgetFeatures)  # 设置特征，不可移动、关闭
        #self.tips_region.setFeatures(QDockWidget.DockWidgetClosable)  # 可关闭
        self.scan_region.show()
        self.history_region.show()
        #self.history_region.setFloating(True)
        self.tool_region.show()
        self.tool_region.hide()
        self.algorithm_region.show()
        self.layer_region.show()
        self.draw_region.show()
        self.tips_region.show()

        # self.setCentralWidget(self.draw_region)
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.scan_region)
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.history_region)
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.tips_region)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.tool_region)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.algorithm_region)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.layer_region)

        self.addDockWidget(Qt.TopDockWidgetArea, self.scan_region)
        self.splitDockWidget(self.scan_region, self.draw_region, Qt.Horizontal)
        self.splitDockWidget(self.draw_region, self.algorithm_region, Qt.Horizontal)

        #self.splitDockWidget(self.scan_region, self.history_region, Qt.Vertical)
        #self.splitDockWidget(self.draw_region, self.tips_region, Qt.Vertical)
        #self.splitDockWidget(self.tool_region, self.algorithm_region, Qt.Vertical)
        self.splitDockWidget(self.algorithm_region, self.layer_region, Qt.Vertical)
        self.splitDockWidget(self.layer_region, self.history_region, Qt.Vertical)
        self.splitDockWidget(self.scan_region, self.tips_region, Qt.Vertical)
        self.splitDockWidget(self.tips_region, self.tool_region, Qt.Vertical)

        self.tabifyDockWidget(self.draw_region, self.draw2_region)
        self.draw_region.raise_()





    # 更新光标
    def updateCursor(self):
        if len(self.label_layers) == 0:
            return

        # 所有可视图层使用“空白”鼠标光标，所有不可视图层使用“正常”鼠标光标
        if self.label_layers[self.current_label_index - 1].isVisible():
            for layer in self.label_layers:
                layer.setCursor(QCursor(Qt.BlankCursor))
                layer.clearShowStatue()
        else:
            for layer in self.label_layers:
                layer.unsetCursor()
                layer.clearShowStatue()

        # 当前图层显示初始化
        self.label_layers[self.current_label_index - 1].initShowStatue()

    # 更新所有
    def updateAll(self):
        self.tool_region.updateCheckStatue()
        self.algorithm_region.updateButtonStatue()
        self.layer_region.updateButtonStatue()
        self.menubar.updateAll()
        self.updateCursor()

    # 清除集中的窗体
    def clearAllFocus(self):
        try:
            focused_widget = QApplication.focusWidget()
            focused_widget.clearFocus()
        except:
            pass

    # 鼠标点击事件
    def mousePressEvent(self, QMouseEvent):
        self.clearAllFocus()
        pass

    # 退出程序事件
    def closeEvent(self, event):
        if self.final_save == True:  # 图层还未保存
            quitbox = QMessageBox()
            quitbox.setWindowTitle('提醒')
            quitbox.setText('是否保存各图层？')
            quitbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            button_x = quitbox.button(QMessageBox.Yes)
            button_x.setText('是')
            button_y = quitbox.button(QMessageBox.No)
            button_y.setText('否')
            button_c = quitbox.button(QMessageBox.Cancel)
            button_c.setText('取消')
            quitbox.exec_()
            if quitbox.clickedButton() == button_x:
                self.menubar.saveImage()
                event.accept()
            elif quitbox.clickedButton() == button_y:
                event.accept()
            else:
                event.ignore()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyMainWindow()
    main.show()
    sys.exit(app.exec_())
