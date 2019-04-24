# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 09:35:13 2018

@author: Thomas Tessier
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas
import math
from mailmerge import MailMerge
import pyproj



def clean(line):
    '''
    takes in a list of strings.
    Outputs an identical list with all instances of '' removed.
    '''
    result=[]
    for e in line:
        if e != '':
            result.append(e)
    return result

def prepare(file):
    '''
    Takes an FAA file and makes the necessary preparations
    Returns a list. Each element is a list of one line in file.
    Each element list is the text elements of each line
    '''
    filestring=file.read()
    filechars=list(filestring)
    for i in range(len(filechars)):
        if filechars[i]=='\t':
            filechars[i]=' '
    filestring=''.join(filechars)
    filelines=filestring.split('\n')
    splitlines=[]
    i=0
    for line in filelines:
        splitlines.append(line.split(' '))
        splitlines[i]=clean(splitlines[i])
        i += 1
    return(splitlines)    


def extract(splitlines,Callsign,Time):
    '''
    extract the needed info from a prepared splitlines and creates MOM Input
    Returns dictionaries of info needed for the merge
    '''
    '''
    Frequency and AM Class
    '''
    i=0
    for line in splitlines:
        if line !=[] and line[0]=='Licensee:':
            Point=i
            break
        i += 1
    Frequency=splitlines[Point+2][0]
    AMClass=splitlines[Point+3][3]
    if AMClass=='A':
        AMNum='1'
    elif AMClass=='B':
        AMNum='2'
    elif AMClass=='C':
        AMNum='3'
    elif AMClass=='D':
        AMNum='4'
    i=0
    
    '''
    Latitude, Longitude and Power
    '''
    for line in splitlines:
        if line != [] and 'Latitude' in line:
            Point=i
            break
        i += 1
    i=0
    for e in splitlines[Point]:
        if e =='Power:':
            Pos=i
            break
        i+=1
    Lat=float(splitlines[Point][Pos-1])
    LatD=int(Lat)
    LatM=int((Lat-LatD)*60)
    LatS=round((Lat-LatD-(LatM/60))*3600)
    Power=splitlines[Point][Pos+1]
    Long=float(splitlines[Point+1][-1])
    LongD=int(-1*Long)
    LongM=int(((-1*Long)-LongD)*60)
    LongS=round(((-1*Long)-LongD-(LongM/60))*3600)    
    
    '''
    Prepare NAD 83 coordinates
    '''
    NAD27=pyproj.Proj(init='epsg:26715')
    NAD83=pyproj.Proj(init='epsg:26915')
    x1,y1=NAD27(Long,Lat)
    x2,y2=pyproj.transform(NAD27,NAD83,x1,y1)
    ConLong,ConLat=NAD83(x2,y2,inverse=True)
    ConLatD=int(ConLat)
    ConLatM=int((ConLat-ConLatD)*60)
    ConLatS=round((ConLat-ConLatD-(ConLatM/60))*3600,2)
    ConLongD=int(-1*ConLong)
    ConLongM=int(((-1*ConLong)-ConLongD)*60)
    ConLongS=round(((-1*ConLong)-ConLongD-(ConLongM/60))*3600,2)    

    
    '''
    Number of towers, RMS, and the tower table
    '''
    i=0
    for line in splitlines:
        if line != [] and line[0]=='Tower' and line[1]=='information:':
            Point=i
            break
        i += 1
    NumTowers=splitlines[Point-2][0]
    RMSTheo=splitlines[Point-7][2]
    i=Point+11
    x=0
    towerinfo=[]
    while splitlines[i] != []:
        towerinfo.append(splitlines[i][1:])
        print(towerinfo[x])
        del towerinfo[x][5]
        if len(towerinfo[x][-1])==7:
            towerinfo[x]=towerinfo[x][:-1]
        x += 1
        i += 1
    
    '''
    ERSS, K, Q
    '''
    i=0
    for line in splitlines:
        if line != [] and line[0]=='Erss':
            Point=i
            break
        i += 1    
    ErssNum=splitlines[Point][2]
    KFactor=splitlines[Point+1][2]
    QFactor=splitlines[Point+1][5]
    
    '''
    Augmentations
    '''
    i=0
    for line in splitlines:
        if line != [] and line[0]=='Number':
            Point=i
            break
        i += 1    
    NumAug=splitlines[Point][-1]
    AugLines=[]
    if NumAug != '0':
        i=Point+9
        while splitlines[i] != []:
            AugLines.append(splitlines[i])
            i += 1
        for line in AugLines:
            line[1]=line[1][:-1]
            line[2]=line[2][:-1]
    
    '''
    Calculate Shortest tower
    '''
    Shortest=9999
    for line in towerinfo:
        if float(line[4]) < Shortest:
            Shortest=float(line[4])
   
    '''
    Build the Input files
    '''
    titleline=' '.join([NumTowers,RMSTheo,QFactor,AMNum,NumAug,ErssNum,str(Shortest),KFactor,Power,str(LatD),str(LatM),str(LatS),str(LongD),str(LongM),str(LongS)])
    filename='.\\MOM Inputs\\'+Callsign+' '+Time+' Base.DAD'
    file=open(filename,'w')
    file.write(titleline+'\n')
    for i in towerinfo:
        file.write(' '.join(i)+'\n')
    for i in AugLines:
        file.write(' '.join(i)+'\n')
    file.write(Frequency)
    file.close()
    
    '''
    Build and return the dictionary
    '''
    Output={}
    if Time=='Daytime':
        timevar='Day'
    elif Time=='Nightime':
        timevar='Night'
    
    Output['Frequency']=Frequency
    Output['LatD']=str(LatD)
    Output['LatM']=str(LatM)
    Output['LatS']=str(round(float(LatS),2))
    Output['LongD']=str(LongD)
    Output['LongM']=str(LongM)
    Output['LongS']=str(round(float(LongS),2))
    Output['ConLatD']=str(ConLatD)
    Output['ConLatM']=str(ConLatM)
    Output['ConLatS']=str(round(float(ConLatS),2))
    Output['ConLongD']=str(ConLongD)
    Output['ConLongM']=str(ConLongM)
    Output['ConLongS']=str(round(float(ConLongS),2))
    Output[timevar+'Power']=Power
    Output[timevar+'RMS']=RMSTheo
    Output[timevar+'K']=KFactor
    Output[timevar+'Q']=QFactor
    Output['Wavelength']=str(round(300000/float(Frequency),2))
    TowerDicts=[]
    i=0
    for line in towerinfo:
        print(line)
        TowerDicts.append({})
        TowerDicts[i][timevar+'TowInd']=str(i+1)
        TowerDicts[i][timevar+'TowFR']=line[0]
        TowerDicts[i][timevar+'TowPhase']=line[1]
        TowerDicts[i][timevar+'TowSpace']=line[2]
        TowerDicts[i][timevar+'TowBear']=line[3]
        TowerDicts[i][timevar+'TowHt']=line[4]
        TowerDicts[i][timevar+'TowA']=line[5]
        TowerDicts[i][timevar+'TowB']=line[6]       
        TowerDicts[i][timevar+'TowC']=line[7]
        print(TowerDicts)
        TowerDicts[i][timevar+'TowD']=line[8]
        i += 1
        
    return Output, TowerDicts


def toweradd(filename, Feet,Dist,Bear, timevar):
    '''
    Adds the tower to the MOM Input file
    Outputs the Dictionary with the proposed tower info
    '''
    file=open(filename)
    filelines=file.readlines()
    file.close()
    splitlines=[]
    for line in filelines:
        splitlines.append(line.split(' '))
    Frequency=float(splitlines[-1][-1])
    Spacing=round(1000*Dist*360/(300000/Frequency),2)
    ElecHt=round((Feet*0.3048)*360/(300000/Frequency),2)
    Bear=round(Bear,1)
    TowerLine=['0','0',str(Spacing),str(Bear),str(ElecHt),'0','0','0','0\n']
    TowerDict={}
    TowerDict[timevar+'TowFRP']=TowerLine[0]
    TowerDict[timevar+'TowPhaseP']=TowerLine[1]
    TowerDict[timevar+'TowSpaceP']=TowerLine[2]
    TowerDict[timevar+'TowBearP']=TowerLine[3]
    TowerDict[timevar+'TowHtP']=TowerLine[4]
    TowerDict[timevar+'TowAP']=TowerLine[5]
    TowerDict[timevar+'TowBP']=TowerLine[6]       
    TowerDict[timevar+'TowCP']=TowerLine[7]
    TowerDict[timevar+'TowDP']=TowerLine[8][0]
    
    if float(splitlines[0][6])>ElecHt:
        splitlines[0][6]=str(ElecHt)
    splitlines[0][0]=str(int(splitlines[0][0])+1)
    splitlines.append([])
    for i in range(len(splitlines)-1,-1,-1):
        splitlines[i]=splitlines[i-1]
        if len(splitlines[i])>4:
            target=i
            break
    splitlines[target]=TowerLine
    resultname=filename[:-8]+'Tower.DAD'
    result=open(resultname,'w')
    for line in splitlines:
        result.write(' '.join(line))
    return TowerDict



def dataextract(filename):
    '''
    Generate the angles and extract values from the MOM output file
    Returns a tuple of two arrays, one for angles and one for values
    '''
    file=open(filename,'r')
    filelines=file.readlines()
    file.close()
    for i in range(len(filelines)):
        if filelines[i]=='Angle      Angle     Mag(mV/m)  Phase(Deg)\n':
            zero=i+1
    angles=np.arange(0,2*np.pi,(5*np.pi/180))
    values=[]
    for i in range(zero,zero+360,5):
        dataline=clean(filelines[i].split(' '))
        values.append(dataline[2])
    values=np.asarray(values, dtype='float32')
    return [angles,values]




def faaextract(filename):
    '''
    Extarcts the values from the FAA record copied from online
    Returns a tuple of two arrays, the theoretical values, and the standard values
    '''
    Augmented=False
    file=open(filename,'r')
    filelines=file.readlines()
    file.close()
    for i in range(len(filelines)):
        brokeline=filelines[i].split(' ')
        brokeline=clean(brokeline)
        if brokeline[0]=='Azimuth' and brokeline[1]=='Etheoretical' and brokeline[3]=='Eaugmented':
            zero=i+3
            Augmented=True
            break
        elif brokeline[0]=='Azimuth' and brokeline[1]=='Etheoretical' and not brokeline[3]=='EAugmented':
            zero=i+3
            break
    theovalues=[]
    stanvalues=[]
    augvalues=[]
    
    if Augmented:
        for i in range(zero,zero+36):
            dataline=clean(filelines[i].split(' '))
            theovalues.append(dataline[1])
            stanvalues.append(dataline[2])
            augvalues.append(dataline[3])
            if i==zero:
                if augvalues[-1]=='180.0':
                    augvalues[-1]=''
        for i in range(zero,zero+36):
            dataline=clean(filelines[i].split(' '))
            theovalues.append(dataline[-3])
            stanvalues.append(dataline[-2])
            augvalues.append(dataline[-1])
    else:
        for i in range(zero,zero+36):
            dataline=clean(filelines[i].split(' '))
            theovalues.append(dataline[1])
            stanvalues.append(dataline[2])
        for i in range(zero,zero+36):
            dataline=clean(filelines[i].split(' '))
            theovalues.append(dataline[4])
            stanvalues.append(dataline[5])    
            
    theovalues=np.asarray(theovalues, dtype='float32')
    stanvalues=np.asarray(stanvalues, dtype='float32')
    if augvalues != []:
        if augvalues[0]=='':
            augvalues[0]=augvalues[1]
        augvalues=np.asarray(augvalues, dtype='float32')        
    if Augmented:
        return [theovalues,stanvalues,augvalues]
    else:
        return [theovalues,stanvalues,stanvalues]



def plotgen(Callsign,Time):
    basepoints=dataextract('.\\MOM Outputs\\'+Callsign+' '+Time+' Base-MN.txt')
    basepoints[0]=np.append(basepoints[0],[0])
    basepoints[1]=np.append(basepoints[1],[basepoints[1][0]])
    towerpoints=dataextract('.\\MOM Outputs\\'+Callsign+' '+Time+' Tower-MN.txt')
    towerpoints[0]=np.append(towerpoints[0],[0])
    towerpoints[1]=np.append(towerpoints[1],[towerpoints[1][0]])
    faavalues=faaextract('.\\FAA Files\\'+Callsign+' '+Time+' FAA.txt')
    faavalues[0]=np.append(faavalues[0],[faavalues[0][0]])
    faavalues[1]=np.append(faavalues[1],faavalues[1][0])
    faavalues[2]=np.append(faavalues[2],faavalues[2][0])
    faaangles=np.arange(0,2*np.pi,(5*np.pi/180))
    faaangles=np.append(faaangles,[0])
    faatheopoints=(faaangles,faavalues[0])
    faastanpoints=(faaangles,faavalues[1])
    faaaugpoints=(faaangles,faavalues[2])
    ratios=towerpoints[1]/basepoints[1]
    resultpoints=(faaangles,ratios*faatheopoints[1])
    plt.figure(figsize=(5,6), dpi=80)
    ax=plt.axes(polar=True)
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    line1,=ax.plot(resultpoints[0],resultpoints[1])
    line2,=ax.plot(faastanpoints[0],faastanpoints[1])
    plt.legend(['Theoretical w/Tower (mV/m)','Standard (mV/m)'], bbox_to_anchor=(0.5,-0.1))
    ax.set_title(Callsign+' '+Time)
    plt.savefig('.\\Plots\\'+Callsign+' '+Time+'.png')
    plt.clf()
    plt.cla()
    plt.figure(figsize=(5,6), dpi=80)
    ax=plt.axes(polar=True)
    
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    line1,=ax.plot(resultpoints[0],resultpoints[1])
    line2,=ax.plot(faaaugpoints[0],faaaugpoints[1])
    plt.legend(['Theoretical w/Tower (mV/m)','Augmented (mV/m)'], bbox_to_anchor=(0.5,-0.1))
    ax.set_title(Callsign+' '+Time)
    plt.savefig('.\\Plots\\'+Callsign+' Augmented '+Time+'.png')
    plt.clf()
    plt.cla()
    return ".\\Plots\\"+Callsign+' '+Time+'.png'



def buildTable(Callsign,Time):
    if Time=='Daytime':
        timevar='Day'
    else:
        timevar='Night'
    cols=['Azimuth (deg)', 'Control Pattern RMS (mV/m)', 'Pattern with Tower RMS (mV/m)','Ratio', 'Theoretical Pattern RMS (mV/m)', 'Adjusted Theoretical Pattern RMS (mV/m)', 'Standard Pattern RMS (mV/m)', 'Difference (mV/m)', 'Difference (dB)']
    fields=[timevar+'Azimuth',timevar+'ControlRMS',timevar+'TowerRMS',timevar+'Ratio',timevar+'Theoretical',timevar+'Adjusted',timevar+'Standard',timevar+'Difference',timevar+'DifferencedB']
    mergerows=[]
    basepoints=dataextract('.\\MOM Outputs\\'+Callsign+' '+Time+' Base-MN.txt')
    towerpoints=dataextract('.\\MOM Outputs\\'+Callsign+' '+Time+' Tower-MN.txt')
    faavalues=faaextract('.\\FAA Files\\'+Callsign+' '+Time+' FAA.txt')
    faaangles=np.arange(0,2*np.pi,(5*np.pi/180))
    faatheopoints=(faaangles,faavalues[0])
    faastanpoints=(faaangles,faavalues[1])
    faaaugpoints=(faaangles,faavalues[2])
    ratios=towerpoints[1]/basepoints[1]
    resultpoints=(faaangles,ratios*faatheopoints[1])
    for i in range(72):
        mergerows.append({})
    dataset=[]
    for i in range(len(faaangles)):
        dataset.append([5*i,basepoints[1][i],towerpoints[1][i],ratios[i],faatheopoints[1][i],resultpoints[1][i],faastanpoints[1][i],resultpoints[1][i]-faastanpoints[1][i],20*math.log10(resultpoints[1][i]/faastanpoints[1][i])])
    df=pandas.DataFrame(data=dataset, columns=cols)
    maximum=df['Difference (mV/m)'].max()
    maximumdb=df.values[df['Difference (mV/m)'].idxmax(),8]
    for i in range(72):
        for j in range(9):
            mergerows[i][fields[j]]=str(round(df.values[i,j],3))
    return mergerows,str(round(maximum,2)),str(round(maximumdb,2))
    






    
mergeDict={}
print('The filenames should be <Callsign> Daytime FAA and <Callsign> Nightime FAA')
Callsign=input('Define the callsign: ')
mergeDict['Callsign']=Callsign
if os.path.exists('.\\FAA Files\\'+Callsign+' Daytime FAA.txt') and os.path.exists('.\\FAA Files\\'+Callsign+' Nightime FAA.txt'):
    running=input('Excellent. Am I running 1 - Day    2 - Night   3 - Both  :')
    print('Great. Now for the new tower info.')
    TowerFeet=float(input('How tall is the tower in feet?  :'))
    mergeDict['TowerHt']=str(TowerFeet*0.3048)

    print('I need the NAD 83 Lat and Long of the Proposed tower.')
    print('Input the coordinates as DMS, with a space in between degrees, minutes, and seconds. No symbols are needed.')
    TowLat=input('Latitude of the proposed tower :')
    TowLong=input('Longitude of the proposed tower :')
    TowLatSplit=TowLat.split(' ')
    mergeDict['TowerLatD']=TowLatSplit[0]
    mergeDict['TowerLatM']=TowLatSplit[1]
    mergeDict['TowerLatS']=TowLatSplit[2]
    TowLongSplit=TowLong.split(' ')
    mergeDict['TowerLongD']=TowLongSplit[0]
    mergeDict['TowerLongM']=TowLongSplit[1]
    mergeDict['TowerLongS']=TowLongSplit[2]



else:
    print('Files not found!')
    print('Be sure that both day and night files are present.')
    input('Press enter to end.')
    sys.exit()
    
if running=='1':
    mergeDict['DayNight']='Daytime'
elif running =='2':
    mergeDict['DayNight']='Nightime'
else:
    mergeDict['DayNight']='Both'


if running =='1' or running == '3':
    DayFile=open('.\\FAA Files\\'+Callsign+' Daytime FAA.txt','r')
    DayLines=prepare(DayFile)
    DayFile.close()
    DayDict, DayTowerDicts=extract(DayLines,Callsign,'Daytime')

    AMLat=float(DayDict['ConLatD'])+(float(DayDict['ConLatM'])/60)+(float(DayDict['ConLatS'])/3600)
    AMLong=-1*(float(DayDict['ConLongD'])+(float(DayDict['ConLongM'])/60)+(float(DayDict['ConLongS'])/3600))
    TowLat=float(mergeDict['TowerLatD'])+(float(mergeDict['TowerLatM'])/60)+(float(mergeDict['TowerLatS'])/3600)
    TowLong=-1*(float(mergeDict['TowerLongD'])+(float(mergeDict['TowerLongM'])/60)+(float(mergeDict['TowerLongS'])/3600))
    
    g=pyproj.Geod(ellps='GRS80')
    TowerBear,ignore,TowerDist=g.inv(AMLong,AMLat,TowLong,TowLat)
    TowerDist=TowerDist/1000
    if TowerBear<0:
        TowerBear=TowerBear+360
    DayPropDict=toweradd('.\\MOM Inputs\\'+Callsign+' Daytime Base.DAD',TowerFeet,TowerDist,TowerBear,'Day')
    DayPropDict['DayTowIndP']=str(len(DayTowerDicts)+1)
if running == '2' or running == '3':
    NightFile=open('.\\FAA Files\\'+Callsign+' Nightime FAA.txt', 'r')
    NightLines=prepare(NightFile)
    NightFile.close()
    NightDict, NightTowerDicts=extract(NightLines,Callsign,'Nightime')

    AMLat=float(NightDict['ConLatD'])+(float(NightDict['ConLatM'])/60)+(float(NightDict['ConLatS'])/3600)
    AMLong=-1*(float(NightDict['ConLongD'])+(float(NightDict['ConLongM'])/60)+(float(NightDict['ConLongS'])/3600))
    TowLat=float(mergeDict['TowerLatD'])+(float(mergeDict['TowerLatM'])/60)+(float(mergeDict['TowerLatS'])/3600)
    TowLong=-1*(float(mergeDict['TowerLongD'])+(float(mergeDict['TowerLongM'])/60)+(float(mergeDict['TowerLongS'])/3600))
    
    g=pyproj.Geod(ellps='GRS80')
    TowerBear,ignore,TowerDist=g.inv(AMLong,AMLat,TowLong,TowLat)
    TowerDist=TowerDist/1000
    if TowerBear<0:
        TowerBear=TowerBear+360
    NightPropDict=toweradd('.\\MOM Inputs\\'+Callsign+' Nightime Base.DAD',TowerFeet,TowerDist,TowerBear,'Night')
    NightPropDict['NightTowIndP']=str(len(NightTowerDicts)+1)

mergeDict['TowerBear']=str(round(TowerBear,1))
mergeDict['TowerDist']=str(round(TowerDist,3))
print('All done. The files for MOM input are in the MOM Input folder.')
print('Now I need some information for the report itself.')
mergeDict['SiteName']=input('What\'s the name of the site?  :')
mergeDict['Customer']=input('Who\'s the customer?  :')




input('Perfect. Now, all of the MOM Output files need to be in the MOM Outputs folder. As soon as you\'re ready, hit enter.')




if running=='1' or running=='3':
    plotpath=plotgen(Callsign,'Daytime')
    mergeDict['DayPolar']=os.path.abspath(plotpath)
    DayTable,mergeDict['DayMax'],mergeDict['DayMaxDB']=buildTable(Callsign,'Daytime')
    file=open('.\\MOM Outputs\\'+Callsign+' Daytime Base-MN.txt','r')
    mergeDict['DayBase']=file.read()
    file.close()
    file=open('.\\MOM Outputs\\'+Callsign+' Daytime Tower-MN.txt','r')
    mergeDict['DayTower']=file.read()
    file.close()
if running =='2' or running=='3':
    plotpath=plotgen(Callsign,'Nightime')
    mergeDict['NightPolar']=os.path.abspath(plotpath)
    NightTable,mergeDict['NightMax'],mergeDict['NightMaxDB']=buildTable(Callsign,'Nightime')
    file=open('.\\MOM Outputs\\'+Callsign+' Nightime Base-MN.txt','r')
    mergeDict['NightBase']=file.read()
    file.close()
    file=open('.\\MOM Outputs\\'+Callsign+' Nightime Tower-MN.txt','r')
    mergeDict['NightTower']=file.read()
    file.close()        


if running=='3':
    if float(mergeDict['DayMax'])>0 or float(mergeDict['NightMax'])>0:
        mergeDict['Disturbance']='disturbances'
    else:
        mergeDict['Disturbance']='no disturbances'
elif running=='1':
    if float(mergeDict['DayMax'])>0:
        mergeDict['Disturbance']='disturbances'
    else:
        mergeDict['Disturbance']='no disturbances'
elif running=='2':
    if float(mergeDict['NightMax'])>0:
        mergeDict['Disturbance']='disturbances'
    else:
        mergeDict['Disturbance']='no disturbances'

    
template='.\\Report Template\\Python MOM Template.docx'
document=MailMerge(template)
if running=='1' or running=='3':
    document.merge_rows('DayTowInd',DayTowerDicts)
    document.merge_rows('DayTowInd',DayTowerDicts)
    document.merge_rows('DayTowIndP',[DayPropDict])
    document.merge_rows('DayAzimuth',DayTable)
    Final={**mergeDict,**DayDict}
    document.merge(**Final)
if running=='2' or running=='3':
    document.merge_rows('NightTowInd',NightTowerDicts)
    document.merge_rows('NightTowInd',NightTowerDicts)
    document.merge_rows('NightTowIndP',[NightPropDict])
    document.merge_rows('NightAzimuth',NightTable)
    Final={**mergeDict,**NightDict}
    document.merge(**Final)

document.write('.\\Report Outputs\\'+Callsign+' MOM Report.docx')
document.close()
print('Done! The report is in the Output folder.')
input('Press Enter to conclude...')
