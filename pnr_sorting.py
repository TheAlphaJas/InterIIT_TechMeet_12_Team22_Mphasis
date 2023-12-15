import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def map_from_sheet(pnr):
    old_keys = pnr.copy()
    new_dict = {}
    for key in old_keys:
        new_dict[key.lower()] = pnr.pop(key)
    new_dict['pnr_no'] = new_dict.pop('recloc')
    new_dict['pnr_cabin'] = new_dict.pop('cos_cd')
    return new_dict
def calc_score(pnr, pnr_scoring, pnr_datasheet):
    passengers = []
    pnr_datasheet = pnr_datasheet[pnr_datasheet['RECLOC']==pnr['pnr_no']]
    for i in range(len(pnr_datasheet)):
        passengers.append(pnr_datasheet.iloc[i].to_dict())
    score = 0
    for p in passengers:
        score += pnr_scoring[0] * (0 if p['SSR_CODE_CD1'] in [np.nan] else 1)
    if pnr['pnr_cabin'] == 'FirstClass':
        score += pnr_scoring[1]
    elif pnr['pnr_cabin'] == 'BusinessClass':
        score += pnr_scoring[2]
    elif pnr['pnr_cabin'] == 'PremiumEconomyClass':
        score += pnr_scoring[3]
    elif pnr['pnr_cabin'] == 'EconomyClass':
        score += pnr_scoring[4]
    score += pnr_scoring[5] * (pnr['seg_total'] - pnr['seg_seq'])
    if pnr['pax_cnt'] > 1:
        score += pnr_scoring[6]
    score += pnr_scoring[7] * pnr['pax_cnt']
    for p in passengers:
        if p['TierLevel'] == 'Presidential Platinum':
            score += pnr_scoring[8]
        elif p['TierLevel'] == 'Platinum':
            score += pnr_scoring[9]
        elif p['TierLevel'] == 'Gold':
            score += pnr_scoring[10]
        elif p['TierLevel'] == 'Silver':
            score += pnr_scoring[11]
    return score
def list_of_pnrs(flight_num, dept_date, pnr_scoring, pnr_list, pnr_datasheet, min_time, max_time):
    affected_pnrs = []
    for i in range(len(pnr_list)):
        #print(type(pnr_list['FLT_NUM'].iloc[i]))
        if int(pnr_list['FLT_NUM'].iloc[i]) == flight_num and pd.Timestamp(pnr_list['DEP_DT'].iloc[i]) == dept_date:
            one_pnr = pnr_list.iloc[i].to_dict()
            one_pnr = map_from_sheet(one_pnr)
            one_pnr['score'] = calc_score(one_pnr, pnr_scoring, pnr_datasheet)
            temp = pnr_list.loc[(pnr_list['RECLOC'] == one_pnr['pnr_no']) & (pnr_list['SEG_SEQ'] == one_pnr['seg_seq']+1)]
            if temp.empty:
                one_pnr['max_time'] = max_time
            else:
                one_pnr['max_time'] = min(max_time, pd.Timestamp(temp['DEP_DTMZ'].iloc[0]))
            temp = pnr_list.loc[(pnr_list['RECLOC'] == one_pnr['pnr_no']) & (pnr_list['SEG_SEQ'] == one_pnr['seg_seq']-1)]
            if temp.empty:
                one_pnr['min_time'] = min_time
            else:
                one_pnr['min_time'] = max(min_time, pd.Timestamp(temp['ARR_DTMZ'].iloc[0]))
            affected_pnrs.append(one_pnr)
    affected_pnrs.sort(key=lambda x: -x['score'])
    return affected_pnrs
# affected_pnrs = list_of_pnrs(2504, pd.Timestamp(2024, 4, 3), pnr_scoring, pnr_list, pnr_datasheet, pd.Timestamp(2024, 4, 3), pd.Timestamp(2024, 4, 3))