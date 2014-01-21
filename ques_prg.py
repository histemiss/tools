# -*- coding:utf-8 -*- 

class Question_P(object):
    #格式化类型
    QUESTION_OUTPUT_SINGLE = 0
    QUESTION_OUTPUT_MULTI = 1
    QUESTION_OUTPUT_NUMBER = 2
    QUESTION_OUTPUT_LOOP_SINGLE = 3
    QUESTION_OUTPUT_LOOP_MULTI = 4
    QUESTION_OUTPUT_LOOP_NUMBER = 5
    QUESTION_OUTPUT_GRID_SINGLE = 6
    QUESTION_OUTPUT_GRID_MULTI = 7
    QUESTION_OUTPUT_GRID_NUMBER = 8
    QUESTION_OUTPUT_TOP2_NUMBER = 9
    QUESTION_OUTPUT_TOP2_MULTI = 10
    QUESTION_OUTPUT_TOP2_SINGLE = 11
    QUESTION_OUTPUT_MEAN_NUMBER = 12
    QUESTION_OUTPUT_MEAN_SINGLE = 13
    QUESTION_OUTPUT_MEAN_MULTI = 14

    feat_dict = {
        u'单选':[QUESTION_OUTPUT_SINGLE, QUESTION_OUTPUT_LOOP_SINGLE, QUESTION_OUTPUT_GRID_SINGLE, QUESTION_OUTPUT_TOP2_SINGLE, QUESTION_OUTPUT_MEAN_SINGLE], 
        u'多选':[QUESTION_OUTPUT_MULTI, QUESTION_OUTPUT_LOOP_MULTI, QUESTION_OUTPUT_GRID_MULTI, QUESTION_OUTPUT_TOP2_MULTI, QUESTION_OUTPUT_MEAN_MULTI], 
        u'数字':[QUESTION_OUTPUT_NUMBER, QUESTION_OUTPUT_LOOP_NUMBER, QUESTION_OUTPUT_GRID_NUMBER, QUESTION_OUTPUT_TOP2_NUMBER, QUESTION_OUTPUT_MEAN_NUMBER], 
        u'循环':[QUESTION_OUTPUT_LOOP_MULTI, QUESTION_OUTPUT_LOOP_SINGLE, QUESTION_OUTPUT_LOOP_NUMBER],
        'GRID':[QUESTION_OUTPUT_GRID_SINGLE, QUESTION_OUTPUT_GRID_MULTI, QUESTION_OUTPUT_GRID_NUMBER],
        'TOP2':[QUESTION_OUTPUT_TOP2_SINGLE, QUESTION_OUTPUT_TOP2_MULTI, QUESTION_OUTPUT_TOP2_NUMBER],
        'MEAN':[QUESTION_OUTPUT_MEAN_SINGLE, QUESTION_OUTPUT_MEAN_MULTI, QUESTION_OUTPUT_MEAN_NUMBER],
        }

    def is_loop(self):
        return isinstance(self, Question_P_Loop)

    def is_grid(self):
        return isinstance(self, Question_P_Grid)

    def is_top2(self):
        return isinstance(self, Question_P_Top2)

    def is_mean(self):
        return isinstance(self, Question_P_Mean)

    def features(self):
        #根据type计算属性
        o = []
        for i in Question_P.feat_dict:
            if self.type in Question_P.feat_dict[i]:
                o.append(i)
        return o

    def refresh_cond(self):
        #当更新问题的过滤条件之后使用
        #只有普通问题和循环才有, 而且外面需要过滤掉不使用的
        if not self.cond_prg :
            print(u"严重错误")
            raise
        self.update_cond(self)
        self.format()

    def update_cond(self):
        #直接重新构造头部
        self.init_head()

    #保存所有结果
    all_ques = []

    def __init__(self, q, t):
        #q是Question, t是类型
        self.q = q
        self.type = t
        
        #单独记录过滤条件, 直接操作这个变量
        self.cond_prg = None
        if not (self.is_grid() or self.is_top2() or self.is_mean()) and q.condition != None:
            self.cond_prg = q.condition.cond_prg
            
        #题目的轴名字, 包含'l'和题号Q_name, 可能包含条件
        self.l = ''
        #题目的描述, 题目表示, 'n23'开头, 使用long_name
        self.des = ''
        #题目的base, 索引ALIAS.QT文件
        self.base = ''

        #不同的题目使用不同的成员
        self.options = []

        #结尾空行, 固定值  'n03,nosort'
        self.n03 = ''
        #结尾, 固定值tots/totm
        self.tail = ''

        self.include = ''

        self.pub_fn = ''
        self.pub_lines = []

        #格式化之后的结果
        self.outputs = []

    #把公共使用的函数放在这里, 不一定每个问题都使用
    def init_head(self):
        #构造轴名字
        self.l = 'l ' + self.q.question.P_name
        if self.q.condition :
            self.l += ';c=' + self.cond_prg

        #构造题干描述
        self.desc = 'n23' + self.q.question.long_name

        #构造base命令, 统一构造
        #self.base = 'base1'

    def init_single_options(self):
        #初始化单选题的选项
        self.options = []
        for i in self.q.options:
            o = '+' + i.option_name + '=' + str(i.option_key)
            self.options.append(o)

    def init_multi_options(self):
        #初始化多选题的选项, pub文件中使用
        #选项行格式是: n01选项描述;c=ca开始偏移'1'
        self.options = []
        for i in self.q.options:
            o = 'n01' + i.option_name + ';c=ca' + str(i.option_key-1) + '\'1\''
            self.options.append(o)
        

class Question_P_Single(Question_P):
    def __init__(self, q):
        #用于单选题目

        super(Question_P_Single, self).__init__(q, Question_P.QUESTION_OUTPUT_SINGLE)
        super(Question_P_Single, self).init_head()

        #base后面
        #题目的数据位置
        #如果使用1位,  col 开始位置
        #如果使用多位, fld 开始位置:长度
        self.col = ''
        col_start = q.question.col.col_start
        col_width = q.question.col.col_width
        if col_width == 1:
            self.col = 'col ' + str(col_start)
        else:
            self.col = 'fld c' + str(col_start) + ':' + str(col_width)

        #题目的选项, +选项描述=选项值
        super(Question_P_Single, self).init_single_options()

        #结尾空行, 固定值  'n03,nosort'
        self.n03 = 'n03;nosort'
        #结尾, 固定值tots
        self.tail = 'tots'

    def format(self):
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.col)
        self.outputs += self.options
        self.outputs.append(self.n03)
        self.outputs.append(self.tail)

class Question_P_Multi(Question_P):
    def __init__(self, q):
        super(Question_P_Multi, self).__init__(q, Question_P.QUESTION_OUTPUT_MULTI)
        super(Question_P_Multi, self).init_head()
        
        #pub文件名
        self.pub_fn = q.question.P_name + '.pub'
        #include行, 包含pub文件名和数据起始位置
        #数据位置格式: ;col(a)=000
        self.include = '*include ' + self.pub_fn + ';col(a)=' + str(q.question.col.col_start)

        #没有尾部, 其他是pub的内容
        
        #题目的选项
        super(Question_P_Multi, self).init_multi_options()

        #结尾空行, 固定值  'n03;nosort'
        self.n03 = 'n03;nosort'
        #结尾, 固定值totm
        self.tail = 'totm'

    def format(self):
        #构造pub文件
        self.pub_lines = []
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)
        
        #构造axe文件的内容
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

class Question_P_Number(Question_P):
    def __init__(self, q):
        super(Question_P_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_NUMBER)

        #头部
        super(Question_P_Number, self).init_head()
        
        #构造val命令
        col_start = q.question.col.col_start 
        col_width = q.question.col.col_width
        self.val = ''
        if col_width == 1:
            self.val = 'val c(' + str(col_start) + ');0:9'
        else :
            self.val = 'val c(' + str(col_start) + ',' + str(col_start + col_width -1) + ');0:' + '9'*col_width

        #尾部
        self.n03 = 'n03;nosort'
        self.tail = 'tots'
        
    def format(self):
        #构造axe文件的内容
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.val)
        self.outputs.append(self.n03)
        self.outputs.append(self.tail)

class Question_P_Loop(Question_P):
    def __init__(self, q, t):
        #所有循环的父类
        super(Question_P_Loop, self).__init__(q, t)

    def init_loop_head(self):
        #pub文件名
        self.pub_fn = self.q.question.Q_name + '.pub'

        #初始化pub文件中的头部
        self.l = 'l &x'
        if self.q.condition:
            self.l += ';c=&b'
            #可能覆盖没条件的pub文件
            self.pub_fn = self.q.question.Q_name + '-c.pub'
        self.desc = 'n23&y'
        #self.base = 'base1'

    def init_include(self):
        #定义include命令
        self.include = '*include ' + self.pub_fn
        if self.q.condition:
            self.include += ';b=' + self.cond_prg
        self.include += ';col(a)=' + str(self.q.question.col.col_start)
        self.include += ';x=' + self.q.question.P_name
        self.include += ';y=' + self.q.question.long_name

    def update_cond(self):
        #对于循环的问题, 更新include
        self.init_include()

class Question_P_Loop_Single(Question_P_Loop):
    def __init__(self, q):
        #用于循环的单选题目
        super(Question_P_Loop_Single, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_SINGLE)

        #准备pub文件内容
        #pub文件头部
        super(Question_P_Loop_Single, self).init_loop_head()

        #col行
        self.col = ''
        col_width = q.question.col.col_width
        if col_width ==1:
            self.col = 'col a0'
        else:
            self.col = 'fld ca0:' + col_width

        #选项, 和在prg文件一样
        super(Question_P_Loop_Single, self).init_single_options()

        #尾部
        self.n03 = 'n03;nosort'
        self.tail = 'tots'

        #include命令
        super(Question_P_Loop_Single, self).init_include()

    def format(self):
        #构造pub文件
        self.pub_lines = []
        self.pub_lines.append(self.l)
        self.pub_lines.append(self.desc)
        self.pub_lines.append(self.base)
        self.pub_lines.append(self.col)
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #axe文件内容
        self.outputs = []
        self.outputs.append(self.include)

class Question_P_Loop_Multi(Question_P_Loop):
    def __init__(self, q):
        #用于循环的多选题目
        super(Question_P_Loop_Multi, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_MULTI)

        self.pub_fn = q.question.Q_name + '.pub'

        #准备pub文件内容
        #头部
        super(Question_P_Loop_Multi, self).init_loop_head()

        #选项
        super(Question_P_Loop_Multi, self).init_multi_options()

        #尾部
        self.n03 = 'n03;nosort'
        self.tail = 'totm'

        #只包括include文件
        super(Question_P_Loop_Multi, self).init_include()

    def format(self):
        #构造pub文件
        self.pub_lines = []
        self.pub_lines.append(self.l)
        self.pub_lines.append(self.desc)
        self.pub_lines.append(self.base)
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #axe轴文件
        self.outputs = []
        self.outputs.append(self.include)

class Question_P_Loop_Number(Question_P_Loop):
    def __init__(self, q):
        #用于循环的多选题目
        super(Question_P_Loop_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_NUMBER)

        self.pub_fn = q.question.Q_name + '.pub'

        #准备pub文件内容
        #头部
        super(Question_P_Loop_Number, self).init_loop_head()
        
        self.val = ''
        col_width = q.question.col.col_width
        if col_width == 1:
            self.val = 'val c(a0);0:9'
        else:
            self.val = 'val c(a0,a' + str(col_width-1) + ');0:' + '9' * col_width

        self.n03 = 'n03;nosort'
        self.tail = 'totm'

        #只包括include文件
        super(Question_P_Loop_Number, self).init_include()

    def format(self):
        #构造pub文件
        self.pub_lines = []
        self.pub_lines.append(self.l)
        self.pub_lines.append(self.desc)
        self.pub_lines.append(self.base)
        self.pub_lines.append(self.val)
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #axe轴文件, include命令
        self.outputs = []
        self.outputs.append(self.include)

class Question_P_Grid(Question_P):
    #所有的grid的类的父类
    def __init__(self, q, t):
        super(Question_P_Grid, self).__init__(q, t)

    def init_grid(self):
        self.l = 'l ' + self.q.question.Q_name + 'g'

        #xls文件中的列,而不是结果数据
        #获取循环的所有子问题
        qs = self.q.get_ques_q()
        self.cols = []
        for i in qs:
            o = 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start)
            self.cols.append(o)

        self.side = 'side'
        self.desc = 'n23' + self.q.question.Q_name + ' - GRID'
        #self.base = 'base1'

class Question_P_Grid_Number(Question_P_Grid):
    def __init__(self, q):
        super(Question_P_Grid_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_GRID_NUMBER)

        #初始化grid共同部分
        super(Question_P_Grid_Number, self).init_grid()

        #构造val
        col_width = q.question.col.col_width
        self.val = 'val c(a0);0:' + '9'*col_width
        
        self.n03 = 'n03,nosort'
        self.tail = 'tots'

    def format(self):
        #axe文件
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs += self.cols
        self.outputs.append(self.side)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)

        self.outputs.append(self.val)
        self.outputs.append(self.n03)
        self.outputs.append(self.tail)

class Question_P_Grid_Single(Question_P_Grid):
    def __init__(self, q):
        super(Question_P_Grid_Single, self).__init__(q, Question_P.QUESTION_OUTPUT_GRID_SINGLE)
        
        #头部使用Question_P_Grid的方法
        super(Question_P_Grid_Single, self).init_grid()

        self.col = 'col a0'
        #单选题的选项
        super(Question_P_Grid_Single, self).init_single_options()
        
        self.n03 = 'n03;nosort'
        self.tail = 'tots'

    def format(self):
        #
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs += self.cols
        self.outputs.append(self.side)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)

        self.outputs.append(self.col)
        self.outputs += self.options
        
        self.outputs.append(self.n03)
        self.outputs.append(self.tail)
        
class Question_P_Grid_Multi(Question_P_Grid):
    def __init__(self, q):
        super(Question_P_Grid_Multi, self).__init__(q, Question_P.QUESTION_OUTPUT_GRID_MULTI)
        
        #pub文件, 不带头部的
        self.pub_fn = q.question.Q_name + '-nohead.pub'
        super(Question_P_Grid_Multi, self).init_multi_options()
        self.n03 = 'n03;nosort'
        self.tail = 'totm'
        
        #头部使用Question_P_Grid的方法
        super(Question_P_Grid_Single, self).init_grid()
        #include命令
        self.include = '*include ' + self.pub_fn

    def format(self):
        #pub文件
        self.pub_lines = []
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #axe文件
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs += self.cols
        self.outputs.append(self.side)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

class Question_P_Top2(Question_P):
    #所有的top2的类的父类
    def __init__(self, q, t):
        super(Question_P_Top2, self).__init__(q, t)

    def format(self):
        
        

class Question_P_Mean(Question_P):
    #所有的top2的类的父类
    def __init__(self, q, t):
        super(Question_P_Mean, self).__init__(q, t)

