# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 12:02:50 2016
@author: darin
"""

import os, sys

import urllib

def openfile(file):
    with open(file,'r') as openfile:
        readfile=openfile.read()
    openfile.close()
    return readfile
    
def adrag(speed, cda):
    return 0.5 * speed * speed * 1.225 * cda

def aroll(weight, crr):
    return float(weight) * crr

if __name__ == "__main__":
    seventydrange = 245.0
    
    txtflag = 0
    homedir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    for root, dirnames, filenames in os.walk(homedir):
        for thefile in filenames:
            if '.txt' in thefile:
                txtflag = 1
                
    if txtflag == 0:
        linklist = []
        
        r = urllib.urlopen('https://www.epa.gov/vehicle-and-fuel-emissions-testing/dynamometer-drive-schedules').read()
        pref = 'https://www.epa.gov/'
        
        for i in r.split('\n'):
            for j in i.split('><'):
                if '.txt' in j:
                    linklist.append(j.split('"')[1])
        for link in linklist:
            urllib.urlretrieve(pref + link, link.split('/')[-1])
            
    
    #.23 Cd = .525m^2 CdA
    #My original assumptions...
    #Model 3 55 weight = 1815, height = 55", width = 71", Cd =.21, CdA=.479
    #Model 3 55 weight = 1905, height = 55", width = 71", Cd =.21
    #Model 3 55 weight = 2177, height = 56", width = 77", Cd =.24
    #Motor trend assumptions are a starting weight ot 1995kg for a 55D(?) with a 200lb driver
    #Their drag area is ~1.075x my original estimate, but that could be from including mirrors in width
    #hwycol.txt count of lines with speed > 0 = 165
    
    vlist = [('Model_3_55',1995,.515), ('Model_3_60',2015,.515), 
             ('Model_3_65',2035,.515), ('Model_3_70',2055,.515),
             ('Model_3_75',2075,.515),  ('Model_S_70',2180, .604)]
            #('Model_S_90D',2279,.604)]
    vreslist = []

    for car in vlist:
        lstring = car[0] + '_list = []'
        exec(lstring)
    
    
    for root, dirnames, filenames in os.walk(homedir):
        for thefile in filenames:
            if '.txt' in thefile:
                tfile = openfile(root + '/' + thefile)
                for car in vlist:
                    clistname = car[0] + '_list'
                    ptot = 0.0
                    vw = car[1]
                    cda = car[2]
                    for sec in tfile.split('\n'):
                        fair = 0.0
                        froll = 0.0
                        ftot = 0.0
                        try:
                            vel = float(sec.split('\t')[1]) * 0.44704
                            fair = adrag(vel, cda)
                            if vel != 0.0:
                                froll = aroll(vw, 0.0089) #from Roadster 3 article
                            ftot = froll + fair
                            ptot = ptot + (ftot * vel) / 3600.0
                            
                        except:
                            pass
                    if ptot > 0:
                        acommand = clistname + ".append(('" + thefile + "'," + str(int(ptot)) +'))'
                        exec(acommand)
    
    zippedresult = eval('[i for i in zip(' + str([eval(i[0]+'_list') for i in vlist])[1:][:-1] + ')]')
    
    for i in zippedresult:
        if i[0][0] in ('hwycol.txt','ftpcol.txt'):
            print '_______________'
            print i[0][0]
            print '_______________'
            zipped = zip (i, [b[0] for b in vlist])
            for j in zipped:
                print j[1] + ' range is about... ' + str((float(i[-1:][0][1])/float(j[0][1])) \
                * 245.0 * \
                (float(j[1].split('_')[-1:][0])/float(zipped[-1:][0][1].split('_')[-1:][0])))
            print '\n'

'''
deriving power equation
f = ma

P = mv(dv/dt)

dt = (mv/P) dv

dt = (mv/(Pmotor - Pdrag)) dv

m is easy peasy, just the vehicle weight in kg.
f can get complicated. very roughly, it's vehicle's torque curve as a function os speed,
expressed as a polynomial, less the road load equation

ultimately... we get t = integral{0->60}((mv/(some polynomial - v(.5*CdA*1.225*v^2 + Crr*m*g)))dv)

That's nasty, so lets dump it into octave... later...

'''
    
'''
    #S70 unadjusted HWFET = 135, FTP75 = 133.7, GGE =33.7kWh
    s70hwycol = 33700/135.0
    s70ftpcol = 33700/133.7

        if i[0][0] == 'hwycol.txt':
            
            print '55 Range is about ' + str((float(i[2][1])/float(i[0][1]))*245.0*(55.0/70.0))
            print '75 Range is about ' + str((float(i[2][1])/float(i[1][1]))*245.0*(75.0/70.0))
        if i[0][0] == 'ftpcol.txt':
            print '55 Range is about ' + str((float(i[2][1])/float(i[0][1]))*245.0*(55.0/70.0))
            print '75 Range is about ' + str((float(i[2][1])/float(i[1][1]))*245.0*(75.0/70.0))
        print '\n'



#guesstimate for background power consumption watts, 50W
for i in zip(Model_3_55_list,Model_S_70D_list):
    if i[0][1] != 0:
        if i[0][0] == 'ftpcol.txt':
            whmile = (s70ftpcol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70ftpcol/whmile) * 243.0 * (55.0/70.0)), i[0][1], i[1][1]
        if i[0][0] == 'hwycol.txt':
            whmile = (s70hwycol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70hwycol/whmile) * 246.0 * (55.0/70.0)), i[0][1], i[1][1]
            
for i in zip(Model_3_75_list,Model_S_70D_list):
    if i[0][1] != 0:
        if i[0][0] == 'ftpcol.txt':
            whmile = (s70ftpcol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70ftpcol/whmile) * 243.0 * (75.0/70.0)), i[0][1], i[1][1]
        if i[0][0] == 'hwycol.txt':
            whmile = (s70hwycol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70hwycol/whmile) * 246.0 * (75.0/70.0)), i[0][1], i[1][1]
            
for i in zip(Model_S_90D_list,Model_S_70D_list):
    if i[0][1] != 0:
        if i[0][0] == 'ftpcol.txt':
            whmile = (s70ftpcol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70ftpcol/whmile) * 243.0 * (90.0/70.0)), i[0][1], i[1][1]
        if i[0][0] == 'hwycol.txt':
            whmile = (s70hwycol - 50.0)*(float(i[0][1])/float(i[1][1])) + 50.0
            print i[0][0], 'wh/mile ' + str(whmile), 'Range ' + str((s70hwycol/whmile) * 246.0 * (90.0/70.0)), i[0][1], i[1][1]
'''