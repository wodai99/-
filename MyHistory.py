# 历史的类型属于常量字符串，形式为 第一数字-第二数字
# 如果第一数字相同那么做的撤回和恢复的处理相同，无需重复写方法
# 第二数字表示旗下不同类型，在历史列表中显示的信息不一样

# 文件打开
OPEN_FILE = '0'
# 图层创建
CREATE_LAYER = '1'
# 改变label_mask
CHANGE_LABEL_MASK = '2'
CLEAR_CURRENT_LABEL_MASK = '2-0'
DRAW = '2-1'
CNN_PREDICTION = '2-2'
GRABCUT = '2-3'
THRESHOLD_SEG = '2-4'
EROSION = '2-5'
LOADJSON='2-6'
# 图层切换
CHANGE_LAYER = '3'  # 暂时废弃
# 删除最后一层
DELETE_LAST_LAYER = '4'
# 改变图层可视化
CHANGE_LAYER_VISIABLE = '5'


class History:
    def __init__(self, type_, **kwargs):
        self.history_index = 0  # 自身所属索引
        self.type_ = type_  # 类型
        self.context = kwargs  # 内容
        self.show_info = self.getShowInfo()  # 输出在历史列表展示的信息

    # 撤销时，进行处理
    def undo(self):
        # 打开文件
        if self.type_ == OPEN_FILE or self.type_[0] == OPEN_FILE:
            pass
        # 创建图层
        elif self.type_ == CREATE_LAYER or self.type_[0] == CREATE_LAYER:
            self.context['mainwindow'].layer_region.deleteLastLayer(not_history=True)  # 删除最后一个图层（不生成历史记录）
        # 改变label_mask
        elif self.type_ == CHANGE_LABEL_MASK or self.type_[0] == CHANGE_LABEL_MASK:
            last_label,json_count,json = self.getLastLabelMask() # 获得上一次的label_mask
            last_label_mask=last_label.copy()
            self.setLabelMask(last_label_mask,json_count,json)  # 将其载入
        # 切换图层
        # elif self.type_ == CHANGE_LAYER or int(self.type_[0]) == CHANGE_LAYER:
        #     self.context['mainwindow'].layer_region.layerSelected(self.context['before_layer_index'] - 1, None,
        #                                                           is_history=True)
        # 删除最后一层图层
        elif self.type_ == DELETE_LAST_LAYER or self.type_[0] == DELETE_LAST_LAYER:
            self.context['mainwindow'].layer_region.newLabel(not_history=True)  # 创建新的图层（不生成历史记录）
            last_label_mask = self.getLastLabelMask().copy()  # 载入当前的历史保存的label_Mask
            self.setLabelMask(last_label_mask)
        # 改变图层可视化
        elif self.type_ == CHANGE_LAYER_VISIABLE or self.type_[0] == CHANGE_LAYER_VISIABLE:
            self.context['mainwindow'].layer_region.setLayerVisible(
                layer_index=self.context['layer_index'], visible=not self.context['visible'])  # 恢复原可视化状态

    # 恢复时，做的处理
    def redo(self):
        # 打开文件
        if self.type_ == OPEN_FILE or self.type_[0] == OPEN_FILE:
            pass
        # 创建图层
        elif self.type_ == CREATE_LAYER or self.type_[0] == CREATE_LAYER:
            self.context['mainwindow'].layer_region.newLabel(not_history=True)
        # 改变label_mask
        elif self.type_ == CHANGE_LABEL_MASK or self.type_[0] == CHANGE_LABEL_MASK:
            self.setLabelMask()
        # 切换图层
        # elif self.type_ == CHANGE_LAYER:
        #     self.context['mainwindow'].layer_region.layerSelected(self.context['layer_index'] - 1, None,
        #                                                           is_history=True)
        # 删除图层
        elif self.type_ == DELETE_LAST_LAYER or self.type_[0] == DELETE_LAST_LAYER:
            self.context['mainwindow'].layer_region.deleteLastLayer(not_history=True)
        # 改变图层可视化
        elif self.type_ == CHANGE_LAYER_VISIABLE or self.type_[0] == CHANGE_LAYER_VISIABLE:
            self.context['mainwindow'].layer_region.setLayerVisible(
                layer_index=self.context['layer_index'], visible=self.context['visible'])

    # 不同类型的历史显示不同信息
    def getShowInfo(self):
        if self.type_ == OPEN_FILE:
            return ['打开文件', '']
        elif self.type_ == CREATE_LAYER:
            return ['新建图层'.format(self.context['pen_shape']), '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == CLEAR_CURRENT_LABEL_MASK:
            return ['Clear', '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == DRAW:
            return ['画 {}'.format(self.context['pen_shape']), '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == CNN_PREDICTION:
            return ['模型预测', '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == GRABCUT:
            return ['图论分割', '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == THRESHOLD_SEG:
            return ['阈值分割', '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == EROSION:
            return ['消除边缘', '标签{}'.format(self.context['layer_index'])]
        # elif self.type_ == CHANGE_LAYER:
        #     return ['Change Layer', '{}->{}'.format(self.context['before_layer_index'], self.context['layer_index'])]
        elif self.type_ == DELETE_LAST_LAYER:
            return ['删除最后一层', '标签{}'.format(self.context['layer_index'])]
        elif self.type_ == CHANGE_LAYER_VISIABLE:
            if self.context['visible']:
                return ['图层可见', '标签{}'.format(self.context['layer_index'])]
            else:
                return ['图层不可见', '标签{}'.format(self.context['layer_index'])]
        elif self.type_==LOADJSON:
            return ['加载Json文件', '标签{}'.format(self.context['layer_index'])]

    # 获得上一个的Label_mask,矩形信息
    def getLastLabelMask(self):
        i = self.history_index
        while (True):
            i -= 1
            last_history_context = self.context['mainwindow'].history_list[i - 1].context
            if 'layer_index' in last_history_context and 'label_mask' in last_history_context:
                if last_history_context['layer_index'] == self.context['layer_index']:
                    try:
                        return (last_history_context['label_mask'],last_history_context['count'],last_history_context['json'])
                    except:
                        count=0
                        json=[[] for i in range(50)]
                        return(last_history_context['label_mask'],count,json)


    # 对历史中指定索引的MyLabel，载入label_mask，矩形信息
    def setLabelMask(self, label_mask=None,json_count=None,json=None):
        layer = self.context['mainwindow'].label_layers[self.context['layer_index'] - 1]
        layer.label_mask = self.context['label_mask'].copy() if label_mask is None else label_mask
        layer.count=json_count if json_count is None else json_count
        layer.json = json if json is None else json
        self.context['mainwindow'].layer_region.layerSelected(self.context['layer_index'] - 1, None)
        layer.initShowStatue()
