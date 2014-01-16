#!/usr/bin/python
# -*- coding:utf-8 -*- 

import re
import os
import sys

from ques_prg import *

#global control variable
#命令行第一个字符为空格,现在没有使用
option_black = False

#回车变量
CRLF = '\n'

#输出文件夹
output_dir = '.'


#辅助函数

#读打开文件，不需要转义回车
def write_open(fn):
    f = open(fn, 'w')
    return f

def read_open(fn):
    f = open(fn, 'r')
    return f

def write_lines(fn, lines):
    f = open(output_dir + '/' + fn, 'w')
    f.write((CRLF.join(lines)).encode('gbk'))
    f.write(CRLF.encode('gbk'))
    f.close()

class Token(object) :
    #*SNG
    TOKEN_SINGLE = 0
    #*MV
    TOKEN_MULTI = 1
    #col, 12L1
    TOKEN_COL = 2
    #FI
    TOKEN_FI = 3
    #忽略的单词
    #*INTRN, *TEK, *INTTIME
    TOKEN_SPECIAL = 4
    #问题编号, 字母后面跟着数字和字母
    TOKEN_QUESTION = 5
    #numbers
    TOKEN_NUMBER = 6
    
    #没有意义的字符串
    TOKEN_BLACK = 10
    #无法识别,需要报错
    TOKEN_UNKNOWN = 11
    
    #token regexp used to match 
    token_str = {
        TOKEN_SINGLE: '\*SNG',
        TOKEN_MULTI: '\*MV', 
        TOKEN_COL: '[\d]+L[\d]+',
        TOKEN_FI:'FI',
        TOKEN_SPECIAL: '\*((INTNR)|(INTTIME)|(SCRCNT)|(INTERNR)|(STIME))',
        TOKEN_QUESTION: '\*[a-zA-Z][a-zA-Z0-9_-]*', 
        TOKEN_NUMBER: '\d+',
    }

    token_type_names = {
        TOKEN_SINGLE: 'SNG',
        TOKEN_MULTI: 'MV', 
        TOKEN_COL: 'COL',
        TOKEN_FI:'FI',
        TOKEN_SPECIAL: 'SPECIAL',
        TOKEN_QUESTION: 'QUESTION', 
        TOKEN_NUMBER: 'NUMBER',
        TOKEN_BLACK: 'BLACK',
    }
    
    def __init__(self, s='', start=-1,len=-1, type = TOKEN_UNKNOWN) :
        self.sentense = None
        self.start = start
        self.len = len
        self.string = s
        self.type = type
        #print("parse " + str(self.string))

    def __str__(self):
        return ("%s \t->%s" % (Token.token_type_names[self.type], self.str))

class Token_Col(Token):
    def __init__(self, s='', start =-1, len =-1):
        super(Token_Col, self).__init__(s, start, len, Token.TOKEN_COL)
        self.col_start = int(self.string.split('L')[0])
        self.col_width = int(self.string.split('L')[1])

def token_parse(s, pos, len):
    if not s :
        return None

    #trim blacks before and after
    r = re.compile('(\A\s*)|(\s*\Z)')
    s = r.sub('', s)
    for i in Token.token_str :
        r = re.compile('\A' + Token.token_str[i] + '\Z')
        if r.match(s) :
            if i == Token.TOKEN_COL:
                return Token_Col(s, pos, len)
            return Token(s, pos, len, i)
    print(u"无法解析 %s" % s)
    raise None

class Sentense(object):
    #每个题目的第一行
    SENTENSE_QUESTION = 0
    #题目第2行,可能不存在
    SENTENSE_CONDITION = 1
    #题目的选项
    SENTENSE_OPTION = 2
    
    #忽略的行
    SENTENSE_BLACK = 10
    #错误
    SENTENSE_UNKNOWN = 11
    
    sentense_type_names = {
        SENTENSE_QUESTION: "QUESTION",
        SENTENSE_CONDITION: "CONDITION",
        SENTENSE_OPTION: "OPTION",
        SENTENSE_BLACK: "BLACK"
    }
    
    def __init__(self, ts = [], s = '', l = -1, t = SENTENSE_BLACK):
        self.ques = None
        self.tokens = ts
        self.line = l
        self.string = s
        self.type = t

    def __str__(self):
        return "\n" + Sentense.sentense_type_names[self.type] + '\t->\n' + '\n'.join([str(i) for i in self.tokens])

class Sentense_cond(Sentense):
    def __init__(self, ts = [], s = '', l = -1):
        super(Sentense_cond, self).__init__(ts, s, l, Sentense.SENTENSE_CONDITION)
        self.output = None

    def cond_ques_expr(self, c):
        #使用题号的判断表达式: 'V2130,1'  前面可能带有#, 后面可能带有多个','
        #去掉头尾的空格
        r = re.compile(r'(\A\s*)|(\s*\Z)')
        c = r.sub('', c)
        
        #结果是output
        output = ''

        #开头是否有'#'
        r_not = False
        if c[0] == '#':
            r_not = True
            c = c[1:]

        #使用','分割, 第一个是题号
        #对于单选题后面是题目的结果, 可能包含多个选项, 过滤条件是选择其中之一的选项的, 使用'or'连接
        #对于多选题后面是子题目的题号, 需要减一, 过滤条件是同时选择这些选项的, 使用'and'连接
        vs = c.split(',')
        q = vs[0]
        vs = vs[1:]
        
        #查找q对应的题目
        q = Question.ques_dict[q]
        if not q:
            print("找不到判断条件的题号", c)
            raise None
        col_start = q.question.col.col_start
        col_width = q.question.col.col_width

        #如果是多选, 找出子问题
        if q.question.type_ques == Sentense_ques.QUESTION_MULTI:
            #如果多个子问题, 使用'and'连起来
            #题号后面有多个子题号, 使用逗号连起来
            #Q,2,4 -> c01'1'.and.c03'1'
            # #Q,2,4 -> not.(c01'1'.and.c03'1')
            #如果是否定, 前面使用not.表示否定
            if len(vs) > 1:
                o_out = []
                for i in vs:
                    i_start = col_start + int(i) -1
                    i_out = 'c' + str(col_start) + '.\'1\''
                    o_out.append(i_out)
                output = '.and.'.join(o_out)
                if r_not:
                    output = 'not.(' + output + ')'
                return output
            
            #如果只有一个子题号, 像单选题一样处理
            col_start += int(vs[0]) - 1
            col_width = 1
            vs = ['1',]

        #单选题
        if col_width == 1:
            #如果题目的结果使用1位, 使用简化的方式
            #如果Q是单选  Q,3 -> c0'3'
            #如果Q是多选  Q,3 -> c02'1'
            #如果是否定, 使用n  c0n'3'
            n_output = 'n' if r_not else ''
            output = 'c' + str(col_start) + n_output + '\'' + ''.join(vs) + '\''
        else:
            #如果题目结果使用多位, 使用'eq'/'ne'的方式
            if len(vs) == 1:
                #只有一个选项,使用'eq'或者'ne'
                #Q,12 -> c0.eq.12
                #如果是否定, 使用ne
                eq_outp = 'ne' if r_not else 'eq'
                output = 'c(' + str(col_start) + ',' + str(col_start + col_width -1) + ').' + eq_outp + '.' + vs[0]
            else:
                #多个值,使用'in'
                #Q,10,20,99 -> c0.in.(10,20,99) 
                #如果是否定, 千米使用not表示否定
                output = 'c(' + str(col_start) + ',' + str(col_start + col_width -1) + ').in(' + ','.join(vs) + ')'
                if r_not:
                    output = 'not.' + output

        return output

    def cond_col_expr(self, c):
        #去掉头尾的空格
        r = re.compile('(\A\s*)|(\s*\Z)')
        c = r.sub('', c)

        #匹配题目结构位置
        r = re.compile('[1-9][0-9]*L[1-9][0-9]*')
        r1 = r.search(c)
        r1 = c[r1.start():r1.end()]
        p = r1.split('L')
        col_start = int(p[0])
        col_width = int(p[1])

        #匹配表达式的值
        r = re.compile('[0-9]+\s*\Z')
        r1 = r.search(c)
        val = c[r1.start():r1.end()]

        #查找判断表达式
        s = ''
        if c.find('<>') != -1:
            s = 'ne'
        elif c.find('>=') != -1:
            s = 'ge'
        elif c.find('<=') != -1:
            s = 'le'
        elif c.find('>') != -1:
            s = 'gt'
        elif c.find('<') != -1:
            s = 'lt'
        elif c.find('=') != -1:
            s = 'eq'
        else :
            print("没有找到比较运算符", c)
            raise None
            
        output = ''
        if col_width == 1 :
            if s == 'eq' or s == 'ne':
                #只简化这种情况
                s_op = '' if s == 'eq' else 'n'
                output = 'c' + str(col_start) + s_op + '\'' + val + '\''
            else :
                output = 'c(' + str(col_start) + ').' + s + '.' + val
        else :
            output = 'c(' + str(col_start) + ',' + str(col_start + col_width-1) + ').' + s + '.' + val

        return output
        
    def cond_parse(self, c):
        #使用题号作为过滤条件
        r_ques = re.compile(r'\A\s*#?[a-zA-Z][a-zA-Z0-9_-]*(,[0-9]+)+\s*(\\|&\s*#?[a-zA-Z][a-zA-Z0-9-_]*(,[0-9]+)+\s*)*\Z')

        #使用数据位置作为过滤条件
        r_col = re.compile(r'\A\s*[1-9][0-9]*L[0-9]+\s*(=)|(<>)|(<)|(>)|(>=)|(<=)\s*[0-9]+\s(\\|&\s*[1-9][0-9]*L[0-9]+\s*(=)|(<>)|(<)|(>)|(>=)|(<=)\s*[0-9]+)*\Z')

        f = None
        
        if f == None and r_ques.match(c):
            f = self.cond_ques_expr
        elif f == None and r_col.match(c):
            f = self.cond_col_expr

        #使用'\'和'&'分割, 使用'or', 'and'连起来
        o_conds = c.split('\\')
        o_out = []
        for o in o_conds:
            a_conds = o.split('&')
            a_out = []
            for a in a_conds:
                a_out.append(f(a))
            o_out.append('.and.'.join(a_out))
        return '.or.'.join(o_out)
            
    def parse_condition(self):
        #FI ( XXXX ) :
        #先分离':'前面的条件
        cond_str = self.string.split(':')[0]
        #先解析括号里面的内容
        r = re.compile('(\AFI\s+\(\s+)|(\s+\)\s+)')
        cond_str = r.sub('', cond_str)

        o = self.cond_parse(cond_str)

        if o == None:
            print('条件解析错误:', self.string)
            raise None
        
        self.output = ';c=' + o


#这一行是题目,解析
class Sentense_ques(Sentense):
    QUESTION_SINGLE = 0
    QUESTION_MULTI = 1
    QUESTION_FORM = 2
    #其他题作为number题
    QUESTION_NUMBER = 3
    #忽略的问题
    QUESTION_OTHER = 10

    question_type_names = {
        QUESTION_SINGLE:'SINGLE',
        QUESTION_MULTI:'MULTI',
        QUESTION_FORM:'FORM',
        QUESTION_NUMBER:"NUMBER",
        QUESTION_OTHER:'OTHER'
    }

    def __init__(self, ts = [], s = '', l = 0):
        super(Sentense_ques, self).__init__(ts, s, l, Sentense.SENTENSE_QUESTION)

        #先去掉2端的空格
        r = re.compile('(\A\s*)|(\s*\Z)|(\')')

        #解析var文件中的名字, 第一个token
        self.V_name = r.sub('', self.tokens[0].string)
        if self.V_name[0] != '*':
            print("VAR名字必须以'*'开头")
            raise None
        #去掉'*'
        self.V_name = self.V_name[1:]

        #解析':'后面的字符串,也就是问题主干, 也就是最后一个token
        #一般是 英文词号.中文名称
        t = r.sub('', self.tokens[-1].string)
        if len(t) == 0:
            #如果为空
            self.Q_name = self.long_name = self.V_name
        else :
            dot = t.find('.')
            if dot == -1:
                #没有'.', 使用VAR名称
                self.Q_name = self.V_name
            else :
                self.Q_name = t[:dot]
            self.long_name = t

        #把Q名字中的'-'改为'_'
        self.Q_name = self.Q_name.replace('-','_')
        self.P_name = self.Q_name
        
        #检查问题的类型
        if self.tokens[1].type == Token.TOKEN_SINGLE:
            self.type_ques = Sentense_ques.QUESTION_SINGLE
            self.col = self.tokens[2]
        elif self.tokens[1].type == Token.TOKEN_MULTI:
            self.type_ques = Sentense_ques.QUESTION_MULTI
            self.col = self.tokens[2]
        elif self.tokens[1].type == Token.TOKEN_COL:
            #不是single和multi的,都是number
            self.type_ques = Sentense_ques.QUESTION_NUMBER
            self.col = self.tokens[1]
        else:
            print("无法分析问题的类型")
            raise None

#这一行是选项, 解析值和对应的名字
class Sentense_opti(Sentense):
    def __init__(self, ts=[], s='', l = 0):
        super(Sentense_opti, self).__init__(ts, s, l, Sentense.SENTENSE_OPTION)
        if len(self.tokens) != 2:
            print("选项行应该只有2个token:", self.string)
            raise None
        r = re.compile('(\A\s*)|(\s*\Z)|(\')')
        self.option_key = int(r.sub('', self.tokens[0].string))
        self.option_name = r.sub('', self.tokens[1].string)

def parse_sentense(s, l = -1):
    #获取':'前面的,开始解析, 没有':', 照样解析
    s1 = s.split(':')[0]

    ts = []
    #解析不是空格的单词
    for i in re.finditer(r'\S+', s1):
        t = token_parse(i.string[i.start():i.end()], i.start(), i.end() - i.start())
        ts.append(t)
        if t.type == Token.TOKEN_FI:
            #停止解析, 这一行是判断条件
            break
        elif t.type == Token.TOKEN_NUMBER:
            #停止解析, 这一行是现象行
            break

    #处理':'后面的,当作没意义的字符串
    p = s.find(':')
    if p != -1:
        t = Token(s[p+1:], p+1, len(s)-p-1)
        t.type = Token.TOKEN_BLACK
        ts.append(t)

    o = None
    if ts[0].type == Token.TOKEN_FI:
        o = Sentense_cond(ts, s, l)
    elif ts[0].type == Token.TOKEN_QUESTION:
        o = Sentense_ques(ts, s, l)
    elif ts[0].type == Token.TOKEN_NUMBER:
        o = Sentense_opti(ts, s, l)
    else:
        #忽略这一行, 其中可能有特殊关键字
        o = Sentense(ts, s, l, Sentense.SENTENSE_BLACK)

    for i in o.tokens :
        i.sentense = o

    #if o.type == Sentense.SENTENSE_QUESTION:
        #print(o)
    return o

class Question(object):
    #全局变量
    ques_dict = {}
    all_ques = []
    Q_ques_dict = {}
    

    def __init__(self):
        self.sentenses = []
        #member vars use Sentense
        self.question = None
        self.condition = None
        self.options = []

        #是否循环, 0表示没有循环, 1表示循环的第一个,2表示循环最后一个,3表示其他
        self.loop_state = 0


    def __str__(self):
        return '%s => %s\n' % ( Sentense_ques.question_type_names[self.question.type_ques],self.sentenses[0].string)

    def add_question(self):
        #对于单选题, 如果没有选项,遍为number问题
        if self.question.type_ques == Sentense_ques.QUESTION_SINGLE and len(self.options) == 0:
            self.question.type_ques = Sentense_ques.QUESTION_NUMBER

        #把问题添加到dict和question中
        Question.all_ques.append(self)
        Question.ques_dict[self.question.V_name] = self
        if not self.question.Q_name in Question.Q_ques_dict:
            Question.Q_ques_dict[self.question.Q_name] = []
        Question.Q_ques_dict[self.question.Q_name].append(self)
        return 

    @staticmethod
    def reset_all():
        #清空字典的question数组
        Question.ques_dict = {}
        Question.all_ques = []
        Question.Q_ques_dict = {}


    @staticmethod
    def check_loop():
        for i in Question.Q_ques_dict:
            qs = Question.Q_ques_dict[i]
            if len(qs) == 1:
                continue

            #如果Q_name一样,就是循环,第一个是开头,最后一个是结尾
            #name的检查序号
            loop_ok = True
            for c in range(1, len(qs)):
                p = qs[c-1]
                c = qs[c]

                #检查var号码是否连续?
                p_no = p.question.V_name
                c_no = c.question.V_name
                #取出最后一部分
                r = re.compile('\d+\Z')
                p_r = re.search(r, p_no)
                c_r = re.search(r, c_no)
                if (not p_r) or (not c_r):
                    #检查不正确
                    loop_ok = False
                    break
                p_no = int(p_r.string[p_r.start():p_r.end()])
                c_no = int(c_r.string[c_r.start():c_r.end()])
                if p_no + 1 != c_no:
                    loop_ok = False
                    break
                   
            if loop_ok:
                qs[0].loop_state = 1
                for c in qs[1:-1]:
                    c.loop_state = 3
                qs[-1].loop_state = 2
                #更新P_name
                for c in range(len(qs)):
                    qs[c].question.P_name += '_' + str(c+1)

def parse_file(f):
    #重值全局变量
    Question.reset_all()
    Question_P.all_ques = []

    #记录当前问题
    q = None
    expects = ( Sentense.SENTENSE_QUESTION, )
    #行号
    l = 0
    while True:
        s = f.readline()
        if not s :
            break 

        s = s.decode('gbk')

        l += 1

        #过滤掉空行
        r = re.compile('\s*')
        if len(r.sub('', s)) == 0:
            continue

        #print('sentense: %s' % s)
        s = parse_sentense(s, l)

        if s.type == Sentense.SENTENSE_BLACK:
            continue
        if not s.type in expects:
            print("解析失败, 获取%d, 期望是:%s" % (s.type,str(expects)))
            raise None
        
        if s.type == Sentense.SENTENSE_QUESTION :
            #当前行是问题, 前一个问题结束
            if q:
                q.add_question()

            q = Question()
            #检查问题类型
            q.question = s
            #下一行可能是新的问题，也可能是条件,可可能是选项
            expects = (Sentense.SENTENSE_QUESTION, Sentense.SENTENSE_CONDITION, Sentense.SENTENSE_OPTION)
        elif s.type == Sentense.SENTENSE_CONDITION:
            q.condition = s
            #条件行下面必须有选项???
            expects = (Sentense.SENTENSE_QUESTION, Sentense.SENTENSE_OPTION)
        elif s.type == Sentense.SENTENSE_OPTION:
            expects = (Sentense.SENTENSE_OPTION, Sentense.SENTENSE_QUESTION)
            q.options.append(s)
        elif s.type == Sentense.SENTENSE_BLACK:
            #忽略的行??
            expects = (Sentense.SENTENSE_QUESTION, Sentense.SENTENSE_CONDITION, Sentense.SENTENSE_OPTION)

        s.ques = q
        q.sentenses.append(s)

    if q:
        q.add_question()

    #print(Question.ques_dict)

    #处理过滤条件
    for i in Question.all_ques:
        if i.condition:
            i.condition.parse_condition()

    #处理循环的题目
    Question.check_loop()

    #遍历所有的var的问题, 生成prg的问题
    for q in Question.all_ques:
        qp = None
        t = q.question.type_ques
        if q.loop_state == 0 :
            if t == Sentense_ques.QUESTION_SINGLE:
                qp = Question_P_Single(q)
            elif t == Sentense_ques.QUESTION_MULTI:
                qp = Question_P_Multi(q)
            else:
                qp = Question_P_Number(q)
            Question_P.all_ques.append(qp)
        elif q.loop_state == 1:
            qs = Question.Q_ques_dict[q.question.Q_name]
            for q1 in qs:
                if t == Sentense_ques.QUESTION_SINGLE:
                    qp = Question_P_Loop_Single(q1)
                elif t == Sentense_ques.QUESTION_MULTI:
                    qp = Question_P_Loop_Multi(q1)
                else:
                    qp = Question_P_Loop_Number(q1)
                Question_P.all_ques.append(qp)

            #添加grid问题
            if t == Sentense_ques.QUESTION_SINGLE:
                qp = Question_P_Grid_Single(q)
            elif t == Sentense_ques.QUESTION_MULTI:
                qp = Question_P_Grid_Multi(q)
            else:
                qp = Question_P_Grid_Number(q)
            Question_P.all_ques.append(qp)


    for q in Question_P.all_ques:
        q.format()
                
    return Question_P.all_ques

def axe_file(var_file):
    f = read_open(sys.argv[1])
    qs = parse_file(f)
    f.close()

    #print '\n'.join([str(i) for i in qs])

    #生成axe文件
    axe_f = write_open(output_dir + '/axe.prg')
    for q in qs:
        axe_f.write((CRLF.join(q.outputs)).encode('gbk'))
        axe_f.write(CRLF.encode('gbk'))
        axe_f.write(CRLF.encode('gbk'))
    axe_f.close()
    
    #tab.prg文件
    lines = []
    for q in Question.all_ques: 
        o = ''
        if q.loop_state == 0:
            o = 'tab ' + q.question.P_name + ' ban1'
        elif q.loop_state != 1:
            #对于循环,只有第一个文件才输出
            pass
        else:
            q_name = q.question.Q_name
            #遍历循环题目
            l_qs = Question.Q_ques_dict[q_name]
            for l in l_qs:
                o = 'tab ' + l.question.P_name +' ban1'
                lines.append(o)
            #grid tab
            o = 'tab ' + q_name + ' grid'
            lines.append(o)

    write_lines('tab.prg', lines)

def bat_file(var_file):
    #根据VAR文件名构造DAT文件名
    DATA_F = os.path.split(var_file)[-1]
    r = re.compile('\.var\Z', re.I)
    DATA_F = r.sub('.dat', DATA_F)

    lines = []
    #1.bat文件
    lines.append('@echo *include 1.prn;e=1 >dp.prn')
    lines.append('call quantum dp.prn ' + DATA_F)
    lines.append('call qout -p a.exp')
    lines.append('call q2cda -p a.exp count.csv')

    lines.append('')

    lines.append('@echo *include 1.prn;e=2 >dp.prn')
    lines.append('call quantum dp.prn ' + DATA_F)
    lines.append('call qout -p a.exp')
    lines.append('call q2cda -p a.exp col.csv')
    lines.append('')
    lines.append('call quclean -a -y')
    lines.append('del a.exp')
    lines.append('del *.bak')

    write_lines('1.bat', lines)

def prn_file():
    lines = []
    lines.append('struct;read=0;reclen=32000')
    lines.append('ed')
    lines.append('')
    lines.append('/* ADEval')
    lines.append('')
    lines.append('/*most often user')
    lines.append('')
    lines.append('end')
    lines.append('a;decp=2;dec=0;spechar=->;op=&e;side=40;pagwid=5000;paglen=300;indent=2;flush;nopage;nz;nosort;linesbef=0;linesaft=0;nopc;topc;notype;netsort;nzcol')
    lines.append('ttl')
    lines.append('ttl')
    lines.append('#include tab.prg')
    lines.append('#include axe.prg')
    lines.append('#include col.prg')

    write_lines('1.prn', lines)

def prg_file():
    lines = []
    lines.append('l ban1')
    lines.append('n10Total')

    write_lines('col.prg', lines)

def maxima_qt_file():
    lines = []
    lines.append('axes=12000')
    lines.append('elms=14500')
    lines.append('heap=1780000')
    lines.append('namevars=13000')
    lines.append('incs=11000')
    lines.append('incheap=14000')
    lines.append('coldefs=1250')
    lines.append('textdefs=1200')
    lines.append('punchdefs=1320')

    write_lines('MAXIMA.QT', lines)

def alias_qt_file():
    lines = []
    lines.append(u'base1 N10基数：有效被访者;nocol;noexport')
    lines.append(u'tots n05合计;nocol;nosort;nonz')
    lines.append(u'totm n01合计;c=+;nocol;nosort;noexport;nonz')
    
    write_lines('ALIAS.QT', lines)

if __name__ == '__main__' :
    if len(sys.argv) < 2:
        print("Usage: %s <file-name>" % sys.argv[0])
    if len(sys.argv) >=3 :
        output_dir = sys.argv[2]
        
    axe_file(sys.argv[1])
    bat_file(sys.argv[1])
    prg_file()
    prn_file()
    maxima_qt_file()
    alias_qt_file()


