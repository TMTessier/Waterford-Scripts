# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 15:12:44 2018

@author: Thomas Tessier
"""
import os
validchars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz !"#$%&\'()*+,-./0123456789:;<=>?@[]\^_`{}|~\n'

goodrows=['NAME','MAKE','FREQUENCY','H_WIDTH','V_WIDTH','FRONT_TO_BACK','GAIN','TILT','POLARIZATION','COMMENTS','HORIZONTAL']
for x in range(360):
    goodrows.append(str(x))
goodrows.append('VERTICAL')
for x in range(360):
    goodrows.append(str(x))

def folderclean(string):
    for entry in os.listdir():
        if os.path.isdir(entry):
            os.chdir(entry)
            print('Current dir: ' + os.getcwd())
            folderclean(entry)
        else:
            if entry.endswith('.pln') or entry.endswith('.txt'):
                file=open(entry,'r')
                filestr=file.read()
                file.seek(0)
                filelines=file.readlines()
                file.close()
                filelist=list(filestr)
                for char in range(len(filelist)):
                    filelist[char]=filelist[char].upper()
                    if filelist[char]=='\r':
                        filelist[char]='\n'                            
                    if filelist[char]=='\t':
                        filelist[char]=' '
                    if filelist[char] not in validchars:
                        filelist[char]=''
                newfilestr=''.join(filelist)
                newfilestr=newfilestr.upper()
                newfilename=open(entry[:-4]+'.adj','w')
                newfilename.write(newfilestr)
                newfilename.close()
                file=open(entry[:-4]+'.adj','r')
                filelines=file.readlines()
                file.close()
                diagnosis.write(entry[:-4]+' has been scrubbed.\n')
                splitlines=[]
                for line in filelines:
                    splitlines.append(line.split(' '))
                checking=[]
                for line in splitlines:
                    checking.append(line[0])
                if checking==goodrows:
                    diagnosis.write('Parameters all present and accounted for.\n')
                else:
                    try:
                        file=open(entry[:-4]+'.tmp','w')
                        diagnosis.write('Parameter missing or out of order. Reordering and adding missing parameters.\n')
                        for line in goodrows[0:11]:
                            wrote=False
                            for i in range(11):
                                if splitlines[i][0]==line:
                                    file.write(' '.join(splitlines[i]))
                                    wrote=True
                                    splitlines[i]=['']
                                    break
                                if not wrote:
                                    file.write(line+'\n')
                        for line in splitlines:
                            if line != [''] and line[0] in goodrows:
                                file.write(' '.join(line))
                        file.close()
                        os.remove(entry[:-4]+'.adj')
                        os.rename(entry[:-4]+'.tmp', entry[:-4]+'.adj')
                        file=open(entry[:-4]+'.adj', 'r')
                        filelines=file.readlines()
                        file.close()
                    except:
                        diagnosis.write(entry[:-4]+' is messed up, I don\'t know what to do with it.')
                        continue
                splitlines=[]
                for line in filelines:
                    splitlines.append(line.split(' '))
                for i in range(len(splitlines)):
                    if (len(splitlines[i]) < 2) or (len(splitlines[i])==2 and splitlines[i][-1]=='\n'):
                        if splitlines[i][0].endswith('\n'):
                            diagnosis.write('Missing Information - '+splitlines[i][0])
                        else:
                            diagnosis.write('Missing Information - '+splitlines[i][0]+'\n')
                file.close()
                diagnosis.write('\n')
    os.chdir('..')
           











start=os.getcwd()
diagnosis=open('diagnosis.txt','w')
folderclean(start)
diagnosis.close() 