#-*- coding:utf-8 -*-
import sys
import os
import platform
import time
import math
import string

def calc():
    global words                                        #所有词
    global dict                                         #词典
    global words_temp                                   #当前文件内所有词
    global type_pre                                     #上一个文本类型

    for i in words_temp:                                #统计该类所有词
        if not i in dict:
            dict[i] = {}
            dict[i]['总'] =  0

        if not type_pre in dict[i]:
            dict[i][type_pre] = 0

        dict[i][type_pre] += words_temp[i]
        dict[i]['总'] += words_temp[i]

    for i in words_temp.keys():
        words.add(i)

def analyse(path):

    global words_temp                                   #当前文件内所有词
    global TF_IDF                                       #tf-idf

    word = set()

    fpi = open(path, "rb")                              #扫出该文件的所有词
    file = fpi.read().split(b'\n')
    flag = 0
    for line in file:
        if not line.decode() == '+++-----------------文本向量----------------+++' and not flag:
            continue
        else:
            flag += 1
        if line and line.decode()[0] == '*' and flag:
            word.add(line.decode().strip()[2:])
            temp = line.decode().strip()[2:]
        elif line and not line.decode().find('|') == -1:
            if not type_pre in TF_IDF:
                TF_IDF[type_pre] = {}
            if not temp in TF_IDF[type_pre]:
                TF_IDF[type_pre][temp] = 0

            TF_IDF[type_pre][temp] += float(line.decode()[line.decode().rfind(' ')+1:])

    for i in word:                                      #统计当前文件内所有词
        if i in words_temp:
            words_temp[i] += 1
        else:
            words_temp[i] = 1

    fpi.close()

def chose(path):

    global words_temp                                   #当前文件夹内所有词
    global type                                         #所有文本类型
    global type_pre                                     #上一个文本类型
    global dict                                         #词典
    global filenum                                      #当前文件夹文档数量
    global filenum_temp                                 #当前文件夹文档数量(打印处理进度专用)
    global filenum_sum                                  #所有文档数量
    global file_time                                    #本文件夹处理时间
    global system                                       #操作系统类型
    global first_chose_file                             #第一次进入该类文件

    if os.path.isdir(path):                             ###判断为文件夹

        for x in os.listdir(path):                      #遍历各个分文件夹、遍历分文件夹中各个文件

            if os.path.split(path)[1] == '.DS_Store':   ##排除mac中系统文件
                continue

            if os.path.isdir(os.path.join(path, x)):    ##如果本文件夹中是文件夹,初始化其中的文件夹

                first_chose_file = 1
                filenum_temp = 0
                filename = x

                filenum = len(os.listdir(os.path.join(path, x)))
                if system == 'Darwin':
                    filenum -= 1

                if filenum:
                    chose(os.path.join(path, x))        #递归处理
                                                        #输出文件处理结果,并重置参数
                print(' '*150 + '\r' + ' '*50 + '#'*20 + '100%  ||  ' + '%-5.2f s\r'%(time.time()-file_time) + '%s'%filename)
                file_time = time.time()


            else:                                       ##如果本文件夹中是文件

                if first_chose_file:
                    first_chose_file = 0
                    type_pre = os.path.split(path)[1]  # 添加文本类别并进行初始化
                    type.append(type_pre)
                    dict['总'][type_pre] = 0

                filenum_temp += 1                       #输出文件处理进度
                print(' '*150 + '\r' + ' '*21 + '%-5.2f s  ||  '%(time.time()-file_time) + "%5d/%-5d  || "%(filenum_temp, filenum) +'#'*int(20*filenum_temp/filenum) +'%3.0f%%\r'%(100*filenum_temp/filenum) + '%-15s ||\r' % type_pre, end = '')

                chose(os.path.join(path, x))            #递归处理

                calc()                                  #换类型,做统计

                words_temp.clear()


    elif os.path.isfile(path):                          ###判断为文件

        if os.path.split(path)[1] == '.DS_Store':       ##排除mac中系统文件
            return

        dict['总'][type_pre] += 1
        filenum_sum += 1
        analyse(path)

def vector():

    global type                                         #所有文本类型
    global words                                        #所有词
    global dict                                         #词典
    global filenum_sum                                  #所有文档数量
    global A                                            #属于该文本类型又包含该词的文档数量
    global B                                            #不属于该文本类型但包含该词的文档数量
    global C                                            #属于该文本类型但不包含该词的文档数量
    global D                                            #不属于该文本类型又不包含该词的文档数量
    global result                                       #当前文本类型内所有词的向量

    result_temp = {}

    for j in type:                                      #初始化
        A[j] = {}
        B[j] = {}
        C[j] = {}
        D[j] = {}

    for i in words:                                     #统计所有词的向量信息
        if i == '':
            continue
        for j in dict[i]:
            if j == '总':
                continue
            A[j][i] = dict[i][j]
            B[j][i] = dict[i]['总'] - A[j][i]
            C[j][i] = dict['总'][j] - A[j][i]
            D[j][i] = filenum_sum - A[j][i] - B[j][i] - C[j][i]

    for j in type:                                      #统计所有文本类型的向量及概率
        result[j] = {}
        for i in A[j]:
            result_temp[i] = pow((A[j][i] * D[j][i] - B[j][i] * C[j][i]), 2) / ((A[j][i] + B[j][i]) * (C[j][i] + D[j][i]))

                                                        #截取文本向量值最高的
        for m in sorted(result_temp, key=result_temp.get, reverse=True)[:5]:
            result[j][m] = [result_temp[m], dict[m][j]]

        result_temp.clear()
                                                        #输出文本向量统计结果
    fdo = open(os.path.join(sys.path[0], 'eigenvalue.txt'), 'w')
    for j in sorted(result):
        fdo.writelines("+++---------------------------------+++\n")
        for i in sorted(result[j], key=result[j].get, reverse=True):
            fdo.writelines('%-15s' % j + '%-10s' % i + '\n' + ' ' * 20 + '%-25s' % str(result[j][i][0]) + '%15s' % str(result[j][i][1]) + '\n')
    fdo.close()

def classify(path):

    global dict                                         #词典
    global type                                         #所有文本类型
    global filenum                                      #当前文件夹文档数量
    global filenum_temp                                 #当前文件夹文档数量(打印处理进度专用)
    global filenum_sum                                  #所有文档数量
    global file_classify                                #所进行处理的类别
    global type_name                                    #当前文本类型
    global file_time                                    #本文件夹处理时间
    global system                                       #操作系统类型
    global TF_IDF                                       #tf-idf
    global match                                        #分类正确

    if os.path.isdir(path):                             ###判断为文件夹

        for x in os.listdir(path):                      #遍历各个分文件夹、遍历分文件夹中各个文件

            if os.path.split(path)[1] == '.DS_Store':   ##排除mac中系统文件
                continue


            if os.path.isdir(os.path.join(path, x)):    ##如果本文件夹中是文件夹,初始化其中的文件夹

                filenum_temp = 0
                filename = x

                file_classify.update(os.listdir(path))
                file_classify.remove('.DS_Store')
                filenum = len(os.listdir(os.path.join(path, x)))

                if system == 'Darwin':
                    filenum -= 1

                if filenum:
                    classify(os.path.join(path, x))     #递归处理
                                                        #输出文件处理结果,并重置参数
                print(' '*150 + '\r' + ' '*50 + '#'*20 + '100%%  ||  %-5.2f s  ||  Recall:%-5.2f%%  ||  Precision:%-5.2f%%\r'%(time.time()-file_time, 100*match/dict['总'][filename], 100*match/len(os.listdir(os.path.join(path, x)))) + '%s'%filename)
                match = 0
                file_time = time.time()


            else:                                       ##如果本文件夹中是文件

                filenum_temp += 1                       #输出文件处理进度

                classify(os.path.join(path, x))         #递归处理

                print(' ' * 150 + '\r' + ' ' * 21 + '%-5.2f s  ||  ' % (time.time() - file_time) + "%5d/%-5d  || " % (filenum_temp, filenum) + '#' * int(20 * filenum_temp / filenum) + '%3.0f%%\r' % (100 * filenum_temp / filenum) + '%-15s ||\r' % type_pre, end="")


    elif os.path.isfile(path):                          ###判断为文件

        if os.path.split(path)[1] == '.DS_Store':       ##排除mac中系统文件
            return

        fpi = open(path, "rb")                          #扫出该文件的所有词
        file = fpi.read().split(b'\n')
        word = set()
        flag = 0
        for line in file:
            if not line.decode() == '+++-----------------文本向量----------------+++' and not flag:
                continue
            else:
                flag += 1
            if line and line.decode()[0] == '*' and flag:
                word.add(line.decode().strip()[2:])
        fpi.close()

        temp = {}
        for i in file_classify:
            temp[i] = math.log(dict['总'][i]/filenum_sum, 2)
            for j in word:
                if j in dict and i in dict[j]:
                    temp[i] += math.log(TF_IDF[i][j]*(dict[j][i]+1)/(dict['总'][i]+2), 2)
                else:
                    temp[i] += math.log((0+1)/(dict['总'][i]+2), 2)

        fpo = open(os.path.join(sys.path[0], 'classify_result.txt'), "ab")
        fpo.write(os.path.split(path)[0][os.path.split(path)[0].find(sys.argv[2])+len(sys.argv[2])+1:].encode() + b" "*20 + os.path.split(path)[1].encode() + b" "*20 + sorted(temp, key=temp.get, reverse=True)[0].encode() + b'\n')
        if sorted(temp, key=temp.get, reverse=True)[0].encode() == os.path.split(path)[0][os.path.split(path)[0].find(sys.argv[2])+len(sys.argv[2])+1:].encode():
            match += 1


if __name__=="__main__":

    #global
    dict = {}                                           #所有词
    dict['总'] = {}                                     #所有文本的信息
    TF_IDF = {}                                         #tf-idf
    type = []                                           #所有文本类型
    type_pre = ""                                       #上个处理的文本类型
    words = set()                                       #所有词
    words_temp = {}                                     #当前文件夹内所有词
    filenum = 0                                         #当前文件夹文档数量
    filenum_temp = 0                                    #当前文件夹内文档数量
    filenum_sum = 0                                     #所有文档数量
    file_classify = set()                               #所进行处理的类别
    first_chose_file = 1                                #第一次进入该类文件
    system = platform.system()                          #记录操作系统
    match = 0                                           #分类正确
    A = {}                                              #属于该文本类型又包含该词的文档数量
    B = {}                                              #不属于该文本类型但包含该词的文档数量
    C = {}                                              #属于该文本类型但不包含该词的文档数量
    D = {}                                              #不属于该文本类型又不包含该词的文档数量
    result = {}                                         #当前文本类型内所有词的向量
                                                        #开始提取所有文件样本分词
    print('\n             +++-------------------------------+++')
    print('++-----------+++---------提取样本分词----------+++-----------++')
    print('             +++-------------------------------+++\n')
    sum_time = file_time = time.time()
    chose(os.path.join(sys.path[0], sys.argv[1]))
    print('             +++-------------------------------+++')
    print("                 提取样本分词共耗费%f s"%(time.time()-sum_time))
    print('             +++-------------------------------+++')

    vector()                                            #开始处理所有文件特征值

                                                        #开始进行文本分类
    print('\n\n             +++-------------------------------+++')
    print('++-----------+++---------开始文本分类----------+++-----------++')
    print('             +++-------------------------------+++\n')
    sum_time = file_time = time.time()
    if system == 'Windows':
        os.popen('del/s/q %s' % os.path.join(sys.path[0], 'classify_result.txt'))
    else:
        os.popen('rm -rf %s' % os.path.join(sys.path[0], 'classify_result.txt'))
    classify(os.path.join(sys.path[0], sys.argv[2]))
    print('             +++-------------------------------+++')
    print("                 进行文本分类共耗费%f s"%(time.time()-sum_time))
    print('             +++-------------------------------+++')