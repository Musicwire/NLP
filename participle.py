#-*- coding:utf-8 -*-
import sys
import os
import time
import math
import platform

window_size=20

def text_analyse(path):
    global sumnum                                       #记录整个运行过程处理文件总个数
    global text_vector                                  #文本向量
    global filenum                                      #记录文件夹文件数
    global filenum_temp                                 #记录目前文件夹文件数
    global filename                                     #记录当前文件夹名
    global file_time                                    #记录当前文件开始时间
    global wordnum_doc                                  #记录本各文件处理字数
    global system                                       #记录操作系统类型

    if os.path.isdir(path):                             ###判断为文件夹

        for x in os.listdir(path):                      #遍历本文件夹中各个文件或文件夹

            if os.path.split(path)[1] == '.DS_Store':   ##排除mac中系统文件
                continue


            if os.path.isdir(os.path.join(path, x)):    ##如果本文件夹中是文件夹,初始化

                filenum_temp = 0
                filename = x

                filenum = len(os.listdir(os.path.join(path, x)))
                if system == 'Darwin':
                    filenum -= 1

                if filenum:
                    text_analyse(os.path.join(path, x)) #递归处理
                                                        #输出文件处理结果,并重置参数
                print(' '*150 + '\r' + ' '*50 + '#'*20 + '100%  ||  ' + '%-5.2f s\r'%(time.time()-file_time) + '%s'%filename)
                file_time = time.time()


            else:                                       ##如果本文件夹中是文件

                filenum_temp += 1                       #输出文件处理进度
                print(' '*150 + '\r' + ' '*21 + '%-5.2f s  ||  '%(time.time()-file_time) + "%5d/%-5d  || "%(filenum_temp, filenum) + '#'*int(20*filenum_temp/filenum) + '%3.0f%%\r'%(100*filenum_temp/filenum) + '%-15s ||\r'%x, end = "")

                text_analyse(os.path.join(path, x))     #递归处理

    elif os.path.isfile(path):                          ###判断为文件

        file_path = os.path.split(path)                 #分割出目录与文件
        if file_path[1] == '.DS_Store':                 ##排除mac中系统文件
            return

        fpo = open(os.path.join(sys.path[0], sys.argv[5], path[path.find(sys.argv[1].split('/')[-2])+len(sys.argv[1].split('/')[-2])+1:] + "_out.txt"), "ab")
        for i in text_vector:
            if file_path[1] in text_vector[i][1]:
                fpo.write(b'**' + i.encode() + b'\n' + b' '*20 + b'|' + b' '*5 + str((text_vector[i][1][file_path[1]]/wordnum_doc[file_path[1]])*math.log(sumnum/len(text_vector[i][1]), 2)).encode() + b'\n' + b"-"*50 + b'\n')


def max_match_segment(line, filename):
    global dic                                          #字典
    global all                                          #总字数
    global text_vector                                  #文本向量

    words = []
    num = 0
    idx = len(line)

    while idx > 0:                                      #以window_size为单位，将该行分割成多个窗口，并逐个处理
        matched = False
        for i in range(0, window_size):                 #在单个窗口中，以类似TCP滑动窗口协议原理的方式滑动截断
            loss = window_size - i
            if idx < window_size:                       #若本行剩余字数小于窗口大小
                if i < idx:
                    cand = line[i:idx]
                    loss = idx-i
                else:
                    continue
            else:                                       #若本行剩余字数大于窗口大小
                cand = line[idx-window_size+i:idx]
            if cand in dic:                             #查询词是否在字典中，若有，窗口减去该词长度
                words.append(cand)
                if not cand in text_vector:             #查询词是否在向量中,若没有则初始化
                    text_vector[cand] = [0, {}]

                if not filename in text_vector[cand][1]:#查询本文件是否在向量该词中,若没有则初始化
                    text_vector[cand][1][filename] = 0

                text_vector[cand][0] += 1
                text_vector[cand][1][filename] += 1
                matched = True                          #若在字典中,窗口减字数
                idx -= loss
                num += 1
                break

        if not matched:                                 #若无在字典中，窗口减一
            i = 1
            words.append(line[idx-i])
            idx -= i
            num += 1
    words.reverse()                                     #因为反向最大匹配，需逆转
    return words

def participle(path):
    global num                                          #记录本文件夹处理文件个数
    global sumnum                                       #记录整个运行过程处理文件总个数
    global text_vector                                  #文本向量
    global filenum                                      #记录文件夹文件数
    global filenum_temp                                 #记录目前文件夹文件数
    global filename                                     #记录当前文件夹名
    global file_time                                    #记录当前文件开始时间
    global start                                        #记录程序时间
    global startagain                                   #记录本文件夹开始时间
    global wordnum_doc                                  #记录本各文件处理字数
    global wordnum_file                                 #记录本文件夹处理字数
    global wordsumnum                                   #记录整个运行过程处理字数
    global system                                       #记录操作系统类型

    if os.path.isdir(path):                             ###判断为文件夹

        for x in os.listdir(path):                      #遍历本文件夹中所有文件或文件夹

            if x == '.DS_Store':                        ##排除mac中系统文件
                continue


            if os.path.isfile(os.path.join(path, x)):   ##如果本文件夹中是文件

                filenum_temp += 1                       #显示此时的处理进度
                print(' '*150 + '\r' + ' '*21 + '%-5.2f s  ||  '%(time.time()-file_time) + "%5d/%-5d  || "%(filenum_temp, filenum) + '#'*int(20*filenum_temp/filenum) + '%3.0f%%\r'%(100*filenum_temp/filenum) + '%-15s ||\r'%x, end = "")
                participle(os.path.join(path, x))       #递归处理


            else:                                       ##如果本文件夹中是文件夹

                filenum_temp = 0                        #参数初始化
                filename = x

                if system == 'Windows':                 #创建输出文件的文件夹
                    os.mkdir(os.path.join(sys.path[0], sys.argv[5], path[path.find(sys.argv[1].split('\\')[-2])+len(sys.argv[1].split('\\')[-2])+1:], filename))
                else:
                    os.mkdir(os.path.join(sys.path[0], sys.argv[5], path[path.find(sys.argv[1].split('/')[-2])+len(sys.argv[1].split('/')[-2])+1:], filename))

                filenum = len(os.listdir(os.path.join(path, filename)))
                if system == 'Darwin':
                    filenum -= 1

                if filenum:
                    participle(os.path.join(path, x))   #递归处理

                now = time.time() - startagain          #打印处理结果
                print(' '*150 + '\r' + ' '*45 + "  ||" + '#'*20 + '100%\r' + "+++-------", filename.center(14),"-------+++")
                print('处理本文件夹运行耗时共 %f 秒'%now)
                try:
                    print('本文件夹平均分词速度 %f 微秒每个词'%(100000*now/wordnum_file))
                except:
                    print('本文件夹分词数为0')
                print('本文件夹总共处理了 %d 个文件'%num)
                print("+++--------------------------------+++\n")

                sumnum += num                           #参数重置
                wordsumnum += wordnum_file
                wordnum_file = 0
                num = 0
                startagain = time.time()
                file_time = time.time()

    elif os.path.isfile(path):                          ###判断为文件

        file_path = os.path.split(path)                 #分割出目录与文件

        fpi = open(path, "rb")

        if system == 'Windows':
            fpo = open(os.path.join(sys.path[0], sys.argv[5], path[path.find(sys.argv[1].split('\\')[-2]) + len(sys.argv[1].split('\\')[-2]) + 1:path.find(path.split('\\')[-1]) - 1], file_path[1] + "_out.txt"), "wb")
        else:
            fpo = open(os.path.join(sys.path[0], sys.argv[5], path[path.find(sys.argv[1].split('/')[-2])+len(sys.argv[1].split('/')[-2])+1:path.find(path.split('/')[-1])-1], file_path[1] + "_out.txt"), "wb")

        wordnum_doc[file_path[1]] = 0
        filetype = sys.argv[2]

        paper = fpi.read()                              #读取文件并分割
        paper = paper.split(b'\n')
        for line in paper:                              #逐行读取并处理
            if not line:                                #跳过行为空的情况
                continue
                                                        #进行处理操作
            word = max_match_segment(line.decode(filetype, "replace").strip(), file_path[1])

            change = "|"                                #处理结果输出到文件夹
            fpo.write((change.join(word)).encode() + b"\n")

            wordnum_doc[file_path[1]] += len(word)      #统计参数
            wordnum_file += wordnum_doc[file_path[1]]
                                                        #所有文件分词结束
        fpo.write('\n\n+++-----------------文本向量----------------+++\n\n\n'.encode())
        fpi.close()
        fpo.close()
        num += 1

if __name__=="__main__":

    start = time.time()                                 #记录时间
    text_vector = {}                                    #文本向量
    filenum = 0.0                                       #记录文件夹文件数
    filenum_temp = 0.0                                  #记录目前文件夹文件数
    filename = ''                                       #记录当前文件夹名
    wordnum_doc = {}                                    #记录本各文件处理字数
    wordnum_file = 0                                    #记录本文件夹处理字数
    wordsumnum = 0.0                                    #记录整个运行过程处理字数
    num = 0.0                                           #记录本文件夹处理文件个数
    sumnum = 0.0                                        #记录整个运行过程处理文件总个数
    system = platform.system()                          #记录操作系统

    try:
        os.mkdir(os.path.join(sys.path[0], sys.argv[5]))
    except:                                             #创建输出文件的文件夹目录,若存在则清空文件夹
        if system == 'Windows':
            os.popen('del/s/q %s' % os.path.join(sys.path[0], sys.argv[5], '*.*'))
        else:
            os.popen('rm -rf %s' % os.path.join(sys.path[0], sys.argv[5], '*'))

    time.sleep(1)

    if system == 'Windows':                             #创建输出文件的文件夹目录
        os.mkdir(os.path.join(sys.path[0], sys.argv[5], ('\\' +sys.argv[1]).split('\\')[-1]))
    else:
        os.mkdir(os.path.join(sys.path[0], sys.argv[5], ('/' +sys.argv[1]).split('/')[-1]))

    fpd=open(os.path.join(sys.path[0],sys.argv[3]),"rb")#打开字典文件，并转换成dictionary结构
    dic_row = fpd.read().split(b'\n')
    dictype = sys.argv[4]
    dic = set('')
    for i in dic_row:
        dic.add(i.decode(dictype).strip())              #注意用strip函数将换行符、回车符、空格符等等都去掉
    fpd.close()


    startagain = time.time()
    file_time = time.time()
    participle(os.path.join(sys.path[0], sys.argv[1]))  #开始对所有文件进行分词

    now = time.time()                                   #收尾统计工作
    print("+++---------------------------------+++")
    print('所有文件分词共耗时 %f 秒'%(now-start))
    print('进行了 %d 次分词'%wordsumnum)
    print('平均分词速度 %f 微秒每个词'%(1000000*(now-start)/wordsumnum))
    print('总共处理了 %d 个文件'%sumnum)
    print("+++---------------------------------+++\n")
    print('\n+++-----------分析文本向量-----------+++')

    file_time = time.time()
    text_analyse(os.path.join(sys.path[0], sys.argv[1]))#开始统计所有文件的文本向量

    end = time.time()                                   #收尾统计工作
    print("+++---------------------------------+++")
    print('分析文本向量共耗时 %f 秒'%(end-now))
    print('总共处理了 %d 个文件' % sumnum)
    print('平均每个文件 %f 毫秒'%(1000*(end-now)/sumnum))
    print("+++---------------------------------+++")