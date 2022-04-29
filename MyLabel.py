from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import cv2
import numpy as np
import MyHistory
import RegionDockWidget


# 创建新类——单击label响应事件
class MyLabel(QLabel):
    #颜色列表
    LABEL_COLORS = [
        (0, 0, 0),
        (230, 20, 20),
        (20, 230, 20),
        (20, 20, 230),
        (230, 230, 20),
        (230, 20, 230),
        (20, 230, 230),
        (20, 230, 160),
        (160, 20, 230),
        (20, 160, 230),

    ]

    import MainGUI
    #注意区分parent和mainwindow，因为mylabel要被两者使用
    def __init__(self, parent=None, mainwindow: MainGUI.MyMainWindow = None):
        super(MyLabel, self).__init__((parent))
        self.mainwindow = mainwindow
        self.initUI()

    def initUI(self):

        # Some Variable
        self.layer_index = len(self.mainwindow.label_layers) + 1  # Label的索引
        self.color = self.LABEL_COLORS[self.layer_index]  # 元组
        self.qcolor = QColor(*self.color)  # *表示把元组排序传入参数，此处获得真颜色
        self.drawable = True  # 是否可画
        self.transparency=255  #透明度

        # Draw and Show
        self.label_mask = np.zeros((512, 512), dtype=np.uint8)  # 真实勾画的label_mask，0:bg 1:fg
        self.label_show = self.label_mask.copy()  # 用来显示的二级label,是一个512*512*256的二维矩阵，不返回label_mask的都是一次性显示的
        self.label_rgb = None  # 相应的rgb图像
        self.image_show = QImage(512, 512, QImage.Format_ARGB32)# 要展示在界面的图像

        #Format_ARGB32是一种图片格式，有4个分量，分别为透明度、rgb

        # Draw statue
        self.begin = (0, 0)  # 起始点（划线和矩形）
        self.end = (0, 0)  # 结束点
        self.line_statue = -1  # 画线的线数目
        self.rect_start = False  # 画矩阵的状态判断
        self.dir_statue=-1 #最初没有画

        # other
        self.setMouseTracking(True)  # 开启追踪鼠标
        self.setCursor(QCursor(Qt.BlankCursor))  # 这是‘空白’鼠标样式
        self.setFocusPolicy(Qt.StrongFocus)#设定如何才能接受焦点

        # json保存矩形信息
        self.json = [[] for i in range(50)]  # 定义二维信息列表
        self.count = 0

    # 从numpy形式的label转换成显示在界面上的Qimage，即label_show 转 image_show
    def getQImageFromNpLabel(self, np_label):

        np_label_bool = np_label == 1 #该代码的意思是，判定np_label是否=1，返回要覆盖的矩阵，np_label就是label_show
        #np_label_bool.shape就是512*512,self.label_rgb是512*512*3的图的数组形式
        self.label_rgb = np.zeros((*np_label_bool.shape, 3), dtype=np.uint8)#生成512*512*3
        self.label_rgb[np_label_bool, :] = self.color #有label的地方设置为相应的颜色,label_rgb元组有三个,写得漂亮

        #cv2.cvtColor就是转换图片的意思，参数：要转换的图片，转换类型
        label_bgra = cv2.cvtColor(self.label_rgb, cv2.COLOR_RGB2BGRA)  # Qimage的argb格式与numpy相反，因此要转为bgra,np是反的，label_bgra元组有4个
        label_bgra[np.logical_not(np_label_bool), 3] = 0  # 没有label的地方设置成全透明，该函数表述false的地方的alpha值为0


        #最终是通过这一步修改透明度的
        if self.mainwindow.current_label_index == self.layer_index:  #仅改变当前图层的透明度
            label_bgra[np_label_bool, 3] = self.mainwindow.pen_transparency  # 有label的设置成指定透明度，使用的值是通过工具栏传给mainwindow的
            self.transparency=self.mainwindow.pen_transparency
        else:
            label_bgra[np_label_bool, 3] = self.transparency#为什么要这么写？？

        image_show = QImage(label_bgra.data, 512, 512, QImage.Format_ARGB32)

        if np.all(self.label_mask == 0):#如果图层全空，则不允许后续操作
            self.mainwindow.algorithm_region.grabcut.setEnabled(False)#图论分割
            self.mainwindow.algorithm_region.erosion.setEnabled(False)#边缘削减
            self.mainwindow.layer_region.clear_label_btn.setEnabled(False)#清除当前图层
        else:
            self.mainwindow.algorithm_region.grabcut.setEnabled(True)
            self.mainwindow.algorithm_region.erosion.setEnabled(True)
            self.mainwindow.layer_region.clear_label_btn.setEnabled(True)

        return image_show

    # 载入新的label_mask
    def loadLabelMask(self, label_mask):
        self.label_mask = label_mask  # 0:bg 1:fg
        self.label_show = self.label_mask.copy()
        self.image_show = self.getQImageFromNpLabel(self.label_show)
        self.update()

    # ！！！！！！paint事件,就是这个事件绘制了image_show
    def paintEvent(self, event):
        temp_painter = QPainter(self)
        temp_painter.scale(self.mainwindow.draw_region.magnification, self.mainwindow.draw_region.magnification)
        temp_painter.drawImage(0,0, self.image_show)
        temp_painter.end()

    # 鼠标按下事件
    def mousePressEvent(self, QMouseEvent):
        #if not 的意思是if x is not
        if not self.drawable or self.mainwindow.current_label_index != self.layer_index:
            return

        shape = self.mainwindow.shape
        pen_width = self.mainwindow.pen_width

        # 鼠标左键按下
        if QMouseEvent.button() == Qt.LeftButton:

            if self.mainwindow.shape == '移动':
               #暂时没写出来
                return

            if shape == '点':  # 画点
                self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
                #画布，中心，半径，边界颜色(bgr)，边界粗细（-1为填充）
                cv2.circle(self.label_mask, self.begin, pen_width, 1, -1)
                self.label_show = self.label_mask.copy()#改变了label_mask,复制给labels_show

            elif shape == '线':  # 画线
                if self.line_statue == -1:
                    self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
                else:  #第一次点击只能确定一点，后续的点击是绘制折线
                    # 画入label_mask，作为真实标签
                    cv2.line(self.label_mask, self.begin, self.end, 1, pen_width * 2)#end在鼠标移动的时候赋值
                    self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())#再次作为起点
                self.line_statue += 1

                self.label_show = self.label_mask.copy()

            elif shape=='测距':
                if self.dir_statue == -1:
                    self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
                    self.dir_statue = 1

                else:
                    for i in range(10):#画虚线
                        endi = (int(self.begin[0] + (self.end[0] - self.begin[0]) / 10 * i),
                                int(self.begin[1] + (self.end[1] - self.begin[1]) / 10 * i))
                        cv2.circle(self.label_mask, endi, 1, 1, -1)
                    self.dir_statue=-1

                    x=self.end[0]-self.begin[0]
                    y=self.end[1]-self.begin[1]
                    point=(self.begin[0],self.begin[1]-5)
                    font = cv2.FONT_HERSHEY_SIMPLEX  # 字体
                    if self.mainwindow.label_scale==0:
                        direct=(x*x+y*y)**0.5
                        cv2.putText(self.label_mask, str(round(direct, 3))+'pix' , point, font, 0.5, 1, 1)
                    else:
                        direct=((x*x+y*y)**0.5)*0.1575/int(self.mainwindow.label_scale)*1000
                        cv2.putText(self.label_mask, str(int(direct)) + 'nm', point, font, 0.5, 1, 1)








            elif shape == '矩形':  # 画矩形
                if not self.rect_start:   #rect_start==False，为什么不直接一点？
                    self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
                else:
                    # 画入label_mask，作为真实标签
                    cv2.rectangle(self.label_mask, self.begin, self.end, 1, pen_width)  #pen_width表示矩形线宽，当为-1值时表示填充矩形框
                self.rect_start = not self.rect_start

                self.label_show = self.label_mask.copy()

            elif shape == '橡皮檫':  # 橡皮擦，基本同画线
                self.begin = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
                cv2.circle(self.label_mask, self.begin, pen_width, 0, -1)#直接抹0

                self.label_show = self.label_mask.copy()

            elif shape == '区域生长':  # 区域生长
                seed_xy = (QMouseEvent.pos().y(), QMouseEvent.pos().x())
                para_dict = {'algorithm_name': '区域生长', 'seed_xy': seed_xy}
                self.mainwindow.algorithm_region.getLabelsByAlgorithm(para_dict)

            if (QApplication.keyboardModifiers() == Qt.ShiftModifier):
                self.mainwindow.draw_region.roi.raise_()    #虚线框置顶

        # 鼠标右键按下
        if QMouseEvent.button() == Qt.RightButton:
            self.initShowStatue()  #强断

        if (QApplication.keyboardModifiers() == Qt.ShiftModifier):
            self.mainwindow.draw_region.roi.raise_()#设置控件在最上层
        self.update()
        self.drawPen()

    # 鼠标移动事件
    def mouseMoveEvent(self, QMouseEvent):
        if not self.drawable or self.mainwindow.current_label_index != self.layer_index or self.mainwindow.pen_width < 1:
            return

        shape = self.mainwindow.shape
        pen_width = self.mainwindow.pen_width

        if self.mainwindow.shape == '移动':
            #没写出来
            return

        if shape == '点' and QMouseEvent.buttons() == Qt.LeftButton:  # 移动画点
            self.end = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
            cv2.line(self.label_mask, self.begin, self.end, 1, pen_width * 2)#画很多细小折线
            #cv2.circle(self.label_mask, self.begin, pen_width, 1, -1)#用这个可能会出现断断续续的情况
            self.begin = self.end

            self.label_show = self.label_mask.copy()

        elif shape == '线' and self.line_statue != -1:  # 画出‘画线’的轨迹
            self.label_show = self.label_mask.copy()
            self.end = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
            cv2.line(self.label_show, self.begin, self.end, 1, pen_width * 2)
            #注意顺序，只在label_show上面画了，只会显示一次，而不在label_mask上留下痕迹

        elif shape == '测距' and self.dir_statue !=-1:
            self.label_show = self.label_mask.copy()
            self.end = (QMouseEvent.pos().x(), QMouseEvent.pos().y())

            for i in range (10):
                endi=(int(self.begin[0]+(self.end[0]-self.begin[0])/10*i),int(self.begin[1]+(self.end[1]-self.begin[1])/10*i))
                cv2.circle(self.label_show,endi,1,1,-1)


        elif shape == '矩形' and self.rect_start:  # 画出‘画矩阵’的轨迹
            self.label_show = self.label_mask.copy()

            self.end = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
            cv2.rectangle(self.label_show, self.begin, self.end, 1,pen_width)   #pen_width表示矩形线宽，当为-1值时表示填充矩形框

        elif shape == '橡皮檫' and QMouseEvent.buttons() == Qt.LeftButton:  # 移动擦除
            self.end = (QMouseEvent.pos().x(), QMouseEvent.pos().y())
            cv2.line(self.label_mask, self.begin, self.end, 0, pen_width * 2)
            self.begin = self.end

            self.label_show = self.label_mask.copy()

        elif shape == '区域生长' and QMouseEvent.buttons() == Qt.LeftButton:  # 移动区域生长
            seed_xy = (QMouseEvent.pos().y(), QMouseEvent.pos().x())
            para_dict = {'algorithm_name': '区域生长', 'seed_xy': seed_xy}
            self.mainwindow.algorithm_region.getLabelsByAlgorithm(para_dict)

        else:
            self.label_show = self.label_mask.copy()


        self.drawPen()
        #图片局部放大
        if self.mainwindow.meg_statue==True:
            x = self.mainwindow.draw_region.roi.x0
            y = self.mainwindow.draw_region.roi.y0

            rect=QRect(QPoint(x+75+19,y+60-10),QSize(150,120))   #x+94-75,y+50-60
            self.mainwindow.draw_region.meg_image = QPixmap()
            self.mainwindow.draw_region.meg_image = self.mainwindow.draw_region.main_widget.grab(rect)
            width = self.mainwindow.draw_region.meg_image.width()
            height = self.mainwindow.draw_region.meg_image.height()
            meg = self.mainwindow.draw_region.meg_number
            self.mainwindow.draw_region.meg_image =self.mainwindow.draw_region.meg_image\
                .scaled(width*meg,height*meg,Qt.KeepAspectRatio)
            self.mainwindow.draw_region.meg_pic.setPixmap(self.mainwindow.draw_region.meg_image)
        self.update()

    # 鼠标滚轮事件
    # def wheelEvent(self, QMouseEvent):
    #     if not self.drawable or self.mainwindow.current_label_index != self.layer_index:
    #         return
    #
    #     # 滚动鼠标缩放画笔大小
    #     scroll_direction = np.sign(QMouseEvent.angleDelta().y())
    #     if (QApplication.keyboardModifiers() ==  Qt.ControlModifier):   #Qt.ShiftModifier  ctrl+滚轮
    #         new_transparency = self.mainwindow.tool_region.transparency_qpb.value() + scroll_direction * 10
    #         self.mainwindow.tool_region.transparency_qpb.setValue(new_transparency)
    #     else:
    #         new_width = self.mainwindow.tool_region.width.value() + scroll_direction
    #         self.mainwindow.tool_region.width.setValue(new_width)
    #
    #     self.mouseMoveEvent(QMouseEvent)
    #
    #     self.drawPen()

    # 鼠标释放事件，作为生成历史的触发点
    def mouseReleaseEvent(self, QMouseEvent):
        if not self.drawable or self.mainwindow.current_label_index != self.layer_index:
            return

        shape = self.mainwindow.shape

        # 鼠标左键释放，不同画笔的历史生成条件不一致
        history_flag = False
        if QMouseEvent.button() == Qt.LeftButton:
            if shape == '线':
                if self.line_statue > 0:
                    history_flag = True
            elif shape == '矩形':
                if self.rect_start == False:
                    history_flag = True
                    self.count += 1
                    self.json[self.count].append(self.count)
                    self.json[self.count].append(self.begin)
                    self.json[self.count].append(self.end)
            else:
                history_flag = True

        if history_flag:
            self.mainwindow.history_region.addHistroyToTree(
                MyHistory.History(
                    type_=MyHistory.DRAW, mainwindow=self.mainwindow,
                    label_mask=self.label_mask.copy(), pen_shape=self.mainwindow.shape,
                    layer_index=self.layer_index,count=self.count,json=self.json))

    # 鼠标离开窗口事件
    def leaveEvent(self, QMouseEvent):
        self.image_show = self.getQImageFromNpLabel(self.label_show)
        self.mainwindow.draw_region.meg_image=QPixmap()#放大区域图片？？？？？？
        self.update()

    #鼠标键盘响应，用来移动鼠标……
    def keyPressEvent(self, QKeyEvent):
        x = QCursor.pos().x()
        y = QCursor.pos().y()
        if QKeyEvent.key() == Qt.Key_Up:
            QCursor.setPos(x,y-1)
        elif QKeyEvent.key() == Qt.Key_Down:
            QCursor.setPos(x, y+1)
        elif QKeyEvent.key() == Qt.Key_Left:
            QCursor.setPos(x-1, y)
        elif QKeyEvent.key() == Qt.Key_Right:
            QCursor.setPos(x+1, y)
        elif QKeyEvent.key() == Qt.Key_Shift:
            self.mainwindow.draw_region.roi.raise_()  # 虚线框置顶

    #改变鼠标的样式，一个是白圈，一个是中点虚圈
    def drawPen(self):
        pos = self.mapFromGlobal(QCursor.pos())  # 获得鼠标在当前控件的相对坐标，非常有用

        self.image_show = self.getQImageFromNpLabel(self.label_show)
        self.cursor_pos = pos
        x=pos.x()
        y=pos.y()
        # T = 100
        temp_painter = QPainter(self.image_show)
        if self.mainwindow.shape=='移动':
            self.setCursor(Qt.ClosedHandCursor)

        elif self.mainwindow.shape =='测距':
            temp_painter.setPen(QPen(QColor(255, 255, 255),1, Qt.SolidLine))  # 画笔颜色、粗细、样式
            temp_painter.drawLine(x-5,y,x+5,y)
            temp_painter.drawLine(x,y-5,x,y+5)

        elif self.mainwindow.shape == '区域生长':

            #通过不断绘制图像来改变图标样式，这样做会徒加功耗，我觉得使用qcursor好点
            temp_painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.DotLine)) #画笔颜色、粗细、样式
            r = self.mainwindow.pen_width
            temp_painter.drawEllipse(pos, r, r)  # 虚线外围圆
            temp_painter.setPen(QPen(QColor(255,255,255), 2, Qt.SolidLine))
            temp_painter.drawEllipse(pos, 1, 1)  # 实线中心点

            # if 0<x<=512 and 0<y<=512:
            #     if self.mainwindow.img[y,x] > T:
            #         temp_painter.setPen(QPen(QColor(0,0,0), 2, Qt.DotLine))
            #         r = self.mainwindow.pen_width
            #         temp_painter.drawEllipse(pos, r, r)  # 虚线外围圆
            #         temp_painter.setPen(QPen(QColor(0,0,0), 2, Qt.SolidLine))
            #         temp_painter.drawEllipse(pos, 1, 1)  # 实线中心点
            #     else:
            #         temp_painter.setPen(QPen(QColor(255,255,255), 2, Qt.DotLine))
            #         r = self.mainwindow.pen_width
            #         temp_painter.drawEllipse(pos, r, r)  # 虚线外围圆
            #         temp_painter.setPen(QPen(QColor(255,255,255), 2, Qt.SolidLine))
            #         temp_painter.drawEllipse(pos, 1, 1)  # 实线中心点
        else:
            temp_painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.SolidLine))  # 白色
            r = self.mainwindow.pen_width
            temp_painter.drawEllipse(pos, r, r)  # 实线圆
            # if 0<x<512 and 0<y<512:
            #     if self.mainwindow.img[y,x] > T:
            #         temp_painter.setPen(QPen(QColor(0,0,0), 2, Qt.SolidLine))  #黑色
            #         r = self.mainwindow.pen_width
            #         temp_painter.drawEllipse(pos, r, r)  # 实线圆
            #     else:
            #         temp_painter.setPen(QPen(QColor(255,255,255), 2, Qt.SolidLine))   #白色
            #         r = self.mainwindow.pen_width
            #         temp_painter.drawEllipse(pos, r, r)  # 实线圆

        temp_painter.end()
        self.update()

    def clearLabelMask(self):
        self.label_mask = np.zeros(self.label_mask.shape, dtype=np.uint8)
        self.json = [[] for i in range(50)]
        self.count = 0
        self.updateShow()

    # 更新画面
    def updateShow(self):
        self.label_show = self.label_mask.copy()
        self.image_show = self.getQImageFromNpLabel(self.label_show)
        self.drawPen()
        self.update()

    # 初始化展示状态,强制隔断直线喝方框的绘制
    def initShowStatue(self):
        self.line_statue = -1
        self.rect_start = False
        self.dir_statue=-1
        self.updateShow()

    # 清空展示状态`(相比前者，不paint画笔)，用于主界面的初始化
    def clearShowStatue(self):
        self.line_statue = -1
        self.rect_start = False
        self.label_show = self.label_mask.copy()
        self.image_show = self.getQImageFromNpLabel(self.label_show)
        # self.drawPen()
        self.update()

    def tempupdate(self):
        self.image_show = self.getQImageFromNpLabel(self.label_show)
        self.drawPen()
        self.update()



#创建新类——可移动方框事件
class RoiLabel(QLabel):
    import MainGUI
    def __init__(self, parent=None, mainwindow: MainGUI.MyMainWindow = None):
        super(RoiLabel, self).__init__((parent))
        self.mainwindow = mainwindow
        self.initUI()

    def initUI(self):
        self.x0=100  #左上角
        self.y0=100
        self.x1=250  #右下角
        self.y1=220
        self.begin=QPoint()
        self.end=QPoint()
        self.xx=self.x0
        self.yy=self.y0

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        painter=QPainter(self)
        painter.begin(self)
        painter.setPen(QPen(Qt.white, 2, Qt.DotLine))
        rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        painter.drawRect(rect)
        painter.end()

    # 鼠标左键点击事件
    def mousePressEvent(self, event):
        self.begin=event.pos()

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if (QApplication.keyboardModifiers() == Qt.ShiftModifier):   #shift键+移动键  拖动矩形移动
            self.end=event.pos()
            x=self.end.x()-self.begin.x()
            y=self.end.y()-self.begin.y()
            self.x0 = self.x0 + x
            self.y0 = self.y0 + y
            self.x1 = self.x1 + x
            self.y1 = self.y1 + y
            self.begin=self.end
            if self.mainwindow.meg_statue == True:
                x = self.mainwindow.draw_region.roi.x0
                y = self.mainwindow.draw_region.roi.y0
                self.xx=x
                self.yy=y

                rect = QRect(QPoint(x + 75 + 19, y + 60 - 10), QSize(150, 120))  # x+94-75,y+50-60
                self.getMegpic(rect)
            self.update()

    def getMegpic(self,rect):#暂时弃之不用
        self.mainwindow.draw_region.meg_image = QPixmap()
        self.mainwindow.draw_region.meg_image = self.mainwindow.draw_region.main_widget.grab(rect)
        width = self.mainwindow.draw_region.meg_image.width()
        height = self.mainwindow.draw_region.meg_image.height()
        meg = self.mainwindow.draw_region.meg_number  # 放大倍数
        self.mainwindow.draw_region.meg_image = self.mainwindow.draw_region.meg_image \
            .scaled(width * meg, height * meg, Qt.KeepAspectRatio)
        self.mainwindow.draw_region.meg_pic.setPixmap(self.mainwindow.draw_region.meg_image)
        self.update()



    #鼠标释放事件
    def mouseReleaseEvent(self, event):
        self.begin = QPoint()
        self.end = QPoint()
        if self.mainwindow.label_layers!=[]:             #如果图层大于1
            self.mainwindow.label_layers[self.mainwindow.current_label_index-1].raise_()

