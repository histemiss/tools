#!/usr/bin/python3
# -*- coding:utf-8 -*- 

import re
import os
import sys

#global control variable
#命令行第一个字符为空格,现在没有使用
option_black = False

#回车变量
CRLF = '\r\n'

#辅助函数

#读打开文件，不需要转义回车
def write_open(fn):
    f = open(fn, 'w', encoding = 'gbk', newline = '')
    return f

def read_open(fn):
    f = open(fn, 'r', encoding = 'gbk', newline = CRLF)
    return f

#输出文件夹
output_dir = '.'

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
        TOKEN_QUESTION: '\*[a-zA-Z][a-zA-Z0-9_]*', 
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

    def parse_condition(self):
        #先解析括号里面的内容
        #FI ( XXXX ) :
        #先分离':'前面的条件
        cond_str = self.string.split(':')[0]
        r = re.compile('(\AFI\s+\(\s+)|(\s+\)\s+)')
        cond_str = r.sub('', cond_str)
        #只处理 QA2,3类型
        ques_cond_re = '[a-zA-Z][a-zA-Z0-9_]*,[1-9][0-9]*'
        r = re.compile('\A' + ques_cond_re + '\Z')
        if not re.match(r,cond_str):
            #匹配失败,去掉条件
            return
        a = cond_str.split(',')
        ques_no = a[0]
        sub_col = int(a[1])
        q = Question.ques_dict[ques_no]
        col_start = q.question.col.col_start 
        col_width = q.question.col.col_width
        col_val = 0
        if q.question.type_ques == Sentense_ques.QUESTION_SINGLE:
            col_val = sub_col
            if col_width == 1:
                #;c=c680'1'
                self.output = ';c=c'
                self.output += str(col_start) +'\'' + str(col_val) + '\''
            else:
                #;c=c(75,76).eq.20
                self.output = ';c=c(' 
                self.output += str(col_start) + ',' + str(col_start + col_width -1)
                self.output += ').eq.' + str(col_val)
        elif q.question.type_ques == Sentense_ques.QUESTION_MULTI:
            #验证sub_col没有超过选项个数
            assert(col_width >= sub_col)
            col_start += (sub_col-1)
            # ;c=c680'1'
            self.output = ';c=c' + str(col_start) + '\'1\''
        else:
            print('条件解析错误:', line)
            raise None
        #输出

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
        self.name = r.sub('', self.tokens[0].string)
        if self.name[0] != '*':
            print("VAR问题号必须以'*'开头")
            raise None
        self.name = self.name[1:]

        #解析':'后面的字符串,也就是问题名称, 也就是最后一个token
        #一般是 英文词号.中文名称
        t = r.sub('', self.tokens[-1].string)
        if len(t) == 0:
            self.Q_name = self.long_name = self.name
        else :
            dot = t.find('.')
            if dot == -1:
                #没有'.', 使用一个名字
                self.Q_name = t
            else :
                self.Q_name = t[:dot]
            self.long_name = t

        #把Q名字中的'-'改为'_'
        self.Q_name = self.Q_name.replace('-','_')
        
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

def sentense_parse(s, l = -1):
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

    def output(self):
        
        if self.question.type_ques == Sentense_ques.QUESTION_SINGLE:
            return self.output_single()
        elif self.question.type_ques == Sentense_ques.QUESTION_MULTI:
            return self.output_multi()
        elif self.question.type_ques == Sentense_ques.QUESTION_NUMBER:
            return self.output_number()
        else:
            return ''

    def output_single(self):
        if self.loop_state == 0:
            #如果不是循环, 直接返回字符串
            o  = 'l ' + self.question.Q_name
            if self.condition:
                #添加过滤条件
                o += self.condition.output
            
            o += CRLF
            o += 'n23' + self.question.long_name + CRLF
            o += 'base1' + CRLF

            if self.question.col.col_width == 1:
                #使用1位表示选项顺序
                o += 'col ' + str(self.question.col.col_start) + CRLF
            else :
                #使用多位表示选项顺序
                o += 'fld c' + str(self.question.col.col_start) + ':' + str(self.question.col.col_width) + CRLF
            #输出选项
            for i in self.options:
                o += '+' + i.option_name + '=' + str(i.option_key) + CRLF
            o += 'n03;nosort' + CRLF
            o += 'tots' + CRLF
            o += CRLF
            return o

        elif self.loop_state != 1:
            #相同循环的一块输出
            return ''

        else:
            #对于循环的题目, 把问题放到pub文件
            pub = self.question.Q_name + '.pub'

            #生成pub文件
            o  = 'l &x'
            if self.condition:
                o += ';c=&b'
            o += CRLF
            o += 'n23&y' + CRLF
            o += 'base1' + CRLF
            if self.question.col.col_width ==1:
                o += 'col a0' + CRLF
            else :
                o += 'fld ca0:' + self.question.col.col_width + CRLF
            #输出选项
            for i in self.options:
                o += '+' + i.option_name + '=' + str(i.option_key) + CRLF
            o += 'n03;nosort' + CRLF
            o += 'tots' + CRLF
            o += CRLF

            #写文件
            pub_f = write_open(output_dir + '/' + pub)
            pub_f.write(o)
            pub_f.close()

            #获取Q_name对应的题目数组
            qs = Question.Q_ques_dict[self.question.Q_name]

            o = ''
            #生成inlude命令
            for i in qs:
                o += '*include ' + pub
                if i.condition:
                    #如果有过滤条件 
                    o += ';b=' + i.question.condition.output
                o += ';col(a)=' + str(i.question.col.col_start)
                #tab不能重名，使用VAR题号
                o += ';x=' + i.question.name
                o += ';y=' + i.question.long_name
                o += CRLF
            o += CRLF
       
            #生成grid tab
            lo = 'l ' + self.question.Q_name + CRLF
            #遍历所有的问题
            for i in qs:
                lo += 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start) + CRLF
            lo += 'side' + CRLF
            lo += 'n23' + self.question.Q_name + ' - GRID' + CRLF
            lo += 'base1' + CRLF
            lo += 'col a0' + CRLF
            for i in self.options:
                lo += '+' + i.option_name + '=' + str(i.option_key) + CRLF
            lo += 'n03;nosort' + CRLF
            lo += 'tots' + CRLF
            lo += CRLF
            return o + lo

    def output_multi(self):
        pub = self.question.Q_name + '.pub'

        if self.loop_state == 0 :
            #对于不是循环的, 头部在外面, 先生成pub文件
            o = ''
            #直接遍历所有的选项
            for i in self.options:
                o += 'n01' + i.option_name + ';c=ca' + str(i.option_key-1) + '\'1\'' + CRLF
            o += 'n03;nosort' + CRLF
            o += 'totm' + CRLF
            o += CRLF

            #写文件 
            pub_f = write_open(output_dir + '/' + pub)
            pub_f.write(o)
            pub_f.close()

            #生成include命令, 包括题目头部
            o  = 'l ' + self.question.Q_name
            if self.condition:
                o += self.condition.output
            o += CRLF
            o += 'n23' + self.question.long_name + CRLF
            o += 'base1' + CRLF
            o += '*include ' + pub + ';col(a)=' + str(self.question.col.col_start) + CRLF
            o += CRLF
            return o

        elif self.loop_state != 1:
            #已经在第一个循环中处理
            return ''

        else:
            #准备pub文件,头部放到pub文件中
            o  = 'l &x'
            if self.condition:
                o += ';c=&b'
            o += CRLF
            o += 'n23&y' + CRLF
            o += 'base1' + CRLF

            #遍历所有的选项
            o_noh = ''
            for i in self.options:
                o_noh += 'n01' + i.option_name + ';c=ca' + str(i.option_key-1) + '\'1\'' + CRLF
            o_noh += 'n03;nosort' + CRLF
            o_noh += 'totm' + CRLF
            o_noh += CRLF
            #写文件 
            o += o_noh
            pub_f = write_open(output_dir + '/' + pub)
            pub_f.write(o)
            pub_f.close()

            #构造一个没有头部的
            pub_noh = self.question.Q_name + '-nohead.pub'
            pub_f = write_open(output_dir + '/' + pub_noh)
            pub_f.write(o_noh)
            pub_f.close()

            #生成include命令
            o = ''
            #获取Q_name对应的题目数组
            qs = Question.Q_ques_dict[self.question.Q_name]
            for c in qs:
                o += '*include ' + pub
                if self.condition:
                    o += ';b=' + self.condition.output
                o += ';col(a)=' + str(self.question.col.col_start)
                o += ';x=' + self.question.name 
                o += ';y=' + self.question.long_name
                
            #最后的grid tab
            lo = 'l ' + self.question.Q_name + CRLF
            #遍历所有的问题
            for i in qs:
                lo += 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start) + CRLF
            lo += 'side' + CRLF
            lo += 'n23' + self.question.Q_name + ' - GRID' + CRLF
            lo += 'base1' + CRLF
            #添加不带头的pub文件
            lo += '*include ' + pub_noh
            lo += CRLF
            return o + lo

    def output_number(self):
        if self.loop_state == 0:
            #不是循环
            o  = 'l ' + self.question.Q_name 
            if self.condition:
                o += self.condition.output
            o += CRLF 
            o += 'n23' + self.question.long_name + CRLF
            o += 'base1' + CRLF 
            col_start = self.question.col.col_start 
            col_width = self.question.col.col_width
            if col_start == 1:
                o += 'val c(' + str(col_start) + ');0:9' + CRLF
            else :
                o += 'val c(' + str(col_start) + ',' + str(col_start + col_width -1) + ');0:' + '9'*col_width + CRLF
            o += 'n03;nosort' + CRLF
            o += 'tots' + CRLF 
            o += CRLF
            return o
        elif self.loop_state != 1:
            #循环的第一个问题输出所有的
            return ''
        else :
            #对于循环的题目, 把问题放到pub文件
            pub = self.question.Q_name + '.pub'

            #生成pub文件
            o  = 'l &x'
            if self.condition:
                o += ';c=&b'
            o += CRLF
            o += 'n23&y' + CRLF
            o += 'base1' + CRLF
            col_start = self.question.col.col_start 
            col_width = self.question.col.col_width
            if col_width == 1:
                o += 'val c(a0);0:9' + CRLF
            else:
                o += 'val c(a0,a' + str(col_width-1) + ');0:' + '9' * col_width + CRLF
            o += 'n03;nosort' + CRLF
            o += 'tots' + CRLF
            o += CRLF

            #写文件
            pub_f = write_open(output_dir + '/' + pub)
            pub_f.write(o)
            pub_f.close()

            #获取Q_name对应的题目数组
            qs = Question.Q_ques_dict[self.question.Q_name]

            o = ''
            #生成inlude命令
            for i in qs:
                o += '*include ' + pub
                if i.condition:
                    #如果有过滤条件 
                    o += ';b=' + i.question.condition.output
                o += ';col(a)=' + str(i.question.col.col_start)
                #tab不能重名，使用VAR题号
                o += ';x=' + i.question.name
                o += ';y=' + i.question.long_name
                o += CRLF
            o += CRLF
       
            #生成grid tab
            lo = 'l ' + self.question.Q_name + CRLF
            #遍历所有的问题
            for i in qs:
                lo += 'n01' + i.question.long_name + ';col(a)=' + str(i.question.col.col_start) + CRLF
            lo += 'side' + CRLF
            lo += 'n23' + self.question.Q_name + ' - GRID' + CRLF
            lo += 'base1' + CRLF
            col_start = self.question.col.col_start 
            col_width = self.question.col.col_width
            if col_start == 1:
                lo += 'val c(' + str(col_start) + ');0:9' + CRLF
            else :
                lo += 'val c(' + str(col_start) + ',' + str(col_start + col_width -1) + ');0:' + '9'*col_width + CRLF
            lo += 'n03,nosort' + CRLF
            lo += 'tots' + CRLF
            lo += CRLF
            return o + lo
            
    def add_question(self):
        #把问题添加到dict和question中
        Question.all_ques.append(self)
        Question.ques_dict[self.question.name] = self
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
                p_no = p.question.name
                c_no = c.question.name
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
            
        
def parse_file(f):
    #重值全局变量
    Question.reset_all()

    #记录当前问题
    q = None
    expects = ( Sentense.SENTENSE_QUESTION, )
    #行号
    l = 0
    while True:
        s = f.readline()
        if not s :
            break 
        if len(s) == 0:
            #空文件?
            continue

        #print('sentense: %s' % s)
        s = sentense_parse(s, l)
        l += 1

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
        
    return Question.all_ques

def axe_file(var_file):
    f = read_open(sys.argv[1])
    qs = parse_file(f)
    f.close()

    #print '\n'.join([str(i) for i in qs])

    #生成axe文件
    axe_f = write_open(output_dir + '/axe.prg')
    for i in qs:
        o = i.output()
        if o :
            axe_f.write(o)
    axe_f.write(CRLF)
    axe_f.close()
    
    #tab.prg文件
    o = ''
    for q in qs: 
        if q.loop_state == 0:
            q_name = q.question.Q_name
            if len(q_name) == 0:
                q_name = q.question.name
            o += 'tab ' + q_name + ' ban1' + CRLF
        elif q.loop_state != 1:
            #对于循环,只有第一个文件才输出
            pass
        else:
            q_name = q.question.Q_name
            #遍历循环题目
            l_qs = Question.Q_ques_dict[q_name]
            for i in range(len(l_qs)):
                #题号里面使用序号
                o += 'tab ' + q_name + '_' + str(i+1) +' ban1' + CRLF
            #grid tab
            o += 'tab ' + q_name + ' grid' + CRLF
    o += CRLF

    prg_f = write_open(output_dir + '/tab.prg')
    prg_f.write(o)
    prg_f.close()

def bat_file(var_file):
    #根据VAR文件名构造DAT文件名
    DATA_F = os.path.split(var_file)[-1]
    r = re.compile('\.var\Z', re.I)
    DATA_F = r.sub('.dat', DATA_F)

    #1.bat文件
    o  = '@echo *include 1.prn;e=1 >dp.prn' + CRLF
    o += 'call quantum dp.prn ' + DATA_F + CRLF
    o += 'call qout -p a.exp' + CRLF
    o += 'call q2cda -p a.exp count.csv' + CRLF

    o += CRLF

    o += '@echo *include 1.prn;e=2 >dp.prn' + CRLF
    o += 'call quantum dp.prn ' + DATA_F + CRLF
    o += 'call qout -p a.exp' + CRLF
    o += 'call q2cda -p a.exp col.csv' + CRLF
    o += CRLF
    o += 'call quclean -a -y' + CRLF
    o += 'del a.exp' + CRLF
    o += 'del *.bak' + CRLF
    o += CRLF

    f = write_open(output_dir + '/1.bat')
    f.write(o)
    f.close()

def prn_file():
    o  = 'struct;read=0;reclen=32000' + CRLF
    o += 'ed' + CRLF
    o += '' + CRLF
    o += '/* ADEval' + CRLF
    o += '' + CRLF
    o += '/*most often user' + CRLF
    o += '' + CRLF
    o += 'end' + CRLF
    o += 'a;decp=2;dec=0;spechar=->;op=&e;side=40;pagwid=5000;paglen=300;indent=2;flush;nopage;nz;nosort;linesbef=0;linesaft=0;nopc;topc;notype;netsort;nzcol' + CRLF
    o += 'ttl' + CRLF
    o += 'ttl' + CRLF
    o += '#include tab.prg' + CRLF
    o += '#include axe.prg' + CRLF
    o += '#include col.prg' + CRLF
    o += CRLF

    f = write_open(output_dir + '/1.prn')
    f.write(o)
    f.close()

def prg_file():
    o  = 'l ban1' + CRLF
    o += 'n10Total' + CRLF
    o += CRLF
    f = write_open(output_dir + '/col.prg')
    f.write(o)
    f.close()

def maxima_qt_file():
    o  = 'axes=12000' + CRLF
    o += 'elms=14500' + CRLF
    o += 'heap=1780000' + CRLF
    o += 'namevars=13000' + CRLF
    o += 'incs=11000' + CRLF
    o += 'incheap=14000' + CRLF
    o += 'coldefs=1250' + CRLF
    o += 'textdefs=1200' + CRLF
    o += 'punchdefs=1320' + CRLF

    f = write_open(output_dir + '/MAXIMA.QT')
    f.write(o)
    f.close()

def alias_qt_file():
    o  = u'base1 N10基数：有效被访者;nocol;noexport' + CRLF
    o += u'tots n05合计;nocol;nosort;nonz' + CRLF
    o += u'totm n01合计;c=+;nocol;nosort;noexport;nonz' + CRLF
    o += CRLF
    
    f = write_open(output_dir + '/ALIAS.QT')
    f.write(o)
    f.close()

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


