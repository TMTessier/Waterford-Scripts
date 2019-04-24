# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 16:23:26 2018

@author: Thomas Muse-Tessier

The purpose of this script is to combine three previously separate database queries and actions into a single, "One Stop Shop." 
1 - Construct a locally saved subset of the online FCC database, focusing on the information needed to identify which cell carriers
    are licensed to operate in which frequency blocks for a given county and state in the United States
  - Perform searches of a county and state, returning all cell carrier licenses for that county and state bsaed on the above data and
    export the information to a .csv
2 - Construct a locally saved subset of the online FCC database, focusing on the information needed to identify microwave antennas and
    omni/whip antennas and their geographical location
  - Perform searches of the above data, returning the microwave and omni antennas within a given radius of a geographical point.
3 - Construct a locally saved subset of the online FCC database, focusing on identifying information for FM, AM and TV antennas
  - Perform searches of the above data, returning the FM, AM and TV antennas within a given radius of a provided geographical point
"""

import tkinter as tk
import pandas
import os
import wget
from zipfile import ZipFile
import datetime
pandas.options.mode.chained_assignment=None




class DBT:


    def LicenseDataBuild(frame):
        '''
        Build the database used to perform Radio Block Search
        '''
        Show(frame,'This is a long process, buckle up.\nDownloading the datafiles')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_cell.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_market.zip')
        Show(frame,'Extracting the files')
        with ZipFile('l_cell.zip', 'r') as zip:
            zip.extract('HD.dat', 'cell')
            zip.extract('MK.dat','cell')
            zip.extract('EN.dat','cell')
        with ZipFile('l_market.zip','r') as zip:
            zip.extract('HD.dat','market')
            zip.extract('MK.dat','market')
            zip.extract('MP.dat','market')
            zip.extract('EN.dat','market')
        os.chdir('cell')
        with open('HD.dat') as file:
            HDCellString=file.read()
        with open('MK.dat') as file:
            MKCellString=file.read()
        with open('EN.dat') as file:
            ENCellString=file.read()
        os.chdir('..//market')
        with open('HD.dat','a') as file:
            file.write(HDCellString)
        with open('MK.dat','a') as file:
            file.write(MKCellString)
        with open('EN.dat','a') as file:
            file.write(ENCellString)
        del(HDCellString)
        del(MKCellString)
        del(ENCellString)
        Show(frame,'Preparing and cleaning up data')
        doc=open('HD.dat','r')
        text=list(doc.read())
        doc.close()
        for i in range(len(text)):
            if text[i]=='"':
                text[i]=''
        text=''.join(text)
        newdoc=open('HD new.DAT','w')
        newdoc.write(text)
        newdoc.close()
        os.remove('HD.dat')
        os.rename('HD new.dat','HD.dat')
        doc=open('MP.dat','r')
        lines=doc.readlines()
        splitlines=[]
        for line in lines:
            splitlines.append(line.split('|'))
        i=0
        while i < len(splitlines):
            if len(splitlines[i])<14:
                splitlines[i][-1]=splitlines[i][-1][:-1]   
                splitlines[i]=splitlines[i]+splitlines[i+1]
                del(splitlines[i+1])
                i-=1
            i+=1
        for line in splitlines:
            if line[6]=='':
                line[6]=' '
        for i in range(len(splitlines)):
            splitlines[i]='|'.join(splitlines[i])
        text='\n'.join(splitlines)
        newfile=open('MP new.dat','w')
        newfile.write(text)
        newfile.close()
        doc.close()
        os.remove('MP.dat')
        os.rename('MP new.dat','MP.dat')
        Show(frame,'Reading the data')
        ValidRadios=['AD','AH','AT','AW','CL','CW','CY','WS','WU','WY','WZ']
        Output=pandas.DataFrame(columns=['County','State','USI','Callsign','Entity Name','Radio Code', 'Channel Block','Frequency'])
        CodeList=pandas.read_csv('..//Radio Blocks//County and Market Codes.csv', sep=',', encoding='cp1252')
        FindUSI=pandas.read_csv('MK.dat', sep='|', encoding='cp1252', header=None, names=['Record Type','USI','ULS File','EBF Number','Callsign','Market Code','Channel Block','Submarket Code','Market Name','Coverage Partitioning','Coverage Dissagregation','Cellular Phase ID','Population','Tribal Credit Indicator','Tribal Credit Calculation','Additional Credit Requested','Tribal Credit Awarded','Additional Credit Awarded','BC PCT','Open Closed Bidding','Bidding Credit Type','Claiming Unserved Area'], dtype={'USI':str,'ULS File':str})
        FindCodes=pandas.read_csv('HD.dat', index_col=False, engine='python', sep='|', encoding='cp1252', header=None, names=['Record Type','USI','ULS File','EBF Number','Callsign','License Status','Radio Service Code','Grant Date','Expired Date','Cancellation Date','Eligibility Rule Num','Applicant Type','Alien','Alien Govt','Alien Corp','Alien Officer','Alien Control','Revoked','Convicted','Adjudged','Involved Reserved','Common Carrier','Non Common Carrier','Private Comm','Fixed','Mobile','Radio Location','Satellite','Developmental or STA','Interconnected Service','Certifier First Name','Certifier MI','Certifier Last Name','Certifier Suffix','Certifier Title','Gender','African American','Native American','Hawaiian','Asian','White','Ethnicity','Effective Date','Last Action Date','Auction ID','Reg Stat Broad Serv','Band Manager','Type Serv Broad Serv','Alien Ruling','Licensee Name Change'], dtype={'USI':str})
        CheckPartition=pandas.read_csv('MP.dat', index_col=False, engine='python', sep='|', encoding='cp1252', header=None, names=['Record Type','USI','ULS File','EBF Number','Callsign','Market Partition Code','Defined Area','Defined Population','Include Exclude','Partitioned ID','Action performed','Census','Def Undef','Partition Sequence'], dtype={'USI':str})
        FindEntity=pandas.read_csv('EN.dat', index_col=False, engine='python', sep='|', encoding='cp1252', header=None, names=['Record Type','USI','ULS File','EBF Number','Callsign','Entity Type','Licensee ID','Entity Name','First Name','MI','Last Name','Suffix','Phone','Fax','Email','Street Address','City','State','Zip Code','PO Box','Attention Line','SGIN','FRN','Applicant Type Code','Applicant Type Code Other','Status Code','Status Date'],dtype={'USI':str})
        ValidRadios=['AD','AH','AT','AW','CL','CW','CY','WS','WU','WY','WZ']
        i=0
        Show(frame,'Beginning to go through the counties')
        for begin in CodeList.index:    
            FinalData=pandas.DataFrame(columns=['USI','Callsign','Entity Name','Radio Code', 'Channel Block'])
            County=CodeList.loc[begin,'COUNTY']
            State=CodeList.loc[begin,'STATE']
            MarketLine=CodeList.loc[(CodeList['COUNTY']==County) & (CodeList['STATE']==State)].values.tolist()[0]
            FIPS=str(MarketLine[1])
            MarketCodes=MarketLine[-12:]
            USIFrame=FindUSI[FindUSI['Market Code'].isin(MarketCodes)]
            USIList=USIFrame['USI'].tolist()
            CodeFrame=FindCodes[(FindCodes['USI'].isin(USIList)) & (FindCodes['Radio Service Code'].isin(ValidRadios)) & (FindCodes['License Status'] == 'A') & ~(FindCodes['Callsign'].str.startswith('L'))]
            FinalData['USI']=CodeFrame['USI'].tolist()
            FinalData['Callsign']=CodeFrame['Callsign'].tolist()
            FinalData['Radio Code']=CodeFrame['Radio Service Code'].tolist()
            checklist=FinalData.index
            for index in checklist:
                test2=CheckPartition[CheckPartition['USI'] == FinalData.loc[index,'USI']]
                if test2.empty:
                    continue
                test1=test2[test2['Defined Area'].str.contains(FIPS)]
                if test1.empty:
                    partlist=test2['Market Partition Code'].tolist()
                    Remove=True
                    BasicList=[MarketCodes[2],MarketCodes[7]]
                    for each in partlist:
                        if each in BasicList:
                            Remove=False
                            break
                    if Remove:
                        FinalData=FinalData.drop(index)
            EntityFrame=FindEntity[FindEntity['USI'].isin(FinalData['USI'])]
            ChannelFrame=FindUSI[FindUSI['USI'].isin(FinalData['USI'])]
            checklist=FinalData.index
            for index in checklist:
                FinalData.loc[index,'Channel Block'] = ChannelFrame[ChannelFrame['USI']==FinalData.loc[index,'USI']].values.tolist()[0][6]
                FinalData.loc[index,'Entity Name']= EntityFrame[(EntityFrame['USI']==FinalData.loc[index,'USI']) & (EntityFrame['Entity Type'] == 'L')].values.tolist()[0][7]
            for index in checklist:
                Output.loc[i,'County']=County
                Output.loc[i,'State']=State
                Output.loc[i,'USI']=FinalData.loc[index,'USI']
                Output.loc[i,'Callsign']=FinalData.loc[index,'Callsign']
                Output.loc[i,'Entity Name']=FinalData.loc[index,'Entity Name']
                Output.loc[i,'Radio Code']=FinalData.loc[index,'Radio Code']
                Output.loc[i,'Channel Block']=FinalData.loc[index,'Channel Block']
                i += 1
            del(FinalData)
            Show(frame,County+' '+State+' done')
        Show(frame,'Cleaning up')
        os.chdir('..')
        #Output.to_csv('Radio Blocks//License Output.csv', index=False)
        os.remove('l_cell.zip')
        os.remove('l_market.zip')
        os.chdir('cell')
        for file in os.listdir():
            os.remove(file)
        os.chdir('..//market')
        for file in os.listdir():
            os.remove(file)
        os.chdir('..')
        os.rmdir('cell')
        os.rmdir('market')
        timecode=datetime.datetime.now().strftime("%m-%d-%Y")
        with open('buildDate.txt','r') as file:
            dates=file.readlines()
        dates[0]=timecode+'\n'
        write=''.join(dates)
        with open('buildDate.txt','w') as file:
            file.write(write)
        
    
    
    
    
    
    
    def MicroDataBuild(frame):
        '''
        Build the database needed for the microwave/omni search
        '''
        Show(frame,'Downloading the data files')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_LMpriv.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_micro.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_LMcomm.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_paging.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_coast.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_LMbcast.zip')
        wget.download('http://wireless.fcc.gov/uls/data/complete/l_mdsitfs.zip')
        Show(frame,'Extracting the data')
        with ZipFile('l_LMpriv.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//LMpriv')
            zip.extract('HD.dat', 'files//LMpriv')    
            zip.extract('FR.dat', 'files//LMpriv')
            zip.extract('LO.dat', 'files//LMpriv')
        with ZipFile('l_micro.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//micro')
            zip.extract('HD.dat', 'files//micro')    
            zip.extract('FR.dat', 'files//micro')
            zip.extract('LO.dat', 'files//micro')
        with ZipFile('l_LMcomm.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//LMcomm')
            zip.extract('HD.dat', 'files//LMcomm')    
            zip.extract('FR.dat', 'files//LMcomm')
            zip.extract('LO.dat', 'files//LMcomm')
        with ZipFile('l_paging.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//paging')
            zip.extract('HD.dat', 'files//paging')    
            zip.extract('FR.dat', 'files//paging')
            zip.extract('LO.dat', 'files//paging')
        with ZipFile('l_coast.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//coast')
            zip.extract('HD.dat', 'files//coast')    
            zip.extract('FR.dat', 'files//coast')
            zip.extract('LO.dat', 'files//coast')
        with ZipFile('l_LMbcast.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//LMbcast')
            zip.extract('HD.dat', 'files//LMbcast')    
            zip.extract('FR.dat', 'files//LMbcast')
            zip.extract('LO.dat', 'files//LMbcast')
        with ZipFile('l_mdsitfs.zip', 'r') as zip:
            zip.extract('AN.dat', 'files//mdsitfs')
            zip.extract('HD.dat', 'files//mdsitfs')    
            zip.extract('FR.dat', 'files//mdsitfs')
            zip.extract('LO.dat', 'files//mdsitfs')
        Show(frame,'Preparing and cleaning the data')
        os.chdir('files')
        ANString=''
        HDString=''
        FRString=''
        LOString=''
        for folder in os.listdir():
            with open(folder+'//AN.dat','r') as file:
                ANString=ANString+file.read()
            with open(folder+'//LO.dat','r') as file:
                LOString=LOString+file.read()
            with open(folder+'//HD.dat','r') as file:
                HDString=HDString+file.read()
            with open(folder+'//FR.dat','r') as file:
                FRString=FRString+file.read()
        os.chdir('..')
        ANfile=open('AN final.dat','w')
        LOfile=open('LO temp.dat','w')
        FRfile=open('FR final.dat','w')
        HDfile=open('HD final.dat','w')
        ANfile.write(ANString)
        ANfile.close()
        HDfile.write(HDString)
        HDfile.close()
        FRfile.write(FRString)
        FRfile.close()
        LOfile.write(LOString)
        LOfile.close()
        del(ANString)
        del(HDString)
        del(LOString)
        del(FRString)
        working=open('LO temp.dat','r')
        filelines=working.readlines()
        for x in range(len(filelines)):
            charcheck=list(filelines[x])
            for i in range(len(charcheck)):
                if charcheck[i] =='"':
                    charcheck[i]=''
            filelines[x]=''.join(charcheck)
            checkline=filelines[x].split('|')
            for y in range(19,27):
                if checkline[y]=='':
                    checkline[y]='-1'
            LatD=int(checkline[19])+(int(checkline[20])/60)+(float(checkline[21])/3600)
            LongD=int(checkline[23])+(int(checkline[24])/60)+(float(checkline[25])/3600)
            checkline[19]=str(LatD)
            checkline[20]=checkline[22]
            checkline[21]=str(LongD)
            checkline[22]=checkline[26]
            del(checkline[23:27])
            filelines[x]='|'.join(checkline)
        newfile=open('LO final.dat','w')
        for line in filelines:
            newfile.write(line)
        working.close()
        newfile.close()
        Show(frame,'Reading the data')
        LocData=pandas.read_csv('LO final.dat', sep='|', encoding='cp1252', header=None, names=['1','USI','3','4','Callsign','6','7','8','Loc Number','10','11','Address','City','14','State','16','17','18','19','LatDec','LatDir','LongDec','LongDir','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51'], dtype={'USI':str,'LongDec':float,'LatDec':float,'LatDir':str,'LongDir':str,'9':str,'11':str,'16':str,'17':str,'30':str,'34':str,'36':str,'37':str,'41':str,'49':str,'50':str})
        AntData=pandas.read_csv('AN final.dat', sep='|', encoding='cp1252', header=None, names=['1','USI','3','4','Callsign','6','Ant Number','Loc Number','9','TR','11','Rad Center','Make','Model','Tilt','16','Beamwidth','Gain','Azimuth','20','21','22','23','24','25','26','27','28','29','30','31','32','Path Number','34','35','36','37','38'], dtype={'USI':str})
        testing=pandas.merge(LocData[['Callsign','Loc Number', 'LatDec','LatDir','LongDec','LongDir','Address','City','State']],AntData[['Callsign','Loc Number','Ant Number','TR','Rad Center','Make','Model','Azimuth']],how='left', on=['Callsign','Loc Number'])
        del(AntData)
        del(LocData) 
        testing=testing[testing['TR']=='T']
        FreqData=pandas.read_csv('FR final.dat',sep='|',encoding='cp1252',header=None,names=['1','USI','3','4','Callsign','6','Loc Number','Ant Number','9','10','Frequency','12','13','14','15','Power','Power ERP','18','19','20','21','22','23','24','25','26','27','28','29','30'])
        testing2=pandas.merge(testing[['Callsign','Loc Number','LatDec','LatDir','LongDec','LongDir','Address','City','State','Ant Number','Rad Center','Make','Model','Azimuth']],FreqData[['Callsign','Loc Number','Ant Number','Frequency','Power','Power ERP']],how='left', on=['Callsign','Loc Number','Ant Number'])
        ActiveData=pandas.read_csv('HD final.dat', index_col=False, sep='|', encoding='cp1252', header=None, names=['Record Type','USI','ULS File','EBF Number','Callsign','License Status','Radio Service Code','Grant Date','Expired Date','Cancellation Date','Eligibility Rule Num','Applicant Type','Alien','Alien Govt','Alien Corp','Alien Officer','Alien Control','Revoked','Convicted','Adjudged','Involved Reserved','Common Carrier','Non Common Carrier','Private Comm','Fixed','Mobile','Radio Location','Satellite','Developmental or STA','Interconnected Service','Certifier First Name','Certifier MI','Certifier Last Name','Certifier Suffix','Certifier Title','Gender','African American','Native American','Hawaiian','Asian','White','Ethnicity','Effective Date','Last Action Date','Auction ID','Reg Stat Broad Serv','Band Manager','Type Serv Broad Serv','Alien Ruling','Licensee Name Change'], dtype={'USI':str})
        testing3=pandas.merge(testing2[['Callsign','Loc Number','LatDec','LatDir','LongDec','LongDir','Address','City','State','Ant Number','Rad Center','Make','Model','Azimuth','Frequency','Power','Power ERP']], ActiveData[['Callsign','License Status','Radio Service Code']], how='left', on=['Callsign'])
        testing3=testing3[testing3['License Status']=='A']
        testing3.to_csv('Micro and Omni//Micro and Omni Output.csv', index=False)
        Show(frame,'Cleaning up')
        del(FreqData)
        del(ActiveData)
        del(testing3)
        del(testing)
        del(testing2)
        for file in os.listdir():
            if file.endswith('.zip') or file.endswith('.dat'):
                os.remove(file)
        os.chdir('files')
        for folder in os.listdir():
            os.chdir(folder)
            for file in os.listdir():
                os.remove(file)
            os.chdir('..')
            os.rmdir(folder)
        os.chdir('..')
        os.rmdir('files')
        timecode=datetime.datetime.now().strftime("%m-%d-%Y")
        with open('buildDate.txt','r') as file:
            dates=file.readlines()
        dates[1]=timecode+'\n'
        write=''.join(dates)
        with open('buildDate.txt','w') as file:
            file.write(write)
        
    
    def addZero(value,check):
        '''
        For use in building the market code list
        '''
        if value < 10:
            output='00'+str(value)
        elif value < 100:
            output='0'+str(value)
        else:
            output=str(value)
        if check=='EAG7':
            output=output[1:]
        return output
        
    def MarketCodeList():
        '''
        Building the market code list used for the Radio Block database and search
        '''
        wget.download('https://transition.fcc.gov/bureaus/oet/info/maps/areas/data/2000/FCCCNTY2K.txt')
        CodeList=pandas.read_csv('FCCCNTY2k.txt', sep=',', encoding='cp1252')
        CodeList=CodeList.rename(columns={'EA':'BEA'})
        for col in CodeList.columns[4:]:
            for row in range(len(CodeList.index)):
                CodeList.loc[row,col]=col+DBT.addZero(CodeList.loc[row,col],col)
        CodeList.to_csv('Radio Blocks//County and Market Codes.csv',sep=',',encoding='cp1252', index=False)
        os.remove('FCCCNTY2K.txt')
        
    
    
    def MassMediaDataBuild(frame):
        '''
        Build the database used for the TV/AM/FM search
        '''
        Show(frame,'Downloading the datafiles')
        os.chdir('Mass Media')
        for file in os.listdir():
            os.remove(file)
        wget.download('https://transition.fcc.gov/ftp/Bureaus/MB/Databases/cdbs/fm_eng_data.zip')
        wget.download('https://transition.fcc.gov/ftp/Bureaus/MB/Databases/cdbs/tv_eng_data.zip')
        wget.download('https://transition.fcc.gov/ftp/Bureaus/MB/Databases/cdbs/am_ant_sys.zip')
        wget.download('https://transition.fcc.gov/ftp/Bureaus/MB/Databases/cdbs/application.zip')
        Show(frame,'Extracting the data')
        with ZipFile('fm_eng_data.zip', 'r') as zip:
            zip.extractall()
        with ZipFile('tv_eng_data.zip', 'r') as zip:
            zip.extractall()
        with ZipFile('am_ant_sys.zip', 'r') as zip:
            zip.extractall()
        with ZipFile('application.zip', 'r') as zip:
            zip.extractall()
        Show(frame,'Cleaning up')
        for file in os.listdir():
            if file.endswith('.zip'):
                os.remove(file)
        os.chdir('..')
        timecode=datetime.datetime.now().strftime("%m-%d-%Y")
        with open('buildDate.txt','r') as file:
            dates=file.readlines()
        dates[2]=timecode
        write=''.join(dates)
        with open('buildDate.txt','w') as file:
            file.write(write)
    
    
        
    
    
    def MicroSearch(frame,LatDec,LongDec):
        '''
        Search for microwaves and omnis within fifteen seconds (roughly one qaurter mile)
        '''    
        Show(frame,'Working...')
        Radius=15/3600
        LatDec=float(LatDec)
        LongDec=float(LongDec)
        if LatDec >= 0:
            LatDir='N'
        else:
            LatDir='S'
        if LongDec >= 0:
            LongDir='E'
        else:
            LongDir='W'
        LatHigh=abs(LatDec) + Radius
        LatLow=abs(LatDec) - Radius
        LongHigh=abs(LongDec) + Radius
        LongLow=abs(LongDec) - Radius
        Data=pandas.read_csv('Micro and Omni//Micro and Omni Output.csv',encoding='cp1252')
        Results=Data[(LatLow<=Data['LatDec']) & (LatHigh>=Data['LatDec']) & (LongLow<=Data['LongDec']) & (LongHigh>=Data['LongDec']) & (LatDir==Data['LatDir']) & (LongDir==Data['LongDir'])]
        del(Data)
        Results.to_excel(writer, sheet_name='Antennas '+str(LatDec)+' '+str(LongDec),index=False)
        del(Results)
        Searching(frame)
        
        
    
    
    def LicenseSearch(frame,County,State):
        '''
        Create a list of channel blocks and licensees
        '''
        Show(frame,'Working...')
        List=pandas.read_csv('Radio Blocks//License Output.csv', sep=',', encoding='cp1252')
        Output=List[(List['County'] ==County) & (List['State'] == State)]
        for index in Output.index:
            if Output.loc[index,'Radio Code'] in ['AD','AH','AT','AW']:
                Output.loc[index,'Frequency']=2100
            elif Output.loc[index,'Radio Code'] in ['CL']:
                Output.loc[index,'Frequency']=850
            elif Output.loc[index,'Radio Code'] in ['CW','CY']:
                Output.loc[index,'Frequency']=1900
            elif Output.loc[index,'Radio Code'] in ['WS']:
                Output.loc[index,'Frequency']=2300
            elif Output.loc[index,'Radio Code'] in ['WU','WY','WZ']:
                Output.loc[index,'Frequency']=700
        Output[['Callsign','Entity Name','Channel Block','Frequency']].to_excel(writer, sheet_name=County+' '+State,index=False)
        del(Output)
        del(List)
        Searching(frame)
        
    
    
    
    
    def MassMediaSearch(frame,LatDec,LongDec):
        '''
        Create a list of AM/TV/FM stations within 14 seconds of the site.
        '''
        Show(frame,'Working...')
        LatDec=float(LatDec)
        LongDec=float(LongDec)
        Lat=LatDec+90
        Long=abs(LongDec)+180
        Radius=14/3600
        FMEngData=pandas.read_csv('Mass Media//fm_eng_data.dat', sep='|', encoding='cp1252', index_col=False, header=None, names=['ant_input_pwr','ant_max_pwr_gain','ant_polarization','ant_rotation','antenna_id','antenna_type','application_id','asd_service','asrn_na_ind','asrn','avg_horiz_pwr_gain','biased_lat','biased_long','border_code','border_dist','docket_num','effective_erp','elev_amsl','elev_bldg_ag','eng_record_type','facility_id','fm_dom_status','gain_area','haat_horiz_rc_mtr','haat_vert_rc_mtr','hag_horiz_rc_mtr','hag_overall_mtr','hag_vert_rc_mtr','horiz_bt_erp','horiz_erp','lat_deg','lat_dir','lat_min','lat_sec','lon_deg','lon_dir','lon_min','lon_sec','loss_area','max_ant_pwer_gain','max_haat','max_horiz_erp','max_vert_erp','multiplexor_loss','power_output_vis_kw','predict_coverage_area','predict_pop','rcamsl_horiz_mtr','rcamsl_vert_mtr','station_class','terrain_data_src','vert_bt_erp','vert_erp','num_sections','present_area','percent_change','spacing','terrain-data_src_other','trans_power_output','mainkey','lat_whole_secs','lon_whole_secs','station_channel','lic_ant_make','lic_ant_model_num','min_horiz_erp','haat_horiz_calc_ind','erp_w','trans_power_output_w','market_group_num','last_change_date','junk'])
        TVEngData=pandas.read_csv('Mass Media//tv_eng_data.dat', sep='|', encoding='cp1252', index_col=False, header=None, names=['ant_input_pwr','ant_max_pwr_gain','ant_polarization','antenna_id','antenna_type','application_id','asrn_na_ind','asrn','aural_freq','avg_horiz_pwr_gain','biased_lat','biased_long','border_code','carrier_freq','docket_num','effective_erp','electrical_deg','elev_amsl','elev_bldg_ag','eng_record_type','fac_zone','facility_id','freq_offset','gain_area','haat_rc_mtr','hag_overall_mtr','hag_rc_mtr','horiz_bt_erp','lat_deg','lat_dir','lat_min','lat_sec','lon_deg','lon_dir','lon_min','lon_sec','loss_area','max_ant_pwer_gain','max_erp_dbk','max_erp_kw','max_haat','mechanical_deg','multiplexor_loss','power_output_vis_dbk','power_output_vis_kw','predict_coverage_are','predict_pop','terrain_data_src_other','terrain_data_src','tilt_towards_azimuth','true_deg','tv_dom_status','upperband_freq','vert_bt_erp','visual_freq','vsd_service','rcamsl_horiz_mtr','ant_rotation','input_trans_line','max_erp_to_hor','trans_line_loss','lottery_group','analog_channel','lat_whole_secs','lon_whole_secs','max_erp_any_angle','station_channel','lic_ant_make','lic_ant_model_num','dt_emission_mask','site_number','elevation_antenna_id','last_change_date','junk'])
        AMAntSys=pandas.read_csv('Mass Media//am_ant_sys.dat', sep='|', encoding='cp1252', index_col=False,header=None, names=['ant_mode','ant_sys_id','application_id','aug_count','bad_data_switch','domestic_pattern','dummy_data_switch','efficiency_restricted','efficiency_theoretical','feed_circ_other','feed_circ_type','hours_operation','lat_deg','lat_dir','lat_min','lat_sec','lon_deg','lon_dir','lon_min','lon_sec','q_factor','q_factor_custom_ind','power','rms_augmented','rms_standard','rms_theoretical','tower_count','eng_record_type','biased_lat','biased_long','mainkey','am_dom_status','lat_whole_secs','lon_whole_secs','ant_dir_id','grandfathered_ind','specified_hrs_range','augmented_ind','last_change_date','junk'])
        Application=pandas.read_csv('Mass Media//application.dat', sep='|', encoding='cp1252', index_col=False,header=None, names=['app_arn','app_service','application_id','facility_id','file_prefix','comm_city','comm_state','fac_frequency','station_channel','fac_callsign','general_app_service','app_type','paper_filed_ind','dtv_type','frn','shortform_app_arn','shortform_file_prefix','corresp_ind','assoc_facility_id','network_affil','sat_tv_ind','comm_county','comm_zip1','comm_zip2','app-code','last_change_date','junk'])
        AMCombined=pandas.merge(Application[['application_id','fac_callsign','comm_city','comm_state','comm_zip1','fac_frequency']],AMAntSys,how='left',on=['application_id'])
        AMResult=AMCombined[(AMCombined['eng_record_type']=='C') & (AMCombined['biased_lat']<= Lat+Radius) & (AMCombined['biased_lat']>= Lat-Radius) & (AMCombined['biased_long']<= Long+Radius) & (AMCombined['biased_long']>= Long-Radius)]
        if not AMResult.empty:
            AMResult[['fac_frequency','fac_callsign','comm_city','comm_state','comm_zip1','ant_mode','last_change_date','lat_deg','lat_min','lat_sec','lat_dir','lon_deg','lon_min','lon_sec','lon_dir','power','hours_operation']].to_excel(writer, sheet_name='AM '+str(LatDec)+' '+str(LongDec),index=False)
        del(AMCombined)
        del(AMResult)
        del(AMAntSys)
        FMCombined=pandas.merge(Application[['application_id','fac_callsign','comm_state','comm_city','comm_zip1','fac_frequency']],FMEngData,how='left',on=['application_id'])
        FMResult=FMCombined[(FMCombined['eng_record_type']=='C') & (FMCombined['biased_lat']<= Lat+Radius) & (FMCombined['biased_lat']>= Lat-Radius) & (FMCombined['biased_long']<= Long+Radius) & (FMCombined['biased_long']>= Long-Radius)]
        if not FMResult.empty:
            FMResult[['fac_frequency','fac_callsign','comm_city','comm_state','comm_zip1','antenna_id','hag_vert_rc_mtr','lat_deg','lat_min','lat_sec','lat_dir','lon_deg','lon_min','lon_sec','lon_dir','erp_w','trans_power_output_w','horiz_erp','vert_erp','last_change_date']].to_excel(writer, sheet_name='FM '+str(LatDec)+' '+str(LongDec),index=False)
        del(FMCombined)
        del(FMResult)
        del(FMEngData)
        TVCombined=pandas.merge(Application[['application_id','fac_callsign','comm_city','comm_state','comm_zip1','fac_frequency']],TVEngData,how='left',on=['application_id'])
        TVResult=TVCombined[(TVCombined['eng_record_type']=='C') & (TVCombined['biased_lat']<= Lat+Radius) & (TVCombined['biased_lat']>= Lat-Radius) & (TVCombined['biased_long']<= Long+Radius) & (TVCombined['biased_long']>= Long-Radius)]
        if not TVResult.empty:
            TVResult[['fac_frequency','fac_callsign','comm_city','comm_state','comm_zip1','carrier_freq','lat_deg','lat_min','lat_sec','lat_dir','lon_deg','lon_min','lon_sec','lon_dir','effective_erp','hag_rc_mtr','horiz_bt_erp','vert_bt_erp','max_erp_kw','antenna_id','last_change_date']].to_excel(writer, sheet_name='TV '+str(LatDec)+' '+str(LongDec),index=False)
        del(TVCombined)
        del(TVResult)
        del(TVEngData)
        Searching(frame)



















def Clean(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def Show(frame,disptext):
    Clean(frame)
    tk.Label(frame,text=disptext).pack()
    frame.update()




def DatabaseBuild(frame):
    def Buildlaunch():
        if LicBuild.get()==1:
            DBT.LicenseDataBuild(frame)            
        if MicBuild.get()==1:
            DBT.MicroDataBuild(frame)
        if MMBuild.get()==1:
            DBT.MassMediaDataBuild(frame)
        Core(frame)
    Clean(frame)
    tk.Label(frame,text='Select the databases you wish to rebuild. Note - The license database can take hours to complete.').pack()
    tk.Checkbutton(frame,text='License Database',variable=LicBuild).pack()
    tk.Checkbutton(frame,text='Microwave Database',variable=MicBuild).pack()
    tk.Checkbutton(frame,text='Mass Media Database',variable=MMBuild).pack()
    tk.Button(frame,text='Proceed',command=Buildlaunch).pack()
    tk.Button(frame,text='Quit',command=lambda:Core(frame)).pack()
    
def Searching(frame):
    def LicSearch():
        Clean(frame)
        tk.Label(frame,text='Input the County and State you wish to search in.').grid(row=0)
        tk.Label(frame,text='County').grid(row=1)
        tk.Label(frame,text='State').grid(row=2)
        County=tk.Entry(frame)
        County.grid(row=1,column=1)
        State=tk.Entry(frame)
        State.grid(row=2,column=1)
        tk.Button(frame,text='Proceed',command=lambda:DBT.LicenseSearch(frame,County.get(),State.get())).grid(row=3)
        tk.Button(frame,text='Done',command=lambda:Searching(frame)).grid(row=3,column=1)
    
    def MicSearch():
        Clean(frame)
        tk.Label(frame,text='Input the Latitude and Longitude as decimals.').grid(row=0)
        tk.Label(frame,text='Latitude').grid(row=1)
        tk.Label(frame,text='Longitude').grid(row=2)
        Lat=tk.Entry(frame)
        Lat.grid(row=1,column=1)
        Long=tk.Entry(frame)
        Long.grid(row=2,column=1)
        tk.Button(frame,text='Proceed',command=lambda:DBT.MicroSearch(frame,Lat.get(),Long.get())).grid(row=3)
        tk.Button(frame,text='Done',command=lambda:Searching(frame)).grid(row=3,column=1)
    def MMSearch():
        Clean(frame)
        tk.Label(frame,text='Input the Latitude and Longitude as decimals.').grid(row=0)
        tk.Label(frame,text='Latitude').grid(row=1)
        tk.Label(frame,text='Longitude').grid(row=2)
        Lat=tk.Entry(frame)
        Lat.grid(row=1,column=1)
        Long=tk.Entry(frame)
        Long.grid(row=2,column=1)
        tk.Button(frame,text='Proceed',command=lambda:DBT.MassMediaSearch(frame,Lat.get(),Long.get())).grid(row=3)
        tk.Button(frame,text='Done',command=lambda:Searching(frame)).grid(row=3,column=1)
    def SearchCompile():
        writer.save()
        Core(frame)    
    Clean(frame)
    tk.Label(frame,text='Execute searches as necessary. Each one will be added to a separate sheet in the resulting Excel.').pack()
    tk.Button(frame,text='License Search',command=LicSearch).pack()
    tk.Button(frame,text='Micro and Omni Search',command=MicSearch).pack()
    tk.Button(frame,text='Mass Media Search',command=MMSearch).pack()
    tk.Button(frame,text='Finished',command=SearchCompile).pack()
    

def Core(frame):
    Clean(frame)
    with open('buildDate.txt','r') as file:
        dates=file.readlines()
        LicDate=dates[0][:-1]
        MicDate=dates[1][:-1]
        MMDate=dates[2]
    tk.Label(frame,text='The License database was last built on '+LicDate+'\nThe Microwave and Omni database was last built on '+MicDate+
             '\nThe Mass Media database was last built on '+MMDate,justify=tk.CENTER,pady=5).pack()
    tk.Button(frame, text='Database Build',padx=20,command=lambda:DatabaseBuild(frame)).pack()
    tk.Button(frame,text='Execute Search',padx=20,command=lambda:Searching(frame)).pack()
    tk.Button(frame,text='Finished',padx=20,command=frame.destroy).pack()



timecode=datetime.datetime.now().strftime("%Y-%m-%d - %H.%M.%S")
writer=pandas.ExcelWriter('Search Outputs ' + timecode + '.xlsx', engine='xlsxwriter')
root=tk.Tk()
LicBuild=tk.BooleanVar()
MicBuild=tk.BooleanVar()
MMBuild=tk.BooleanVar()
Core(root)
root.mainloop()
