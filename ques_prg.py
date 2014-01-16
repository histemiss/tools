# -*- coding:utf-8 -*- 

from ques import write_lines

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
    QUESTINO_OUTPUT_TOP2_NUMBER = 9
    QUESTINO_OUTPUT_TOP2_MULTI = 10
    QUESTINO_OUTPUT_TOP2_SINGLE = 11
    QUESTION_OUTPUT_MEAN_NUMBER = 12
    QUESTION_OUTPUT_MEAN_SINGLE = 13
    QUESTION_OUTPUT_MEAN_MULTI = 14

    #保存所有结果
    all_ques = []

    def __init__(self, q, t):
        #q是Question, t是类型
        self.q = q
        self.type = t

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

        self.pub_fn = ''
        self.include = ''

        #格式化之后的结果
        self.outputs = []

    #把公共使用的函数放在这里, 不一定每个问题都使用
    def init_head(self):
        #构造轴名字
        self.l = 'l ' + self.q.question.P_name
        if self.q.condition :
            self.l += self.q.condition.output

        #构造题干描述
        self.desc = 'n23' + self.q.question.long_name

        #构造base命令
        self.base = 'base1'

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
        lines = []
        lines += self.options
        lines.append(self.n03)
        lines.append(self.tail)
        write_lines(self.pub_fn, lines)
        
        #构造axe文件的内容
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

class Question_P_Number(Question_P):
    def __init__(self, q):
        super(Question_P_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_NUMBER)
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

class Question_P_Loop_Single(Question_P):
    def __init__(self, q):
        #用于循环的单选题目
        super(Question_P_Loop_Single, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_SINGLE)

        self.pub_fn = q.question.Q_name + '.pub'

        #准备pub文件内容
        self.l = 'l &x'
        if q.condition:
            self.l += ';c=&b'
            #可能覆盖没条件的pub文件
            self.pub_fn = q.question.Q_name + '-c.pub'
        self.desc = 'n23&y'
        self.base = 'base1'

        self.col = ''
        col_width = q.question.col.col_width
        if col_width ==1:
            self.col = 'col a0'
        else:
            self.col = 'fld ca0:' + col_wdith

        #选项
        super(Question_P_Loop_Single, self).init_single_options()
        #print('test', self.options)
        
        self.n03 = 'n03;nosort'
        self.tail = 'tots'

        #include命令
        self.include = '*include ' + self.pub_fn
        if q.condition:
            self.include += ';b=' + q.question.condition.output
        self.include += ';col(a)=' + str(q.question.col.col_start)
        self.include += ';x=' + q.question.P_name
        self.include += ';y=' + q.question.long_name

    def format(self):
        #构造pub文件
        lines = []
        lines.append(self.l)
        lines.append(self.desc)
        lines.append(self.base)
        lines.append(self.col)
        lines += self.options
        lines.append(self.n03)
        lines.append(self.tail)

        write_lines(self.pub_fn, lines)

        #axe文件内容
        self.outputs = []
        self.outputs.append(self.include)

class Question_P_Loop_Multi(Question_P):
    def __init__(self, q):
        #用于循环的多选题目
        super(Question_P_Loop_Multi, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_MULTI)

        self.pub_fn = q.question.Q_name + '.pub'

        #准备pub文件内容
        self.l = 'l &x'
        if q.condition:
            self.l += ';c=&b'
            #可能覆盖没条件的pub文件
            self.pub_fn = q.question.Q_name + '-c.pub'
        self.desc = 'n23&y'
        self.base = 'base1'

        #选项
        super(Question_P_Loop_Multi, self).init_multi_options()

        self.n03 = 'n03;nosort'
        self.tail = 'totm'

        #只包括include文件
        self.include = '*include ' + self.pub_fn
        if q.condition:
            self.include += ';b=' + q.question.condition.output
        self.include += ';col(a)=' + str(q.question.col.col_start)
        self.include += ';x=' + q.question.P_name
        self.include += ';y=' + q.question.long_name

    def format(self):
        #构造pub文件
        lines = []
        lines.append(self.l)
        lines.append(self.desc)
        lines.append(self.base)
        lines += self.options
        lines.append(self.n03)
        lines.append(self.tail)

        write_lines(self.pub_fn, lines)

        #axe轴文件
        self.outputs = []
        self.outputs.append(self.include)

class Question_P_Loop_Number(Question_P):
    def __init__(self, q):
        #用于循环的多选题目
        super(Question_P_Loop_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_LOOP_NUMBER)

        self.pub_fn = q.question.Q_name + '.pub'

        #准备pub文件内容
        self.l = 'l &x'
        if q.condition:
            self.l += ';c=&b'
            #可能覆盖没条件的pub文件
            self.pub_fn = q.question.Q_name + '-c.pub'
        self.desc = 'n23&y'
        self.base = 'base1'

        self.val = ''
        col_width = q.question.col.col_width
        if col_width == 1:
            self.val = 'val c(a0);0:9'
        else:
            self.val = 'val c(a0,a' + str(col_width-1) + ');0:' + '9' * col_width

        self.n03 = 'n03;nosort'
        self.tail = 'totm'

        #只包括include文件
        self.include = '*include ' + self.pub_fn
        if q.condition:
            self.include += ';b=' + q.question.condition.output
        self.include += ';col(a)=' + str(q.question.col.col_start)
        self.include += ';x=' + q.question.P_name
        self.include += ';y=' + q.question.long_name

    def format(self):
        #构造pub文件
        lines = []
        lines.append(self.l)
        lines.append(self.desc)
        lines.append(self.base)
        lines.append(self.val)
        lines.append(self.n03)
        lines.append(self.tail)

        write_lines(self.pub_fn, lines)

        #axe轴文件
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
        qs = self.q.Q_ques_dict[self.q.question.Q_name]
        self.cols = []
        for i in qs:
            o = 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start)
            self.cols.append(o)

        self.side = 'side'
        self.desc = 'n23' + self.q.question.Q_name + ' - GRID'
        self.base = 'base1'

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
        lines = []
        lines += self.options
        lines.append(self.n03)
        lines.append(self.tail)
        write_lines(self.pub_fn, lines)

        #axe文件
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs += self.cols
        self.outputs.append(self.side)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

