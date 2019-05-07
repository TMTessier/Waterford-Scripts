# -*- coding: utf-8 -*-
"""
Created on Tue May  7 09:16:04 2019

@author: Thomas Tessier
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 12:39:53 2018

@author: Thomas Tessier
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:01:07 2018

@author: Thomas Tessier
"""

'''
The purpose of this code is to extract information from the reports generated by
Airspace and insert them into a Waterford FAA Report Template

v1.1
Changed the way lines are read, code is easier to adjust and more accurate.

v1.0
Uses the same template and logic as the existing FAA Generator 1.09 by Dave Kiser
as much as possible.
'''

'''
Info that cannot be extracted from Airspace reports
Customer Name (User Input)
Type of structure (monopole, rooftop, etc.)(User Input)
Does contruction increase height of existing structure?
'''
import os

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



merge={}
filenames=input('Type in the name of the desired report files\n (Exactly the same as put into Airspace, no file extension)\n : ')
OverExisting=bool(input('Type in True if an existing structure is getting taller.\n Otherwise press Enter\n : '))
merge['Customer']=input("Who's the customer? \n : ")
merge['Writer']=input("Report Writer's Name?\n : ")


from mailmerge import MailMerge
search=0



'''
Base setup
'''
fh=open('.\\Airspace Files\\'+filenames+'.SRP','r')
lines=fh.readlines()

    

'''
Reading and extracting heights from 77.9 rules and check if TERPS analysis needed
'''

for x in range(len(lines)):
    if 'NOTICE CRITERIA' in lines[x]:
        search=x
        break
Rules779={search+1:'77.9(a)',search+2:'77.9(b)','IFR':'IFR Straight-In'}

merge['RuleSeven']=''
if 'Exceeds' in lines[search+1]:
    merge['RuleSeven']='77.9(a)'

if 'Exceeds' in lines[search+2]:
    testline=lines[search+2].split(' ')
    testline=clean(testline)
    NoNoticeSL=int(testline[-2])
    merge['RuleSeven']='77.9(b)'


TERPSNeed=False
for i in range(search+3,search+7):
    if 'TERPS' in lines[i]:
        TERPSNeed=True

ifr=search+14
while 'OBSTRUCTION' not in lines[ifr]:
    if 'maximum height to avoid' in lines[ifr]:
        testline=lines[ifr].split(' ')
        testline=clean(testline)
        testval=int(round(float(testline[-3])))
        if testval < NoNoticeSL:
            NoNoticeSL=testval
            merge['RuleSeven']='IFR Straight-In'
    ifr+=1

Limiters={}

for x in range(len(lines)):
    if '77.17(a)(3)' in lines[x]:
        search=x
        break
testline=lines[search+1].split(' ')
testline=clean(testline)
try:
    Limiters['77.17(a)(3)']=int(testline[-3])
except:
        pass

for x in range(len(lines)):
    if 'MOCA' in lines[x]:
        search=x
        break
testline=lines[search+2].split(' ')
testline=clean(testline)
Limiters['MOCA']=int(testline[-3])


for x in range(len(lines)):
    if 'TRAFFIC PATTERN' in lines[x]:
        search=x
        break
while 'TERPS' not in lines[search]:
    if 'Maximum AMSL' in lines[search]:
        testline=lines[search].split(' ')
        testline=clean(testline)
        Limiters['VFR']=int(testline[-2])
    search+=1


        
'''
Address
'''

addressline=lines[10].split(' ')
addressline=clean(addressline)
address=' '.join(addressline[1:])
merge['Address']=address[:-1]


'''
Site Name
'''

siteline=lines[8].split(' ')
site=list(siteline[-1][:-1])
for i in range(len(site)):
    if site[i] == '_':
        site[i] = ' '
site=''.join(site)
site=site.split(' ')
for i in range(len(site)):
    site[i]=site[i][0]+site[i][1:].lower()
merge['Site']=' '.join(site)

'''
Coordinates
'''

coordline=lines[12].split(' ')
coordline=clean(coordline)
merge['Latitude'] = coordline[1]
merge['Longitude'] = coordline[3][:-1]

'''
Elevation, study height, total height
'''

elevationline=lines[14].split('......')
elevationline=elevationline[1].split(' ')
merge['Elevation'] = elevationline[0]
elev=float(merge['Elevation'])

heightline=lines[15].split('.........')
heightline=heightline[1].split(' ')
merge['StudyHeight'] = heightline[0]

totalline=lines[16].split('......')
totalline=totalline[1].split(' ')
merge['TotalHeight'] = totalline[0]
totalheight=int(totalline[0])


NoNotice=NoNoticeSL-elev

'''
Proposed or Existing
'''

sowline=lines[2].split('Report: ')
if sowline[1][0]=='N':
    merge['SOW']='proposed'
    merge['Describe']='proposed structure'
elif sowline[1][0]=='E':
    merge['SOW']='existing'
    merge['Describe']='proposed changes to the existing structure'
else:
    print('Oops')

'''
Check for Private Air facilities
'''

for x in range(search, len(lines)):
    if 'PRIVATE' in lines[x]:
        search=x
        break
Private=False
while 'NAVIGATION' not in lines[search]:
    if 'Possible Impact' in lines[search]:
        Private=True
        break
    search+=1
    
if Private:
    merge['PrivateAir']='Private use landing facilities are a potential factor for this location.'
else:
    merge['PrivateAir']='Private use landing facilities are not a factor for this location.'    

'''
Check for AM Stations
'''
for x in range(search, len(lines)):
    if 'CFR Title 47' in lines[x]:
        search=x
        break
AM=False
amline=lines[search+1].split(' ')
amline=clean(amline)
if amline[3]=='REQUIRED':
    AM=True
    
if AM:
    merge['AMStudy']='An AM study is required.'
else:
    merge['AMStudy']='An AM study is not required.'


'''
Copy report
'''
fh.seek(0)
merge['SummaryReport']=fh.read()

'''
close file
'''     
fh.close() 

        
'''
Reading and extracting heights from 77.17 and 77.19
'''

Hazard=499
Study=499
HazardSL=Hazard+elev
StudySL=Study+elev


far=open('.\\Airspace Files\\'+filenames+'.FAR','r')
farlines=far.readlines()
search=0
rules=['77.17(a)(1)','77.17(a)(2)','77.19 (a)','77.19(b)','77.19(c)','77.19(e)','77.19(d)']
for rule in rules:
    for x in range(search,len(farlines)):
        if rule in farlines[x]:
            search=x+1
            break
    while 'A height' not in farlines[search]:
        if 'ALLOWABLE HEIGHT' in farlines[search]:
            line=farlines[search].split(' ')
            line=clean(line)
            Limiters[rule]=int(line[-3])
            break
        if 'SURFACE HEIGHT' in farlines[search]:
            line=farlines[search].split(' ')
            line=clean(line)
            Limiters[rule]=int(float(line[-2]))
            break
        search+=1
studyrule=''
hazardrule=''
for rule in Limiters:
    if StudySL > Limiters[rule]:
        HazardSL=StudySL
        hazardrule=studyrule
        StudySL=Limiters[rule]
        studyrule=rule
    
Hazard=HazardSL-elev
Study=StudySL-elev

if StudySL<totalheight:
    merge['RuleSeventeen']=studyrule
if HazardSL<totalheight:
    merge['RuleNineteen']=hazardrule




far.close()

merge['NoNoticeSL']=str(NoNoticeSL)
merge['NoNotice']=str(NoNotice)
merge['StudySL']=str(StudySL)
merge['Study']=str(Study)
merge['HazardSL']=str(HazardSL)
merge['Hazard']=str(Hazard)


'''
Specific Report Language
'''
if merge['SOW'] == 'proposed':
    if merge['RuleSeven'] != '':
        merge['NoticeRequire']='Notice is required'
        merge['NoticeExpl']='At this proposed height, there are FAR rule exceendances.'
    else:
        merge['NoticeRequire']='Notice is not required'
        merge['NoticeExpl']='At this proposed height, there are no FAR rule exceedances.'
elif OverExisting:
    if merge['RuleSeven'] != '':
        merge['NoticeRequire']='Notice is required'
        merge['NoticeExpl']='At this proposed height, there will be an increase to the overall existing structure height and FAR rule exceedances.'
    else:
        merge['NoticeRequire']='Notice is not required'
        merge['NoticeExpl']='At this proposed height, there will be an increase to the overall existing structure height but no FAR rule exceedances.'
else:
    merge['NoticeRequire']='Notice is not required'
    merge['NoticeExpl']='At this proposed height, there will be no increase to the overall existing structure height.'



'''
Airport File
'''
fh=open('.\\Airspace Files\\'+filenames+'.APT','r') 
lines=fh.readlines()

'''
Find correct airport and extract info
'''

airportline=lines[17].split(' ')
airportline=clean(airportline)
merge['AirportID']=airportline[0]
merge['AirportDist']=airportline[-3]
merge['AirportBear']=airportline[-4]
namestring=airportline[2:-4]     
merge['AirportName']=' '.join(namestring)

if airportline[1]=='AIR':
    merge['AirportType']='airport'
elif airportline[1]=='SEA':
    merge['AirportType']='seaport'
else:
    merge['AirportType']='facility'


fh.close()

'''
write merge dictionary to template and create report
'''
template='.\\Template\\FAA Template Python.docx'
with MailMerge(template) as document:
    document.merge_pages([merge])
    document.write('.\\Results\\'+merge['Site']+' Test Output.docx')
    document.close()

print('Done!')
if TERPSNeed:
    print('The report indicates that a TERPS analysis is required, may want to double check.')
input('Press enter to check it out...')
os.startfile('.\\Results\\'+merge['Site']+' Test Output.docx', 'open')