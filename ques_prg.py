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
    QUESTION_OUTPUT_TOP2 = 9
    QUESTION_OUTPUT_MEAN = 10
    
    ''' top2和mean题不分子类型
    QUESTION_OUTPUT_TOP2_NUMBER = 9
    QUESTION_OUTPUT_TOP2_MULTI = 10
    QUESTION_OUTPUT_TOP2_SINGLE = 11
    QUESTION_OUTPUT_MEAN_NUMBER = 12
    QUESTION_OUTPUT_MEAN_SINGLE = 13
    QUESTION_OUTPUT_MEAN_MULTI = 14
    '''

    feat_dict = {
        u'单选':[QUESTION_OUTPUT_SINGLE, QUESTION_OUTPUT_LOOP_SINGLE, QUESTION_OUTPUT_GRID_SINGLE], 
        u'多选':[QUESTION_OUTPUT_MULTI, QUESTION_OUTPUT_LOOP_MULTI, QUESTION_OUTPUT_GRID_MULTI],
        u'数值':[QUESTION_OUTPUT_NUMBER, QUESTION_OUTPUT_LOOP_NUMBER, QUESTION_OUTPUT_GRID_NUMBER],
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
        if self.is_loop():
            o.append(u'循环')
        if self.is_grid():
            o.append(u'GRID')
        if self.is_top2():
            o.append(u'TOP2')
        if self.is_mean():
            o.append(u'MEAN')
        
        for i in Question_P.feat_dict:
            if self.type in Question_P.feat_dict[i]:
                o.append(i)
        return o

    def refresh_cond(self):
        #当更新问题的过滤条件之后使用
        self.update_cond()
        self.format()

    def update_cond(self):
        #构造轴名字中的过滤条件
        self.l = 'l ' + self.q.question.P_name
        if len(self.cond_prg) > 0:
            self.l += ';c=' + self.cond_prg
        self.init_head()

    def update_pub(self):
        #修改pub文件后，更新axe文件
        pass

    def __init__(self, q, t):
        #q是Question, t是类型
        self.q = q
        self.type = t
        
        #单独记录过滤条件, 直接操作这个变量
        #所有题目都可能添加条件
        self.cond_prg = ''
        if q.condition != None:
            self.cond_prg = q.condition.cond_prg
            
        #题目的轴名字, 包含'l'和题号Q_name, 可能包含条件
        self.l = ''
        #题目的描述, 题目表示, 'n23'开头, 使用long_name
        self.desc = ''
        #题目的base, 索引ALIAS.QT文件
        #base更新后，重新调用format即可
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
        if len(self.cond_prg) > 0:
            self.l += ';c=' + self.cond_prg

        #构造题干描述
        self.desc = 'n23' + self.q.question.long_name

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

    def create_axe(self):
        #构造axe文件内容
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

    def update_pub(self):
        #修改axe文件中的描述
        self.include = '*include ' + self.pub_fn + ';col(a)=' + str(self.q.question.col.col_start)
        #重新构造axe文件
        self.create_axe()

    def format(self):
        #构造pub文件
        self.pub_lines = []
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #构造axe文件的内容
        self.create_axe()

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
        
        #反向关联题目
        q.qp = self

    def init_loop_head(self):
        #pub文件名
        self.pub_fn = self.q.question.Q_name + '.pub'

        #初始化pub文件中的头部
        self.l = 'l &x'
        if len(self.cond_prg) > 0:
            self.l += ';c=&b'
            #可能覆盖没条件的pub文件
            self.pub_fn = self.q.question.Q_name + '_c.pub'
        self.desc = 'n23&y'

    def init_include(self):
        #定义include命令
        self.include = '*include ' + self.pub_fn
        if len(self.cond_prg) > 0:
            self.include += ';b=' + self.cond_prg
        self.include += ';col(a)=' + str(self.q.question.col.col_start)
        self.include += ';x=' + self.q.question.P_name
        self.include += ';y=' + self.q.question.long_name

    def create_axe(self):
        #构造axe文件内容，只有inlucde
        self.outputs = []
        self.outputs.append(self.include)

    def update_cond(self):
        #更新pub文件中的描述中的过滤条件
        self.l = 'l &x'
        if len(self.cond_prg) > 0:
            self.l += ';c=&b'

        #对于循环的问题, 更新include
        self.init_include()
        
        #更新对应的grid,top2,mean题目
        self.grid.refresh_cond()
        self.top2.refresh_cond()
        self.mean.refresh_cond()

    def update_pub(self):
        #更新include内容
        self.init_include()
        #重新构造axe中的内容
        self.create_axe()

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
            self.col = 'fld ca0:' + str(col_width)

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
        self.create_axe()

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
        self.create_axe()

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
        self.tail = 'tots'

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

        #axe轴文件
        self.create_axe()

class Question_P_Grid(Question_P):
    #所有的grid的类的父类
    def __init__(self, q, t):
        super(Question_P_Grid, self).__init__(q, t)
        #过滤条件为空, 不会依托子问题过滤条件
        self.cond_prg = ''
        
        #循环的子问题关联grid题目, 更新子问题过滤条件时，更新对应的grid题目
        qs = self.q.get_ques_q()
        for q in qs:
            q.qp.grid = self

    def init_grid(self):
        self.l = 'l ' + self.q.question.Q_name + 'g'
        if len(self.cond_prg) > 0:
            self.l += ';c=' + self.cond_prg

        #xls文件中的列,而不是结果数据
        #获取循环的所有子问题
        qs = self.q.get_ques_q()
        self.cols = []
        for i in qs:
            if len(i.qp.cond_prg) > 0:
                o = 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start) + ";c=" + i.qp.cond_prg
            else:
                o = 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start)
            self.cols.append(o)

        self.side = 'side'
        self.desc = 'n23' + self.q.question.Q_name + ' - GRID'

    def update_cond(self):
        #更新grid的描述和子问题的判断条件
        self.init_grid()

class Question_P_Grid_Number(Question_P_Grid):
    def __init__(self, q):
        super(Question_P_Grid_Number, self).__init__(q, Question_P.QUESTION_OUTPUT_GRID_NUMBER)

        #初始化grid共同部分
        super(Question_P_Grid_Number, self).init_grid()

        #构造val
        col_width = q.question.col.col_width
        if col_width == 1:
            self.val='val c(a0);0:9'
        else:
            self.val = 'val c(a0,'+str(col_width-1)+');0:' + '9'*col_width
      
        self.n03 = 'n03;nosort'
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
        self.pub_fn = q.question.Q_name + 'n.pub'
        super(Question_P_Grid_Multi, self).init_multi_options()
        self.n03 = 'n03;nosort'
        self.tail = 'totm'
        
        #头部使用Question_P_Grid的方法
        super(Question_P_Grid_Multi, self).init_grid()
        #include命令
        self.include = '*include ' + self.pub_fn

    def create_axe(self):
        self.outputs = []
        self.outputs.append(self.l)
        self.outputs += self.cols
        self.outputs.append(self.side)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        self.outputs.append(self.include)

    def format(self):
        #pub文件
        self.pub_lines = []
        self.pub_lines += self.options
        self.pub_lines.append(self.n03)
        self.pub_lines.append(self.tail)

        #axe文件
        self.create_axe()

    def update_pub(self):
        #更新include行
        self.include = '*include ' + self.pub_fn
        #更新axe文件内容
        self.create_axe()

class Question_P_Top2(Question_P):
    #top2问题不再区分子类型
    def __init__(self, q):
        super(Question_P_Top2, self).__init__(q, Question_P.QUESTION_OUTPUT_TOP2)
        #默认过滤条件为空
        self.cond_prg = ''

        #子问题反向影射top2问题
        qs = self.q.get_ques_q()
        for q in qs:
            q.qp.top2 = self

        self.init_top2()

        #描述文件
        self.desc = 'n23' + self.q.question.Q_name + '.TOP2'
        #不使用pub文件
        self.pub_fn = ''
        
    def init_top2(self):
        self.l = 'l ' + self.q.question.Q_name + 't'
        if len(self.cond_prg) > 0:
            self.l += ';c=' + self.cond_prg

        #base后面的子问题行
        self.cols = []
        qs = self.q.get_ques_q()
        for i in qs:
            col = i.question.col.col_start
            if len(i.qp.cond_prg) > 0:
                o = '*include top2c.pub;col(a)=' + str(col) + ';y=' + i.question.long_name + ';b=' + i.qp.cond_prg
            else:
                o = '*include top2.pub;col(a)=' + str(col) + ';y=' + i.question.long_name
            self.cols.append(o)

    def format(self):
        #所有的top2问题使用一套pub文件
        '''
        self.pub_fn = 'top2.pub'
        self.pub_lines =[ "n01&y;c=ca0'45'",]
        self.pub_fn = 'top2c.pub'
        self.pub_lines =[ 
            "n00;c=&b",
            "n01&y;c=ca0'45'",]
        '''

        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        for o in self.cols:
            self.outputs.append(o)

    def update_cond(self):
        #更新axe文件中的描述和子问题描述
        self.init_top2()
        
class Question_P_Mean(Question_P):
    def __init__(self, q):
        super(Question_P_Mean, self).__init__(q, Question_P.QUESTION_OUTPUT_MEAN)
        #默认过滤条件为空
        self.cond_prg = ''

        #子问题反向影射mean题目
        qs = self.q.get_ques_q()
        for q in qs:
            q.qp.mean = self

        self.init_mean()

        #题目描述和pub文件名不会改变
        self.desc = 'n23' + self.q.question.Q_name + '.MEAN'
        self.pub_fn = ''

    def init_mean(self):
        self.l = 'l ' + self.q.question.Q_name + 'm'
        if len(self.cond_prg) > 0:
            self.l += ';c=' + self.cond_prg

        #base后面的子问题选项行
        self.cols = []
        qs = self.q.get_ques_q()
        for i in qs:
            col = i.question.col.col_start
            if len(i.qp.cond_prg) > 0:
                o = '*include meanc.pub;col(a)=' + str(col) + ';y=' + i.question.long_name + ';b=' + i.qp.cond_prg
            else:
                o = '*include mean.pub;col(a)=' + str(col) + ';y=' + i.question.long_name
            self.cols.append(o)


    def update_cond(self):
        self.init_mean()

    def format(self):
        #使用相同的一套, mean.pub, meanc.pub
        '''
        self.pub_fn = 'mean.pub'
        self.pub_lines =[ 
            "n25;inc=ca0", 
            "n12&y;dec=2"]
        self.pub_fn = 'meanc.pub'
        self.pub_lines =[ 
            "n00;c=&b",
            "n25;inc=ca0", 
            "n12&y;dec=2"]
        '''

        self.outputs = []
        self.outputs.append(self.l)
        self.outputs.append(self.desc)
        self.outputs.append(self.base)
        for o in self.cols:
            self.outputs.append(o)
        
