from ACQUAlyzer import Variables, Smd
from HSL.HelperTools.AcquaVariables import get_var_value, save_var
from HSL.HelperTools.UniversalQuestionnaire import run_universal_questionnaire_gui
from HEAD import const

# Defination of variable names
var_sys_labname = 'LabName'
var_sys_frontend = 'Frontend'
var_sys_simulator = 'Simulator'
var_sys_bgncon = 'BGNConnection'
var_sys_bgnsoft = 'BGNSoftware'
var_sys_maxuncer = 'max_uncertainty'
var_sys_dranad = 'D_RAN_AD'
var_sys_dranda = 'D_RAN_DA'
var_sys_dsrrea = 'D_SR_REA'
var_sys_desc = 'EquipDesc'
var_sys_bgnset_noise = 'BGNSetupNoise'
var_sys_bgnset_audio = 'BGNSetupAudio'
var_dut_remo_ctr = 'DUTRemoteControl'
var_dut_remo_ctr_mode = 'DUTRemoteControlMode'
var_dut_wifi_addr = 'DUTWifiAddr'
var_dut_hh_pos = 'DUTHHPos'
var_dut_uc = 'DUTUsecase'
var_dut_hs_type = 'DUTHSType'
var_cmw_remo_ctr = 'CMWRemoteControl'
var_call_net = 'CallNetwork'
var_call_vc = 'CallVocoder'
var_call_bw = 'CallBandwidth'
var_test_dflt_force = 'TestDefaultAppForce'
var_test_swb_base = 'TestSWBBase'
var_test_fb_base = 'TestFBBase'
var_test_net_flow = 'TestNetworkFlow'
var_seq_filter_mode = 'SeqFilterMode'
var_seq_test_mode = 'SeqTestMode'
var_seq_name = 'SeqName'
var_seq_uc = 'SeqUsecase'
# Default key variable values
var_dflt_sys_equip = {var_sys_labname: 'Audio Lab', var_sys_frontend: 'labCORE', var_sys_simulator: 'CMW500', var_sys_bgncon: 'USB', var_sys_bgnsoft: 'AutoEQ', var_sys_bgnset_audio: '3quest', var_sys_bgnset_noise: 'Default'}
var_dflt_sys_val = {var_sys_maxuncer: [20, 'ms'], var_sys_dranad: [0.46, 'ms'], var_sys_dranda: [0.67, 'ms'], var_sys_dsrrea: [1.13, 'ms']}
var_dflt_sys_desc = 'Default environment settings'
var_dflt_test = {var_test_dflt_force: '8N', var_test_swb_base: 'WB', var_test_fb_base: 'WB', var_test_net_flow: 'LTE_AMR_NB+WB,LTE_EVS_NB+WB,LTE_EVS_SWB'}

# Settings for sequence running
seq_filter_mode = {'Frame Title': 'Select sequence filter mode:',
            'VarName': var_seq_filter_mode,
            'Options': ['Lite version', 'Mini version', 'Full version'],
            'Values': ['lite', 'mini', 'full'],
            'Orientation': 'H'}
seq_test_mode = {'Frame Title': 'Select sequence test mode:',
            'VarName': var_seq_test_mode,
            'Options': ['Single mode', 'Loop mode'],
            'Values': ['single', 'loop'],
            'Orientation': 'H'}

# Common settings for sequences
network = {'Frame Title': 'Select network connection:',
            'VarName': var_call_net,
            'Options': ['GSM', 'WCDMA', 'LTE', '5G', 'WLAN', 'VoIP'],
            'Values': ['GSM', 'WCDMA', 'LTE', '5GNR', 'WLAN', 'VoIP'],
            'Orientation': 'H',
            'GrayOut': {var_seq_test_mode: ['loop']}}
vocoder = {'Frame Title': 'Select vocoder:',
            'VarName': var_call_vc,
            'Options': ['AMR', 'EVS'],
            'Values': ['AMR', 'EVS'],
            'Orientation': 'H',
            'GrayOutSingleRadioButton': {'EVS': {var_call_net: ['GSM', 'WCDMA']}},
            'GrayOut': {var_call_net: ['VoIP'], var_seq_test_mode: ['loop']}}
bandwidth = {'Frame Title': 'Select bandwidth:',
            'VarName': var_call_bw,
            'Options': ['NB+WB', 'NB', 'WB', 'SWB', 'FB', 'Wechat(WB)', 'Teams(SWB)'],
            'Values': ['NB+WB', 'NB', 'WB', 'SWB', 'FB', 'Wechat', 'Teams'],
            'Orientation': 'H',
            'GrayOutSingleRadioButton': {
                'NB+WB': {var_call_net: ['VoIP']},
                'NB': {var_call_net: ['VoIP']},
                'WB': {var_call_net: ['VoIP']},
                'SWB': {var_call_net: ['GSM', 'WCDMA','VoIP'],var_call_vc: ['AMR']},
                'FB': {var_call_net: ['GSM', 'WCDMA','VoIP'],var_call_vc: ['AMR']},
                'Wechat': {var_call_net: ['GSM', 'WCDMA','LTE','5GNR','WLAN']},
                'Teams': {var_call_net: ['GSM', 'WCDMA','LTE','5GNR','WLAN']}},
            'GrayOut': {var_seq_test_mode: ['loop']}}
usecase = {'Frame Title': 'Select usecase:',
            'VarName': var_dut_uc,
            'Options': ['All Usecase', 'Handset', 'Headset', 'Handsfree', 'Bluetooth', 'Headset Interface'],
            'Values': ['All', 'HA', 'HE', 'HH', 'BT', 'HI'],
            'Orientation': 'H'}
hs_type = {'Frame Title': 'Select headset type:',
            'VarName': var_dut_hs_type,
            'Options': ['Analog Binaural', 'Digital Binaural', 'Bluetooth Binaural', 'Analog Monaural', 'Digital Monaural', 'Bluetooth Monaural'],
            'Values': ['AnaBin', 'DigiBin', 'BTBin', 'AnaMono', 'DigiMono', 'BTMono'],
            'Orientation': 'H',
            'GrayOut': {var_dut_uc: ['HA','HH','BT','HI']}}

# Specific settings for TMO
phone_tier_tmo = {'Frame Title': 'Select tier of the phone:',
            'VarName': 'DUTTier',
            'Options': ['High-Tier Smartphone', 'Mid-Tier Smartphone', 'Value Smartphone', 'Feature Phone', 'Tablet/Laptop', 'Wearable'],
            'Values': ['highphone', 'midphone', 'valuephone', 'featurephone', 'tablet', 'wearable'],
            'Orientation': 'H'}
network_tmo = network.copy()
network_tmo.update({'Options': ['GSM 1900', 'UMTS Band 2 and 4', 'LTE(VoLTE) Band 2, 4, 12, 25, 66 and 71', '5G FR1 Sub6 VoNR n2, n25, n41, n66 and n71 / 5G FR2 mmW VoNR n258, n260 and n261', 'WLAN VoWiFi (WFC 2.0) 2.4GHz and 5GHz']})
mic_nc_ha = {'Frame Title': 'Select microphone number for noise cancellation in handset mode:',
            'VarName': 'DUTNCMicsHA',
            'Options': ['Two or More', 'Single'],
            'Values': ['2', '1'],
            'Orientation': 'H',
            'GrayOut': {var_dut_uc: ['HE','HH','BT','HI']}}
mic_nc_he = mic_nc_ha.copy()
mic_nc_he.update({'Frame Title': 'Select microphone number for noise cancellation in headset mode:', 'VarName': 'DUTNCMicsHE', 'GrayOut': {var_dut_uc: ['HA','HH','BT','HI']}})

def check_global_var(seq_name='Default', seq_uc='All'):
    if not Variables.Exists(var_sys_labname):
        set_const_var()
    if not Variables.Exists(var_seq_name):
        set_seq_tag(seq_name, seq_uc)
        set_global_config()

def set_const_var():
    if Variables.Exists(var_sys_desc):
        desc = get_var_value(var_sys_desc)
    elif Variables.Exists(f'system.{var_sys_desc}'):
        desc = get_var_value(f'system.{var_sys_desc}')
    else:
        desc = var_dflt_sys_desc
        save_var(f'system.{var_sys_desc}', desc, const.evsUserDefined, '', desc, '', False)
    for key, val in var_dflt_sys_equip.items():
        if not Variables.Exists(key):
            if Variables.Exists(f'system.{key}'):
                val = get_var_value(f'system.{key}')
            else:
                save_var(f'system.{key}', val, const.evsUserDefined, '', desc, '', False)
            save_var(key, val, const.evsUserDefined, '', desc, '', False)
    for key, val in var_dflt_sys_val.items():
        if not Variables.Exists(key):
            if Variables.Exists(f'system.{key}'):
                val[0] = Variables.GetItem(f'system.{key}').Value
                val[1] = Variables.GetItem(f'system.{key}').PhysicalUnit
            else:
                save_var(f'system.{key}', val[0], const.evsUserDefined, val[1], desc, '', False)
            save_var(key, val[0], const.evsUserDefined, val[1], desc, '', False)
    for key, val in var_dflt_test.items():
        if not Variables.Exists(f'system.{key}'):
            save_var(f'system.{key}', val, const.evsUserDefined, '', desc, '', False)

def set_seq_tag(seq_name, seq_uc):
    save_var(var_seq_name, seq_name, const.evsUserDefined, '', '', Smd.Title, False)
    save_var(var_seq_uc, seq_uc, const.evsUserDefined, '', '', Smd.Title, False)

def set_global_config():
    if not Variables.Exists(var_seq_test_mode) or 'loop' != get_var_value(var_seq_test_mode):
        seq_name = get_var_value(var_seq_name)
        seq_uc = get_var_value(var_seq_uc)
        usecase = usecase
        if 'All' != seq_uc and seq_uc in ['HA', 'HE', 'HH', 'BT', 'HI']:
            usecase.update({'GrayOut': {seq_test_mode: ['single','loop']}})
            save_var(var_dut_uc, seq_uc, const.evsUserDefined, '', '', Smd.Title, True)
        if 'TMO' == seq_name:
            run_universal_questionnaire_gui(seq_test_mode, phone_tier_tmo, network_tmo, vocoder, usecase, mic_nc_ha, mic_nc_he, hs_type)
        elif 'BigRule' == seq_name:
            run_universal_questionnaire_gui(seq_test_mode, network, vocoder, usecase, hs_type)
        else:
            run_universal_questionnaire_gui(seq_filter_mode, seq_test_mode, network, vocoder, bandwidth,usecase, hs_type)

def network_flow():
    if Variables.Exists(var_seq_test_mode) and 'loop' == get_var_value(var_seq_test_mode):
        networks = get_var_value(var_test_net_flow)
        if networks:
            networks = networks.split(',')
            save_var(var_test_net_flow, ','.join(networks[1:]), const.evsUserDefined, '', 'Networks for loop mode', Smd.Title, True)
            networks = networks[0].split('_')
            save_var(var_call_net, networks[0], const.evsUserDefined, '', 'Current network selected for loop mode', Smd.Title, True)
            save_var(var_call_vc, networks[1], const.evsUserDefined, '', 'Current vocoder selected for loop mode', Smd.Title, True)
            save_var(var_call_bw, networks[2], const.evsUserDefined, '', 'Current bandwidth selected for loop mode', Smd.Title, True)
        else:
            raise Exception('No more network defined for loop mode.')
