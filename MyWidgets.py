from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import MyHistory
import cv2
import numpy as np
import json

import RegionDockWidget
from JsonFile import create_Json
from LabelAlgorithm import Labels
from RegionDockWidget import *

class MyMenuBar(QMenuBar):
    import MainGUI
    def __init__(self, parent: MainGUI.MyMainWindow):
        super(MyMenuBar, self).__init__(parent)
        self.parent_ = parent

        #文件工具栏
        self.file_tool = parent.addToolBar("File")
        self.new = QAction(QIcon('./icon/new.webp'),"new", self)
        self.file_tool.addAction(self.new)
        self.new.triggered.connect(self.loadImage)

        self.dir = QAction(QIcon('./icon/dir.jpg'), "dir", self)
        self.file_tool.addAction(self.dir)
        self.dir.triggered.connect(self.loadImages)

        self.savet = QAction(QIcon('./icon/save.webp'), "savet", self)
        self.file_tool.addAction(self.savet)
        self.savet.triggered.connect(self.saveImage)

        #编辑工具栏
        self.edit_tool = parent.addToolBar("Edit")
        self.undo = QAction(QIcon('./icon/undo.webp'), "undo", self)
        self.edit_tool.addAction(self.undo)
        self.undo.triggered.connect(self.undof)

        self.redo = QAction(QIcon('./icon/redo.webp'), "redo", self)
        self.edit_tool.addAction(self.redo)
        self.redo.triggered.connect(self.redof)



        # 文件菜单
        self.file_menu = self.addMenu("文件")
        self.open_img = QAction("打开图片", self)
        self.open_img.setObjectName('open_img')
        self.open_img.setShortcut('Ctrl+O')
        self.file_menu.addAction(self.open_img)

        self.open_folder = QAction("打开文件夹", self)  # 目前软件整体架构还是为了一张图像服务（暂时不启用）
        self.open_folder.setObjectName('open_folder')
        self.open_folder.setShortcut('Ctrl+Shift+O')
        self.file_menu.addAction(self.open_folder)

        self.save = QAction("保存", self)
        self.save.setObjectName('save')
        self.file_menu.addAction(self.save)
        self.save.setShortcut("Ctrl+Shift+S")  # 快捷键

        self.save_as=QAction("另存为",self)
        self.save_as.setObjectName('save_as')
        self.file_menu.addAction(self.save_as)
        self.save_as.setShortcut("Ctrl+alt+S")

        self.save_json = QAction("保存当前图层的矩形框信息", self)
        self.save_json.setObjectName('save_json')
        self.file_menu.addAction(self.save_json)

        self.load_json= QAction("加载矩形框信息", self)
        self.load_json.setObjectName('load_json')
        self.file_menu.addAction(self.load_json)

        self.quit = QAction("退出", self)
        self.quit.setObjectName('quit')
        self.file_menu.addAction(self.quit)
        self.quit.setShortcut("E")

        # 编辑菜单
        self.edit_menu = self.addMenu("编辑")
        self.undo_qat = QAction("←撤销", self)
        self.undo_qat.setObjectName('undo_qat')
        self.undo_qat.setShortcut('Ctrl+Z')
        self.edit_menu.addAction(self.undo_qat)

        self.redo_qat = QAction("→还原", self)
        self.redo_qat.setObjectName('redo_qat')
        self.redo_qat.setShortcut('Ctrl+Shift+Z')
        self.edit_menu.addAction(self.redo_qat)

        self.part_meg=QAction("放大镜",self)
        self.part_meg.setObjectName('part_meg')
        self.part_meg.setShortcut('M')
        self.edit_menu.addAction(self.part_meg)


        self.show_hidden = QAction("隐藏/显示当前图层", self)
        self.show_hidden.setObjectName('show_hidden')
        self.show_hidden.setShortcut('V')
        self.edit_menu.addAction(self.show_hidden)

        self.clear = QAction("清空", self)
        self.clear.setObjectName('clear')
        self.clear.setShortcut('Ctrl+Shift+P')
        self.edit_menu.addAction(self.clear)

        #窗口菜单
        self.win_menu = self.addMenu("窗口")

        self.file_reg = QAction("文件浏览区", self)
        self.file_reg.setObjectName('file_reg')
        self.win_menu.addAction(self.file_reg)
        self.file_reg.setShortcut("F")

        self.his_reg = QAction("历史记录区", self)
        self.his_reg.setObjectName('his_reg')
        self.win_menu.addAction(self.his_reg)
        self.his_reg.setShortcut("H")

        self.tool_reg = QAction("工具管理区", self)
        self.tool_reg.setObjectName('tool_reg')
        self.win_menu.addAction(self.tool_reg)
        self.tool_reg.setShortcut("T")

        self.alg_reg = QAction("方法区", self)
        self.alg_reg.setObjectName('alg_reg')
        self.win_menu.addAction(self.alg_reg)
        self.alg_reg.setShortcut("A")

        self.layer_reg = QAction("图层管理区", self)
        self.layer_reg.setObjectName('layer_reg')
        self.win_menu.addAction(self.layer_reg)
        self.layer_reg.setShortcut("L")

        self.tips_reg = QAction("文本提示区", self)
        self.tips_reg.setObjectName('tips_reg')
        self.win_menu.addAction(self.tips_reg)
        self.tips_reg.setShortcut("I")

        self.win_default = QAction("默认风格", self)
        self.win_default.setObjectName('win_default')
        self.win_default.setShortcut('D')
        self.win_menu.addAction(self.win_default)


        self.open_img.triggered.connect(self.loadImage)
        self.open_folder.triggered.connect(self.loadImages)
        self.save.triggered.connect(self.saveImage)   #保存图片
        self.save_as.triggered.connect(self.saveImage)  # 另存为
        self.save_json.triggered.connect(self.saveJson)
        self.load_json.triggered.connect(self.loadJson)
        self.quit.triggered.connect(self.quitApp)   #退出
        self.undo_qat.triggered.connect(self.undoOrRedo)   #撤销
        self.redo_qat.triggered.connect(self.undoOrRedo)    #恢复
        self.part_meg.triggered.connect(self.partMeg)
        self.show_hidden.triggered.connect(self.showOrHidden)   #隐藏/显示当前图层
        self.clear.triggered.connect(self.parent_.initAll)    #清空
        self.win_default.triggered.connect(self.parent_.setWindowStyle)
        self.file_reg.triggered.connect(self.dockWindowShow)
        self.his_reg.triggered.connect(self.dockWindowShow)
        self.tool_reg.triggered.connect(self.dockWindowShow)
        self.alg_reg.triggered.connect(self.dockWindowShow)
        self.layer_reg.triggered.connect(self.dockWindowShow)
        self.tips_reg.triggered.connect(self.dockWindowShow)

        self.all_widget = [self.open_img,self.save,self.save_as,self.save_json, self.load_json,self.quit, self.undo_qat, self.redo_qat,
                           self.part_meg,self.show_hidden, self.clear]



    # 打开单张图片
    def loadImage(self):

        #初始化5个图层
        if self.parent_.label_new==0:
            self.parent_.label_new = 1
            for i in range (6):
                self.parent_.layer_region.newLabel()


        file_path, _ = QFileDialog.getOpenFileName(self, "打开文件", './', '图像文件(*.jpg *.png *.jpeg)')
        #中文路径

        if os.path.exists(file_path):

            self.parent_.scan_region.addFileToTree(file_path)#往文件区的树添加图片
            #self.parent_.draw_region.setPic(file_path)    #在此处设置图片
            self.parent_.history_region.addHistroyToTree(
                MyHistory.History(type_=MyHistory.OPEN_FILE, mainwindow=self.parent_))

            #初始化放大镜
            self.parent_.meg_statue=False
            self.parent_.tool_region.btn.setText("放大镜")
            self.parent_.draw_region.roi.hide()
            self.parent_.draw_region.meg_image = QPixmap()
            self.parent_.draw_region.meg_pic.setPixmap(self.parent_.draw_region.meg_image)
            #提示
            self.parent_.tips_region.text_tips.setPlainText('打开图片成功:\n请点击“模型预测”以获得自动分割结果')

    # 打开文件夹，实现浏览多张图像
    def loadImages(self):

        #初始化5个图层
        if self.parent_.label_new==0:
            self.parent_.label_new = 1
            for i in range (6):
                self.parent_.layer_region.newLabel()

        path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")#文件夹路径
        if path:
            dirs = os.listdir(path)#返回文件夹中所有文件的名称
            fileInfo = QFileInfo(path)  # 获取文件综合信息
            fileIcon = QFileIconProvider()  # 生成一个控制器,用来获取fileInfo中的某条信息
            icon = QIcon(fileIcon.icon(fileInfo))#图标

            root = QTreeWidgetItem(self.parent_.scan_region.scan_tree)  # 根节点
            root.setText(0, path.split('/')[-1])#根节点的名字定为：文件夹名称；split的意思是，所有该字符的地方切一刀，组成数组
            root.setIcon(0, QIcon(icon))

            self.createTree(dirs, root, path)  # 递归创建子节点
            QApplication.processEvents()  # 实时刷新页面

        self.openscale()

    # 递归创建子节点
    def createTree(self, dirs, root, path):#文件夹中所有文件名，根，文件夹路径
        for i in dirs:

            path_new = path + '/' + i
            #path是文件夹路径,i是文件名，path_new是文件路径，斜线别反了…………
            #每打开一个图片，新建一个大图层
            if not os.path.isdir(path_new):
                self.parent_.label_num=1

            fileInfo = QFileInfo(path_new)
            fileIcon = QFileIconProvider()
            icon = QIcon(fileIcon.icon(fileInfo))

            child = QTreeWidgetItem(root)
            child.setText(0, i)
            child.setText(1, path_new)
            child.setIcon(0, QIcon(icon))

            if os.path.isdir(path_new):#如果是文件夹，递归创建子树
                dirs_new = os.listdir(path_new)
                self.createTree(dirs_new, child, path_new)

    # 保存label图片
    def saveImage(self):
        try:
            button=self.sender()
            if button==None:
                button_name="save"
            else:
                button_name=button.objectName()

            if button_name=="save_as":   #另存为
                file_path = self.parent_.file_path  # 打开图片的路径
                _, file_name = os.path.split(file_path)  # 返回文件的路径和文件名
                file_name = file_name.split('.')[0]

                save_folder, ok = QFileDialog.getSaveFileName(None, "文件保存", "E:/")
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)   #创建多层目录

            else:  #保存
                self.parent_.final_save=False
                file_path = self.parent_.file_path  #打开图片的路径E:/Pycharm_FILE/GUI/InteractiveSeg-source/Img/2_335_09_0_1.png
                _, file_name = os.path.split(file_path)   #返回文件的路径和文件名file_name=2_335_09_0_1.png
                file_name = file_name.split('.')[0]       #文件名（不包括扩展名）file_name=2_335_09_0_1
                save_folder = os.path.join('Save',file_name)    #保存路径文件夹save_folder=Save\2_335_09_0_1
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)   #创建多层目录

            # 解决中文路径保存问题  cv2.imwrite(imagepath, frame)---->cv2.imencode('.jpg', frame)[1].tofile(imagepath)
            # 每个label单独保存一份[0,1]图像和rgb图像
            label_merge = np.zeros((512, 512), dtype=np.uint8)
            label_merge_bgr = np.zeros((512, 512, 3), dtype=np.uint8)

            #cv2.imdecode()函数从指定的内存缓存中读取数据，并把数据转换(解码)成图像格式;主要用于从网络传输数据中恢复出图像
            #cv2.imencode()函数是将图片格式转换(编码)成流数据，赋值到内存缓存中;主要用于图像数据格式的压缩，方便网络传输。
            for i, layer in enumerate(self.parent_.label_layers):    #enumerate内置函数：组合为一个索引序列,i是序列，layer是图层
                label_bgr = cv2.cvtColor(layer.label_rgb, cv2.COLOR_RGB2BGR)
                cv2.imencode('.jpg', layer.label_mask)[1].tofile(os.path.join(save_folder, file_name + '_laberl{}.{}'.format(i + 1, 'png')))
                cv2.imencode('.jpg', label_bgr)[1].tofile(os.path.join(save_folder, file_name + '_rgblaberl{}.{}'.format(i + 1, 'png')))

                label_merge += layer.label_mask  #??
                label_merge_bgr += label_bgr
            # 组合保存一份[0,1,2,3...]图像和rgb图像
            cv2.imencode('.jpg', label_merge)[1].tofile(os.path.join(save_folder, file_name + '_laberl.{}'.format('png')))
            cv2.imencode('.jpg', label_merge_bgr)[1].tofile(os.path.join(save_folder, file_name + '_rgblaberl.{}'.format('png')))

            origin_img = cv2.imread(file_path)  #原图
            merge_img = cv2.addWeighted(origin_img, 0.8, label_merge_bgr, 0.2, 0)
            cv2.imencode('.jpg', merge_img)[1].tofile(os.path.join(save_folder, file_name + '_merge.{}'.format('png')))
            #!!!!!为什么没有保存下来？？？？

            self.parent_.status.showMessage('标记保存于: {}'.format(save_folder))
        except:
            pass

    #打开比例尺文件
    def openscale(self):
        s_root = './Json/UGFBdatalist.json'
        with open(s_root, 'r') as f:
            file = json.load(f)
        self.parent_.scale_file = file

    # 保存json文件
    def saveJson(self):
        for label in self.parent_.label_layers:
            if label.layer_index==self.parent_.current_label_index:   #当前选中层的层数
                number = label.count
                if number!=0:
                    create_Json(self.parent_.file_path, number, label)
                    QMessageBox.information(self, "消息", "矩形框信息保存成功！")
                else:
                    QMessageBox.warning(self, "提示", "当前层无矩形框，请重新确认！")
    #加载矩形信息
    def loadJson(self):
        json_path, _ = QFileDialog.getOpenFileName(self, "打开文件", './', 'Json文件(*.json)')
        file = json.load(open(json_path, 'r'))
        rect = file['rect']
        count = len(rect)  # 矩形个数
        height, width = (512, 512)
        json_mask= np.zeros((height, width), dtype=np.uint8)
        pen_width = 6  # 画笔线宽默认为5
        for i in range(0, count):
            begin= rect[i]['point_1']
            end=rect[i]['point_2']
            if begin[0][0]>end[0][0]:
                end = rect[i]['point_1']
                begin = rect[i]['point_2']
            x1=begin[0][0]
            y1=begin[0][1]
            x2=end[0][0]
            y2=end[0][1]
            for m in range(x1-1, x2+1):
                for n in range(y1-1, y2+1):
                    json_mask[n, m] = 255
            for m in range(x1+pen_width, x2-pen_width):
                for n in range(y1+pen_width, y2-pen_width):
                    json_mask[n, m] = 0

        labels=Labels(json_mask,module='new')

        if labels is None:
            return

        for i in labels.indexes:
            label_mask = (labels.labels == i).astype(np.uint8) #存在的部分赋值
            self.parent_.layer_region.newLabel()
            self.parent_.label_layers[self.parent_.current_label_index - 1].loadLabelMask(label_mask)
            self.parent_.label_layers[self.parent_.current_label_index - 1].count=count
            for i in range(1,count+1):     #新加载的矩形图层中添加矩形信息
                begin=(rect[i-1]['point_1'][0][0],rect[i-1]['point_1'][0][1])
                end=(rect[i-1]['point_2'][0][0],rect[i-1]['point_2'][0][1])
                self.parent_.label_layers[self.parent_.current_label_index - 1].json[i].append(i)
                self.parent_.label_layers[self.parent_.current_label_index - 1].json[i].append(begin)
                self.parent_.label_layers[self.parent_.current_label_index - 1].json[i].append(end)
        history_type=MyHistory.LOADJSON
        if history_type is not None:
            label_mask_ = self.parent_.label_layers[self.parent_.current_label_index - 1].label_mask.copy()
            count_ = self.parent_.label_layers[self.parent_.current_label_index - 1].count
            json_ = self.parent_.label_layers[self.parent_.current_label_index - 1].json
            history = MyHistory.History(type_=history_type, mainwindow=self.parent_,
                                        label_mask=label_mask_, layer_index=self.parent_.current_label_index,
                                        count=count_, json=json_)
            self.parent_.history_region.addHistroyToTree(history)

    # 撤销和恢复
    def undoOrRedo(self):
        one_step = 0
        sender_name = self.sender().objectName()

        if sender_name == 'undo_qat':
            one_step = -1
        elif sender_name == 'redo_qat':
            one_step = 1
        step = one_step
        self.parent_.history_region.undoRedoWithStep(step)
        
    def undof(self):
        one_step = -1
        self.parent_.history_region.undoRedoWithStep(one_step)
    def redof(self):
        one_step = 1
        self.parent_.history_region.undoRedoWithStep(one_step)

    # 快捷显示或隐藏图层
    def showOrHidden(self):
        cb = self.parent_.layer_region.findChild(QCheckBox, str(self.parent_.current_label_index))
        cb.setChecked(not cb.isChecked())

    #浮动窗口的显示
    def dockWindowShow(self):
        button=self.sender()
        if button.objectName()=="file_reg":
            self.parent_.scan_region.show()
        elif button.objectName()=="his_reg":
            self.parent_.history_region.show()
        elif button.objectName() == "tool_reg":
            self.parent_.tool_region.show()
        elif button.objectName() == "alg_reg":
            self.parent_.algorithm_region.show()
        elif button.objectName() == "layer_reg":
            self.parent_.layer_region.show()
        elif button.objectName() == "tips_reg":
            self.parent_.tips_region.show()

    #局部放大
    def partMeg(self):
        self.parent_.meg_statue=not self.parent_.meg_statue#如果false则true，反之亦然
        if self.parent_.meg_statue==False:      #放大镜关闭
            self.parent_.tool_region.btn.setText("放大镜")
            self.parent_.draw_region.roi.hide()
            self.parent_.draw_region.meg_image=QPixmap()
            self.parent_.draw_region.meg_pic.setPixmap(self.parent_.draw_region.meg_image)
        else:
            self.parent_.tool_region.btn.setText("放大镜(正在使用)")
            self.parent_.draw_region.roi.show()
            self.parent_.draw_region.meg_image = QPixmap()

            x=self.parent_.draw_region.roi.xx
            y=self.parent_.draw_region.roi.yy

            rect = QRect(QPoint(x++ 75 + 19, y+60-10), QSize(150, 120))
            self.parent_.draw_region.roi.getMegpic(rect)

    # 更新全部
    def updateAll(self):
        for widget in self.all_widget:
            widget.setEnabled(True)

        if self.parent_.file_path is None:
            self.save.setEnabled(False)
            self.save_as.setEnabled(False)
            self.part_meg.setEnabled(False)
            self.clear.setEnabled(False)
            self.save_json.setEnabled(False)
            self.load_json.setEnabled(False)

        if self.parent_.current_label_index == 0:
            self.show_hidden.setEnabled(False)
            self.save.setEnabled(False)
            self.save_as.setEnabled(False)
            self.save_json.setEnabled(False)
            # self.part_meg.setEnabled(False)

        if len(self.parent_.history_list) == 0:
            self.undo_qat.setEnabled(False)
            self.redo_qat.setEnabled(False)

        if self.parent_.current_history_index == 1:
            self.undo_qat.setEnabled(False)

        if self.parent_.current_history_index == len(self.parent_.history_list):
            self.redo_qat.setEnabled(False)

        # self.open_folder.setEnabled(False)

     # 退出程序
    def quitApp(self):
        if self.parent_.final_save == True:  # 图层还未保存
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
                self.parent_.menubar.saveImage()
                app = QApplication.instance()
                app.quit()
            elif quitbox.clickedButton() == button_y:
                app = QApplication.instance()
                app.quit()
        else:
            app = QApplication.instance()
            app.quit()





