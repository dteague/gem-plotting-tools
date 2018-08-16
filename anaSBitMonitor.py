#!/bin/env python

"""
anaSbitMonitor.py
=================
"""

if __name__ == '__main__':
    import os
    import sys
    
    from gempython.gemplotting.utils.anaoptions import parser
    #parser.add_option("--badPolThresh",type="int",dest="badPolThresh",default=128,
    #        help="the mininum number of channels an sbit should be observed for to assume it's polarity is wrong", metavar="badPolThresh")
    parser.add_option("--checkInvalid",action="store_true", dest="checkInvalid",
            help="If provided invalid sbits will be considered", metavar="checkInvalid")
    
    parser.set_defaults(outfilename="SBitMonitorData.root")
    (options, args) = parser.parse_args()
    filename = options.filename[:-5]
    os.system("mkdir " + options.filename[:-5])

    print filename
    outfilename = options.outfilename

    import ROOT as r
    #r.TH1.SetDefaultSumw2(True)
    r.gROOT.SetBatch(True)
    outF = r.TFile(filename+'/'+outfilename, 'recreate')
    inF = r.TFile(filename+'.root')

    # Determine the rates scanned
    print('Determining rates tested')
    import numpy as np
    import root_numpy as rp #note need root_numpy-4.7.2 (may need to run 'pip install root_numpy --upgrade')

    list_bNames = ['calEnable','isValid','ratePulsed']
    initInfo = rp.tree2array(tree=inF.sbitDataTree, branches=list_bNames)
    calEnableValues = np.unique(initInfo['calEnable'])
    isValidValues = np.unique(initInfo['isValid'])
    ratesUsed = np.unique(initInfo['ratePulsed'])

    print('Initializing histograms')
    from gempython.utils.nesteddict import nesteddict as ndict

    # Summary plots - 2D
    dict_h_vfatObsVsVfatPulsed = ndict() #Keys as: [isValid][calEnable][rate]

    # VFAT lvl plots - 1D
    dict_h_sbitMulti = ndict() #Keys as: [isValid][calEnable][rate][vfat]
    dict_h_sbitSize = ndict() #Keys as: [isValid][calEnable][rate][vfat]

    # VFAT lvl plots - 2D 
    dict_g_rateObsCTP7VsRatePulsed = ndict() #Keys as: [isValid][vfat]
    dict_g_rateObsFPGAVsRatePulsed = ndict() #Keys as: [isValid][vfat]
    dict_g_rateObsVFATVsRatePulsed = ndict() #Keys as: [isValid][vfat]
    dict_h_chanVsRatePulsed_ZRateObs = ndict() #Z axis is rate observed; Keys as: [isValid][calEnable][vfat]
    dict_h_sbitObsVsChanPulsed = ndict() #Keys as: [isValid][calEnable][rate][vfat]
    dict_h_sbitMultiVsSbitSize = ndict() #Keys as: [isValid][calEnable][rate][vfat]

    rateMap = {}
    from gempython.gemplotting.utils.anautilities import formatSciNotation
    for isValid in isValidValues:
        if not isValid and not options.checkInvalid:
            continue

        if isValid:
            strValidity="validSbits"
        else:
            strValidity="invalidSbits"

        for calEnable in calEnableValues:
            if calEnable:
                strCalStatus="calEnabled"
            else:
                strCalStatus="calDisabled"

            postScript = "{0}_{1}".format(strValidity,strCalStatus)

            # Summary Case
            for rate in ratesUsed:
                if ( not ( (calEnable and rate > 0) or (not calEnable and rate == 0.0) ) ):
                    continue

                # 2D Observables
                dict_h_vfatObsVsVfatPulsed[isValid][calEnable][rate] = r.TH2F(
                        "h_vfatObservedVsVfatPulsed_{0}_{1}Hz".format(postScript,int(rate)),
                        "Summmary - Rate {0} Hz;VFAT Pulsed;VFAT Observed".format(int(rate)),
                        24,-0.5,23.5,24,-0.5,23.5)
                dict_h_vfatObsVsVfatPulsed[isValid][calEnable][rate].Sumw2()

            for vfat in range(0,24):
                dict_h_chanVsRatePulsed_ZRateObs[isValid][calEnable][vfat] = r.TH2F(
                        "h_chanVsRatePulsed_ZRateObs_vfat{0}_{1}".format(vfat,postScript),
                        "VFAT{0};Rate #left(Hz#right);Channel",
                        len(ratesUsed),0,len(ratesUsed),
                        128,-0.5,127.5)

                # Overall Rate Observed by CTP7
                if calEnable:
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat] = r.TGraphErrors()
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].SetName(
                            "g_rateObsCTP7VsRatePulsed_vfat{0}_{1}".format(vfat,strValidity))
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].SetLineColor(r.kBlue)
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].SetLineWidth(2)
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].SetMarkerColor(r.kBlue)
                    dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].SetMarkerStyle(22)

                    # Overall Rate Observed by OH FPGA
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat] = r.TGraphErrors()
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].SetName(
                            "g_rateObsFPGAVsRatePulsed_vfat{0}_{1}".format(vfat,strValidity))
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].SetLineColor(r.kRed)
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].SetLineWidth(2)
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].SetMarkerColor(r.kRed)
                    dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].SetMarkerStyle(23)

                    # Per VFAT Rate Observed by OH
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat] = r.TGraphErrors()
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat].SetName(
                            "g_rateObsVFATVsRatePulsed_vfat{0}_{1}".format(vfat,strValidity))
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat].SetLineColor(r.kGreen)
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat].SetLineWidth(2)
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat].SetMarkerColor(r.kGreen)
                    dict_g_rateObsVFATVsRatePulsed[isValid][vfat].SetMarkerStyle(24)

                for binX,rate in enumerate(ratesUsed):
                    if vfat == 0: # Summary Case
                        # Set bin labels
                        rateMap[rate]=binX+1 # Used later to translate rate to bin position
                    dict_h_chanVsRatePulsed_ZRateObs[isValid][calEnable][vfat].GetXaxis().SetBinLabel(binX+1,formatSciNotation(str(rate)))

                    # VFAT level
                    if (calEnable or (not calEnable and rate == 0.0)):
                        # 1D Obs
                        dict_h_sbitMulti[isValid][calEnable][rate][vfat] = r.TH1F(
                                "h_sbitMulti_vfat{0}_{1}_{2}Hz".format(vfat,postScript,int(rate)),
                                "VFAT{0} - Rate {1} Hz;SBIT Multiplicity;N".format(vfat,int(rate)),
                                9,-0.5,8.5)
                        dict_h_sbitMulti[isValid][calEnable][rate][vfat].Sumw2()

                        dict_h_sbitSize[isValid][calEnable][rate][vfat] = r.TH1F(
                                "h_sbitSize_vfat{0}_{1}_{2}Hz".format(vfat,postScript,int(rate)),
                                "VFAT{0} - Rate {1} Hz;SBIT Size;N".format(vfat,int(rate)),
                                8,-0.5,7.5)
                        dict_h_sbitSize[isValid][calEnable][rate][vfat].Sumw2()

                        # 2D Obs
                        dict_h_sbitObsVsChanPulsed[isValid][calEnable][rate][vfat] = r.TH2F(
                                "h_sbitObsVsChanPulsed_vfat{0}_{1}_{2}Hz".format(vfat,postScript,int(rate)),
                                "VFAT{0} - Rate {1} Hz;Channel Pulsed;SBIT Observed".format(vfat,int(rate)),
                                128,-0.5,127.5,64,-0.5,63.5)
                        dict_h_sbitObsVsChanPulsed[isValid][calEnable][rate][vfat].Sumw2()

                        dict_h_sbitMultiVsSbitSize[isValid][calEnable][rate][vfat] = r.TH2F(
                                "h_sbitMultiVsSbitSize_vfat{0}_{1}_{2}Hz".format(vfat,postScript,int(rate)),
                                "VFAT{0} - Rate {1} Hz;SBIT Size;SBIT Multiplicity".format(vfat,int(rate)),
                                8,-0.5,7.5,9,-0.5,8.5)
                        dict_h_sbitMultiVsSbitSize[isValid][calEnable][rate][vfat].Sumw2()

    print("Looping over events and filling histograms")
    dict_validSbitsPerEvt = ndict()
    dict_listSbitSizesPerEvt = ndict()
    dict_wrongPolarity = ndict() # Keys [vfatN][vfatSBIT] = [ list of vfatCH values ]
    from math import floor, sqrt
    lastPrintedEvt = 0
    for entry in inF.sbitDataTree:
        # Get Values from tree for readability
        calEnable = entry.calEnable
        evtNum = entry.evtNum
        isValid = entry.isValid
        rate = entry.ratePulsed
        rateObsCTP7 = entry.rateObservedCTP7
        rateObsFPGA = entry.rateObservedFPGA
        rateObsVFAT = entry.rateObservedVFAT
        sbitSize = entry.sbitClusterSize
        vfatCH = entry.vfatCH
        vfatSBIT = entry.vfatSBIT
        vfatN = entry.vfatN
        vfatObs = entry.vfatObserved
        
        if( (evtNum % 1000) == 0 and lastPrintedEvt != evtNum):
            lastPrintedEvt = evtNum
            print("processed {0} events so far".format(entry.evtNum))

        # Skip this event because it's invaldi?
        if not isValid and not options.checkInvalid:
            continue

        # Track if sbit is mismatched
        if (vfatSBIT != floor(vfatCH/2)):
            if (len(dict_wrongPolarity[vfatN][vfatSBIT]) > 0): 
                dict_wrongPolarity[vfatN][vfatSBIT].append(vfatCH)
            else:
                dict_wrongPolarity[vfatN][vfatSBIT] = [ vfatCH ]

        # Summary Plots
        dict_h_vfatObsVsVfatPulsed[isValid][calEnable][rate].Fill(vfatN,vfatObs)

        # Track sbit multiplicity
        if evtNum in dict_validSbitsPerEvt[isValid][calEnable][rate][vfatN].keys():
            if isValid:
                dict_validSbitsPerEvt[isValid][calEnable][rate][vfatN][evtNum]+=1
        else:                                                                 
            if isValid:                                                       
                dict_validSbitsPerEvt[isValid][calEnable][rate][vfatN][evtNum]=1
            else:                                                             
                dict_validSbitsPerEvt[isValid][calEnable][rate][vfatN][evtNum]=0

        # Store sbit size
        if evtNum in dict_listSbitSizesPerEvt[isValid][calEnable][rate][vfatN].keys():
            if isValid:
                dict_listSbitSizesPerEvt[isValid][calEnable][rate][vfatN][evtNum].append(sbitSize)
        else:                                                                    
            if isValid:                                                          
                dict_listSbitSizesPerEvt[isValid][calEnable][rate][vfatN][evtNum] = [sbitSize]
            else:                                                                
                dict_listSbitSizesPerEvt[isValid][calEnable][rate][vfatN][evtNum] = []

        # VFAT lvl plots - 1D
        dict_h_sbitSize[isValid][calEnable][rate][vfatN].Fill(sbitSize)

        # VFAT lvl plots - 2D
        newPt = dict_g_rateObsCTP7VsRatePulsed[isValid][vfatN].GetN()
        dict_g_rateObsCTP7VsRatePulsed[isValid][vfatN].SetPoint(
                newPt,
                rate,
                rateObsCTP7)
        dict_g_rateObsCTP7VsRatePulsed[isValid][vfatN].SetPointError(
                newPt,
                0,
                sqrt(rateObsCTP7))

        newPt = dict_g_rateObsFPGAVsRatePulsed[isValid][vfatN].GetN()
        dict_g_rateObsFPGAVsRatePulsed[isValid][vfatN].SetPoint(
                newPt,
                rate,
                rateObsFPGA)
        dict_g_rateObsFPGAVsRatePulsed[isValid][vfatN].SetPointError(
                newPt,
                0,
                sqrt(rateObsFPGA))

        newPt = dict_g_rateObsVFATVsRatePulsed[isValid][vfatN].GetN()
        dict_g_rateObsVFATVsRatePulsed[isValid][vfatN].SetPoint(
                newPt,
                rate,
                rateObsVFAT)
        dict_g_rateObsVFATVsRatePulsed[isValid][vfatN].SetPointError(
                newPt,
                0,
                sqrt(rateObsVFAT))

        #dict_h_chanVsRatePulsed_ZRateObs

        dict_h_sbitObsVsChanPulsed[isValid][calEnable][rate][vfatN].Fill(vfatCH,vfatSBIT)

    print("Filling multiplicity distributions")
    for isValid in isValidValues:
        if not isValid and not options.checkInvalid:
            continue
        
        for calEnable in calEnableValues:
            for rate in ratesUsed:
                for vfat in range(0,24):
                    for event,multi in dict_validSbitsPerEvt[isValid][calEnable][rate][vfat].iteritems():
                        dict_h_sbitMulti[isValid][calEnable][rate][vfat].Fill(multi)

                        for size in dict_listSbitSizesPerEvt[isValid][calEnable][rate][vfat][event]:
                            dict_h_sbitMultiVsSbitSize[isValid][calEnable][rate][vfat].Fill(size,multi)
    
    print("Making summary plots")
    from gempython.gemplotting.utils.anautilities import make3x8Canvas, saveSummary
    for isValid in isValidValues:
        if not isValid and not options.checkInvalid:
            continue
        
        if isValid:
            strValidity="validSbits"
        else:
            strValidity="invalidSbits"

        # All Rates
        rateCanvas = make3x8Canvas(
                name="rateObservedVsRatePulsed_{0}".format(strValidity),
                initialContent=dict_g_rateObsCTP7VsRatePulsed[isValid],
                initialDrawOpt="APE1",
                secondaryContent=dict_g_rateObsFPGAVsRatePulsed[isValid],
                secondaryDrawOpt="PE1")
        rateCanvas = make3x8Canvas(
                name="",
                secondaryContent=dict_g_rateObsVFATVsRatePulsed[isValid],
                secondaryDrawOpt="PE1",
                canv=rateCanvas)
        
        # Make the legend
        rateLeg = r.TLegend(0.5,0.5,0.9,0.9)
        rateLeg.AddEntry(
                dict_g_rateObsCTP7VsRatePulsed[isValid][0],
                "CTP7 Rate",
                "LPE")
        rateLeg.AddEntry(
                dict_g_rateObsFPGAVsRatePulsed[isValid][0],
                "FPGA Rate",
                "LPE")
        rateLeg.AddEntry(
                dict_g_rateObsVFATVsRatePulsed[isValid][0],
                "VFAT Rate",
                "LPE")

        rateCanvas.cd(1)
        rateLeg.Draw("same")

        # Save Canvas
        rateCanvas.SaveAs("{0}/rateObservedVsRatePulsed_{1}.png".format(filename,strValidity))

        # CalDisable rate 0 case
        saveSummary(dict_h_sbitMulti[isValid][0][0], name="{0}/sbitMulti_{1}_calDisabled_0Hz.png".format(filename,strValidity), drawOpt="")
        saveSummary(dict_h_sbitSize[isValid][0][0], name="{0}/sbitSize_{1}_calDisabled_0Hz.png".format(filename,strValidity), drawOpt="")

        saveSummary(dict_h_sbitObsVsChanPulsed[isValid][0][0], name="{0}/sbitObsVsChanPulsed_{1}_calDisabled_0Hz.png".format(filename,strValidity), drawOpt="COLZ")
        saveSummary(dict_h_sbitMultiVsSbitSize[isValid][0][0], name="{0}/sbitMultiVsSbitSize_{1}_calDisabled_0Hz.png".format(filename,strValidity), drawOpt="COLZ")
        
        for idx,rate in enumerate(ratesUsed):
            # Sum over all rates
            if rate > 0:
                if (-1 not in dict_h_vfatObsVsVfatPulsed[isValid][1].keys()):
                    name = dict_h_vfatObsVsVfatPulsed[isValid][1][rate].GetName()
                    title = dict_h_vfatObsVsVfatPulsed[isValid][1][rate].GetTitle()
                    dict_h_vfatObsVsVfatPulsed[isValid][1][-1] = dict_h_vfatObsVsVfatPulsed[isValid][1][rate].Clone(name.replace("{0}Hz".format(int(rate)),"SumOfAllRates"))
                    dict_h_vfatObsVsVfatPulsed[isValid][1][-1].SetTitle(title.replace("Rate {0} Hz".format(int(rate)), "Sum of All Rates"))
                else:
                    dict_h_vfatObsVsVfatPulsed[isValid][1][-1].Add(dict_h_vfatObsVsVfatPulsed[isValid][1][rate])

                cloneExists = { vfat:False for vfat in range(0,24) }
                for vfat in range(0,24):
                    if ( not cloneExists[vfat] ):
                        cloneExists[vfat] = True

                        name = dict_h_sbitMulti[isValid][1][rate][vfat].GetName()
                        title = dict_h_sbitMulti[isValid][1][rate][vfat].GetTitle()
                        dict_h_sbitMulti[isValid][1][-1][vfat] = dict_h_sbitMulti[isValid][1][rate][vfat].Clone(name.replace("{0}Hz".format(int(rate)),"SumOfAllRates"))
                        dict_h_sbitMulti[isValid][1][-1][vfat].SetTitle(title.replace("Rate {0} Hz".format(int(rate)), "Sum of All Rates"))
                        
                        name = dict_h_sbitSize[isValid][1][rate][vfat].GetName()
                        title = dict_h_sbitSize[isValid][1][rate][vfat].GetTitle()
                        dict_h_sbitSize[isValid][1][-1][vfat] = dict_h_sbitSize[isValid][1][rate][vfat].Clone(name.replace("{0}Hz".format(int(rate)),"SumOfAllRates"))
                        dict_h_sbitSize[isValid][1][-1][vfat].SetTitle(title.replace("Rate {0} Hz".format(int(rate)), "Sum of All Rates"))

                        name = dict_h_sbitObsVsChanPulsed[isValid][1][rate][vfat].GetName()
                        title = dict_h_sbitObsVsChanPulsed[isValid][1][rate][vfat].GetTitle()
                        dict_h_sbitObsVsChanPulsed[isValid][1][-1][vfat] = dict_h_sbitObsVsChanPulsed[isValid][1][rate][vfat].Clone(name.replace("{0}Hz".format(int(rate)),"SumOfAllRates"))
                        dict_h_sbitObsVsChanPulsed[isValid][1][-1][vfat].SetTitle(title.replace("Rate {0} Hz".format(int(rate)), "Sum of All Rates"))

                        name = dict_h_sbitMultiVsSbitSize[isValid][1][rate][vfat].GetName()
                        title = dict_h_sbitMultiVsSbitSize[isValid][1][rate][vfat].GetTitle()
                        dict_h_sbitMultiVsSbitSize[isValid][1][-1][vfat] = dict_h_sbitMultiVsSbitSize[isValid][1][rate][vfat].Clone(name.replace("{0}Hz".format(int(rate)),"SumOfAllRates"))
                        dict_h_sbitMultiVsSbitSize[isValid][1][-1][vfat].SetTitle(title.replace("Rate {0} Hz".format(int(rate)), "Sum of All Rates"))
                    else:
                        dict_h_sbitMulti[isValid][1][-1][vfat].Add(dict_h_sbitMulti[isValid][1][rate][vfat])
                        dict_h_sbitSize[isValid][1][-1][vfat].Add(dict_h_sbitSize[isValid][1][rate][vfat])
                        dict_h_sbitObsVsChanPulsed[isValid][1][-1][vfat].Add(dict_h_sbitObsVsChanPulsed[isValid][1][rate][vfat])
                        dict_h_sbitMultiVsSbitSize[isValid][1][-1][vfat].Add(dict_h_sbitMultiVsSbitSize[isValid][1][rate][vfat])
        
                saveSummary(dict_h_sbitMulti[isValid][1][-1], name="{0}/sbitMulti_{1}_calEnabled_SumOfAllRates.png".format(filename,strValidity), drawOpt="")
                saveSummary(dict_h_sbitSize[isValid][1][-1], name="{0}/sbitSize_{1}_calEnabled_SumOfAllRates.png".format(filename,strValidity), drawOpt="")

                saveSummary(dict_h_sbitObsVsChanPulsed[isValid][1][-1], name="{0}/sbitObsVsChanPulsed_{1}_calEnabled_SumOfAllRates.png".format(filename,strValidity), drawOpt="COLZ")
                saveSummary(dict_h_sbitMultiVsSbitSize[isValid][1][-1], name="{0}/sbitMultiVsSbitSize_{1}_calEnabled_SumOfAllRates.png".format(filename,strValidity), drawOpt="COLZ")

    print("Storing TObjects in output TFile")
    # Per VFAT Plots
    for vfat in range(0,24):
        dirVFAT = outF.mkdir("VFAT{0}".format(vfat))

        for isValid in isValidValues:
            if not isValid and not options.checkInvalid:
                continue

            if isValid:
                strValidity="validSbits"
            else:
                strValidity="invalidSbits"
            dirIsValid = dirVFAT.mkdir(strValidity)
            dirIsValid.cd()
            dict_g_rateObsCTP7VsRatePulsed[isValid][vfat].Write()
            dict_g_rateObsFPGAVsRatePulsed[isValid][vfat].Write()
            dict_g_rateObsVFATVsRatePulsed[isValid][vfat].Write()

            for calEnable in calEnableValues:
                if calEnable:
                    strCalStatus="calEnabled"
                else:
                    strCalStatus="calDisabled"

                dirCalStatus = dirIsValid.mkdir(strCalStatus)
                if calEnable:
                    dirCalStatus.cd()
                    dict_h_sbitMulti[isValid][calEnable][-1][vfat].Write()
                    dict_h_sbitSize[isValid][calEnable][-1][vfat].Write()
                    dict_h_sbitObsVsChanPulsed[isValid][calEnable][-1][vfat].Write()
                    dict_h_sbitMultiVsSbitSize[isValid][calEnable][-1][vfat].Write()

                for rate in ratesUsed:
                    if ( not ( (calEnable and rate > 0) or (not calEnable and rate == 0.0) ) ):
                        continue

                    dirRate = dirCalStatus.mkdir("{0}Hz".format(int(rate)))
                    dirRate.cd()
                    dict_h_sbitMulti[isValid][calEnable][rate][vfat].Write()
                    dict_h_sbitSize[isValid][calEnable][rate][vfat].Write()
                    dict_h_sbitObsVsChanPulsed[isValid][calEnable][rate][vfat].Write()
                    dict_h_sbitMultiVsSbitSize[isValid][calEnable][rate][vfat].Write()

    # Summary Plots
    dirSummary = outF.mkdir("Summary")
    for isValid in isValidValues:
        if not isValid and not options.checkInvalid:
            continue

        if isValid:
            strValidity="validSbits"
        else:
            strValidity="invalidSbits"
        dirIsValid = dirSummary.mkdir(strValidity)

        for calEnable in calEnableValues:
            if calEnable:
                strCalStatus="calEnabled"
            else:
                strCalStatus="calDisabled"

            dirCalStatus = dirIsValid.mkdir(strCalStatus)

            if calEnable:
                dirCalStatus.cd()
                dict_h_vfatObsVsVfatPulsed[isValid][calEnable][-1].Write() 

            for rate in ratesUsed:
                if ( not ( (calEnable and rate > 0) or (not calEnable and rate == 0.0) ) ):
                    continue

                dirRate = dirCalStatus.mkdir("{0}Hz".format(int(rate)))
                dirRate.cd()
                dict_h_vfatObsVsVfatPulsed[isValid][calEnable][rate].Write() 

    # Close input TFile
    inF.Close()
    
    # Close output TFile
    outF.Close()
                
    print("List Of Mis-mapped Sbits")
    print("| vfatN | vfatSBIT | N_Mismatches |")
    print("| :---: | :------: | :----------: |")
    for vfat,dictBadSBits in dict_wrongPolarity.iteritems():
        for sbit,chanList in dictBadSBits.iteritems():
            print("| {0} | {1} | {2} |".format(
                vfat,
                sbit,
                len(chanList)))

    print("\nDone")
