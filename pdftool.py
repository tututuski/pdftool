#!/usr/bin/python3
#-*- encoding:utf-8 -*-
from PyPDF2 import PdfFileReader,PdfFileWriter
import os,optparse,sys,copy
from math import ceil

def getFileName(filepath):
    file_list = []
    for root,dirs,files in os.walk(filepath):
        for filespath in files:
            # print(os.path.join(root,filespath))
            file_list.append(os.path.join(root,filespath))

    return file_list

def cut_page(page,m={'l':0,'t':0,'r':0,'b':0}):
    new_tl=page.mediaBox.upperLeft
    new_tr=page.mediaBox.upperRight
    new_bl=page.mediaBox.lowerLeft
    new_br=page.mediaBox.lowerRight
    
    new_tl=(new_tl[0]+m['l'],new_tl[1]-m['t'])
    new_tr=(new_tr[0]-m['r'],new_tr[1]-m['t'])
    new_bl=(new_bl[0]+m['l'],new_bl[1]+m['b'])
    new_br=(new_br[0]-m['r'],new_br[1]+m['b'])
    
    page.mediaBox.setUpperLeft(new_tl)
    page.mediaBox.setUpperRight(new_tr)
    page.mediaBox.setLowerLeft(new_bl)
    page.mediaBox.setLowerRight(new_br)
    return copy.deepcopy(page)
    

class pdfSpliter():    
    def __init__(self,inFile,outPath,filenum,startpage=0,endpage=0,m={'l':0,'t':0,'r':0,'b':0},ismerge=0):
        os.system('mkdir -p '+outPath)
        self.infile=inFile
        self.pdfreader=PdfFileReader(inFile) if ismerge==0\
        else None
        self.outPath=outPath
        self.pagenum=self.pdfreader.getNumPages() if ismerge==0 \
        else len(getFileName(inFile))
        self.spage=startpage-1 if startpage>0 else 0
        self.epage=endpage-1 if (endpage>self.spage and endpage<self.pagenum) \
        else self.pagenum-1
        self.fileNum=(filenum if filenum >0 else  (self.epage-self.spage+1))\
                        if ismerge==0 else\
                        (filenum if filenum >0 else 1)
        self.spac=ceil((self.epage-self.spage+1)/self.fileNum)
        self.pagesavecount=0
        self.m=m
        self.ismerge=ismerge
        
    def execute(self):
        if self.ismerge!=0:
            print('merge')
            self.merge()
        else:
            print('split')
            self.split()
    def split(self):
        x=ceil((self.epage-self.spage+1)/self.spac)
        for t in range(x):
            i=t*self.spac+self.spage
            flag=0
            for j in list(range(self.spac))[::-1]:
                pnum=i+j
                if pnum >self.epage:
                    continue
                print(t+1,'-',j+1,' (',x,'/',self.spac,') page:',pnum+1)
                if flag==0:
                    page=cut_page(self.pdfreader.getPage(pnum),self.m)
                    flag=1
                else:
                    pageadd=cut_page(self.pdfreader.getPage(pnum),self.m)
                    high=page['/MediaBox'][3]
                    page.mergeTranslatedPage(page2=pageadd,tx=0,ty=high,expand=True)
            with open(self.outPath+'/'+str(self.pagesavecount)+'.pdf','wb') as rt:
                pdfout=PdfFileWriter()
                pdfout.addPage(page)
                #print('WT high',page['/MediaBox'])
                pdfout.write(rt)
                self.pagesavecount=self.pagesavecount+1
    def merge(self):
        writer=PdfFileWriter()
        for t in range(self.spage,self.epage+1):
            pnum=t
            print(pnum)
            pf=PdfFileReader(self.infile+'/{num}.pdf'.format(num=pnum))
            pagenum=pf.getNumPages()
            for iPage in range(pagenum):
                writer.addPage(pf.getPage(iPage))
        with open(self.outPath+'/'+str(self.pagesavecount)+'.pdf','wb') as rt:
            writer.write(rt)                 
class script_opt:
    def __init__(self):
        #初始化
        parser = optparse.OptionParser()
        parser.add_option("-i", "--infile", dest="infile",default="None", help="\n\
当功能为拆分pdf时(默认拆分),指定为输入pdf的文件路径,当功能为合并时 (存在参数 -m 1) 为含有0.pdf 1.pdf 2.pdf ......的路径")
        parser.add_option("-o", "--outpath",dest="outpath",default='./output', help="\n\
不论功能为合并还是拆分,都为输出路径,若不存在则自动创建")
        parser.add_option("-n", "--outfilenum",type="int", dest="outfilenum",default=0, help="\n\
仅在拆分pdf时有效,为指定将输入文件拆分成几页独立pdf,可实现页的合并(例如源文件有10页 指定 -n 5 则将输出5个pdf 每个pdf包含原来的两页,且两页合成了一页,中间没有分页符号 )")
        parser.add_option("-s", "--startpage", type="int",dest="startpage",default=0, help="\n\
起始页码,取值 1,2,3,...,n, 对拆分指源文件内的页码,对合并指-i <dir> 内的 *.pdf 注意 合并时 0.pdf 算做 -s 1 ,以此类推")
        parser.add_option("-e", "--endpage", type="int", dest="endpage",default=0, help="\n\
终止页码,拆分或合并区别同上")
        parser.add_option("-m", "--merge", type="int", dest="ismerge",default=0, help="\n\
指定功能为合并(merge) 使用时为 -m 1")
        parser.add_option("-u", "--cut-up", type="int", dest="up",default=0, help="\n\
cut 掉源pdf页内上边距, 仅在拆分pdf 且 -n 不指定 或指定为源pdf内置页数时有效,默认为0")
        parser.add_option("-d", "--cut-down", type="int", dest="down",default=0, help="\ncut 下边距,详细同上")
        parser.add_option("-l", "--cut-left", type="int", dest="left",default=0, help="\ncut 左边距,详细同上")
        parser.add_option("-r", "--cut-right", type="int", dest="right",default=0, help="\ncut 右边距,详细同上")        
        #解析参数
        self.options, self.args = parser.parse_args()
        if self.options.infile=="None":
            print('Please input pdf file name')
            sys.exit()

if __name__=='__main__':
    opt=script_opt()
    foo=pdfSpliter(opt.options.infile,
                   opt.options.outpath,
                   opt.options.outfilenum,
                   opt.options.startpage,
                   opt.options.endpage,
                   {'t':opt.options.up,
                    'b':opt.options.down,
                    'l':opt.options.left,
                    'r':opt.options.right
                   },opt.options.ismerge)
    foo.execute()
