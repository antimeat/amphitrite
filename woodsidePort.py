### Specific function for generating partitions as required for Mermaid Sound

import readSpectrum

def mermaidSound(filename):

    ## create object for the partitions
    P0_ = 7
    P1_st = 7
    P1_ed = 13
    P2_st = 13
    P2_ed = 18
    P3_ = 16.5

    P0 = readSpectrum.onePartition(filename, P0_)
    P1 = readSpectrum.rangePartition(filename, P1_ed, P1_st)
    P2 = readSpectrum.rangePartition(filename, P2_ed, P2_st)
    P3 = readSpectrum.onePartition(filename, P3_)

    ws = readSpectrum.noPartition(filename)

    #append partitioned variables to file
    ws['hs_P0'] = P0.hs_sea
    ws.hs_P0.attrs['standard_name'] = ws.hs_P0.attrs['standard_name']+'_P0_partition'
    ws['hmax_P0'] = P0.hmax_sea
    ws.hmax_P0.attrs['standard_name'] = ws.hmax_P0.attrs['standard_name']+'_P0_partition'
    ws['tp_P0'] = P0.spec.tp(smooth=False).fillna(1 / P0.freq.max())
    ws.tp_P0.attrs['standard_name'] = ws.tp_P0.attrs['standard_name']+'_P0_partition'
    ws['tm01_P0'] = P0.tm01_sea
    ws.tm01.attrs['standard_name'] = ws.tm01.attrs['standard_name']+'_P0_partition'
    ws['tm02_P0'] = P0.tm02_sea
    ws.tm02_P0.attrs['standard_name'] = ws.tm02.attrs['standard_name']+'_P0_partition'
    ws['dp_P0'] = P0.dp_sea
    ws.dp_P0.attrs['standard_name'] = ws.dp_P0.attrs['standard_name']+'_P0_partition'
    ws['dm_P0'] = P0.dm_sea
    ws.dm_P0.attrs['standard_name'] = ws.dm_P0.attrs['standard_name']+'_P0_partition'
    ws['dspr_P0'] = P0.dspr_sea
    ws.dspr_P0.attrs['standard_name'] = ws.dspr_P0.attrs['standard_name']+'_P0_partition'

    #append partitioned variables to file
    ws['hs_P1'] = P1.hs
    ws.hs_P1.attrs['standard_name'] = ws.hs_P1.attrs['standard_name']+'_P1_partition'
    ws['hmax_P1'] = P1.hmax
    ws.hmax_P1.attrs['standard_name'] = ws.hmax_P1.attrs['standard_name']+'_P1_partition'
    ws['tp_P1'] = P1.spec.tp(smooth=False).fillna(1 / P1.freq.max())
    ws.tp_P1.attrs['standard_name'] = ws.tp_P1.attrs['standard_name']+'_P1_partition'
    ws['tm01_P1'] = P1.tm01
    ws.tm01_P1.attrs['standard_name'] = ws.tm01_P1.attrs['standard_name']+'_P1_partition'
    ws['tm02_P1'] = P1.tm02
    ws.tm02_P1.attrs['standard_name'] = ws.tm02_P1.attrs['standard_name']+'_P1_partition'
    ws['dpm_P1'] = P1.dp
    ws.dp_P1.attrs['standard_name'] = ws.dp_P1.attrs['standard_name']+'_P1_partition'
    ws['dm_P1'] = P1.dm
    ws.dm_P1.attrs['standard_name'] = ws.dm_P1.attrs['standard_name']+'_P1_partition'
    ws['dspr_P1'] = P1.dspr
    ws.dspr_P1.attrs['standard_name'] = ws.dspr_P1.attrs['standard_name']+'_P1_partition'

    #append partitioned variables to file
    ws['hs_P2'] = P2.hs
    ws.hs_P2.attrs['standard_name'] = ws.hs_P2.attrs['standard_name']+'_P2_partition'
    ws['hmax_P2'] = P2.hmax
    ws.hmax_P2.attrs['standard_name'] = ws.hmax_P2.attrs['standard_name']+'_P2_partition'
    ws['tp_P2'] = P2.spec.tp(smooth=False).fillna(1 / P2.freq.max())
    ws.tp_P2.attrs['standard_name'] = ws.tp_P2.attrs['standard_name']+'_P2_partition'
    ws['tm01_P2'] = P2.tm01
    ws.tm01_P2.attrs['standard_name'] = ws.tm01_P2.attrs['standard_name']+'_P2_partition'
    ws['tm02_P2'] = P2.tm02
    ws.tm02_P2.attrs['standard_name'] = ws.tm02_P2.attrs['standard_name']+'_P2_partition'
    ws['dp_P2'] = P2.dp
    ws.dpm_P2.attrs['standard_name'] = ws.dpm_P2.attrs['standard_name']+'_P2_partition'
    ws['dm_P2'] = P2.dm
    ws.dm_P2.attrs['standard_name'] = ws.dm_P2.attrs['standard_name']+'_P2_partition'
    ws['dspr_P2'] = P2.dspr
    ws.dspr_P2.attrs['standard_name'] = ws.dspr_P2.attrs['standard_name']+'_P2_partition'

    #append partitioned variables to file
    ws['hs_P3'] = P3.hs_sw
    ws.hs_P3.attrs['standard_name'] = ws.hs_P3.attrs['standard_name']+'_P3_partition'
    ws['hmax_P3'] = P3.hmax_sw
    ws.hmax_P3.attrs['standard_name'] = ws.hmax_P3.attrs['standard_name']+'_P3_partition'
    ws['tp_P3'] = P3.spec.tp(smooth=False).fillna(1 / P3.freq.max())
    ws.tp_P3.attrs['standard_name'] = ws.tp_P3.attrs['standard_name']+'_P3_partition'
    ws['tm01_P3'] = P3.tm01_sw
    ws.tm01_P3.attrs['standard_name'] = ws.tm01_P3.attrs['standard_name']+'_P3_partition'
    ws['tm02_P3'] = P3.tm02_sw
    ws.tm02_P3.attrs['standard_name'] = ws.tm02_P3.attrs['standard_name']+'_P3_partition'
    ws['dp_P3'] = P3.dpm_sw
    ws.dpm_P3.attrs['standard_name'] = ws.dpm_P3.attrs['standard_name']+'_P3_partition'
    ws['dm_P3'] = P3.dm_sw
    ws.dm_P3.attrs['standard_name'] = ws.dm_P3.attrs['standard_name']+'_P3_partition'
    ws['dspr_P3'] = P3.dspr_sw
    ws.dspr_P3.attrs['standard_name'] = ws.dspr_P3.attrs['standard_name']+'_P3_partition'
    
    
    return ws
