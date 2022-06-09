import time

from ACQUAlyzer import Tags, Variables, HelperFunctions, Smd
from HSL.HelperTools.AcquaVariables import get_var_value, save_var, delete_vars
from HSL.HelperTools.SMDTags import get_tag_values
from HSL.HelperTools.UniversalQuestionnaire import run_universal_questionnaire_gui
from HSL.MeasurementHandlings.Delay import set_d_script
from HSL.MeasurementHandlings.Delay.SetEquipmentDelays import input_delay_radio_rcv, input_delay_radio_snd
from HSL.MeasurementHandlings.BGN.BGNRemote import RemoteControlHAE, BGNConnectionError
from HSL.MeasurementHandlings.BGN.BGNConfigurator import BGNConfigurator
from HEAD import const

from AdbPhoneControl import *
from CMWController import *

class MeasurementConst():
    var_sys_labname = 'LabName'
    var_sys_frontend = 'Frontend'
    var_sys_simulator = 'Simulator'
    var_sys_bgncon = 'BGNConnection'
    var_sys_bgnsoft = 'BGNSoftware'
    var_sys_maxuncer = 'max_uncertainty'
    var_sys_dranad = 'D_RAN_AD'
    var_sys_dranda = 'D_RAN_DA'
    var_sys_dsrrea = 'D_SR_REA'
    var_sys_equipdesc = 'EquipDesc'
    var_dut_remo_ctr = 'DUTRemoteControl'
    var_dut_remo_ctr_mode = 'DUTRemoteControlMode'
    var_dut_wifi_addr = 'DUTWifiAddr'
    var_dut_hh_pos = 'DUTHHPos'
    var_dut_tier = 'DUTTier'
    var_dut_mic_nc = 'DUTNCMics'
    var_dut_uc = 'DUTUseCase'
    var_hs_type = 'HSType'
    var_cmw_remo_ctr = 'CMWRemoteControl'
    var_call_net = 'CallNetwork'
    var_call_vc = 'CallVocoder'
    var_call_bw = 'CallBandwidth'
    var_test_dflt_force = 'TestDefaultAppForce'
    var_test_swb_base = 'TestSWBBase'
    var_test_fb_base = 'TestFBBase'
    var_seq_filter_mode = 'SeqFilterMode'
    var_seq_test_mode = 'SeqTestMode'
    var_seq_name = 'SeqName'
    var_seq_uc = 'SeqUsecase'

    var_equip_dflt_list = {var_sys_labname: 'Audio Lab', var_sys_frontend: 'labCORE', var_sys_simulator: 'CMW500', var_sys_bgncon: 'USB', var_sys_bgnsoft: 'AutoEQ'}
    var_equip_dflt_val = {var_sys_maxuncer: [20, 'ms'], var_sys_dranad: [0.46, 'ms'], var_sys_dranda: [0.67, 'ms'], var_sys_dsrrea: [1.13, 'ms']}
    var_equip_dflt_desc = 'Default environment settings'

class VoiceMeasurementSetting():
    # Settings for sequence running
    seq_filter_mode = {'Frame Title': 'Select sequence filter mode:',
                'VarName': MeasurementConst.var_seq_filter_mode,
                'Options': ['Lite version', 'Mini version', 'Full version'],
                'Values': ['lite', 'mini', 'full'],
                'Orientation': 'H'}
    # Todo: add loop mode functions
    seq_test_mode = {'Frame Title': 'Select sequence test mode:',
                'VarName': MeasurementConst.var_seq_test_mode,
                'Options': ['Single mode', 'Loop mode'],
                'Values': ['single', 'loop'],
                'Orientation': 'H'}

    # Common settings for sequences
    network = {'Frame Title': 'Select network connection:',
                'VarName': MeasurementConst.var_call_net,
                'Options': ['GSM', 'WCDMA', 'LTE', '5G', 'WLAN', 'VoIP'],
                'Values': ['GSM', 'WCDMA', 'LTE', '5GNR', 'WLAN', 'VoIP'],
                'Orientation': 'H'}
    vocoder = {'Frame Title': 'Select vocoder:',
                'VarName': MeasurementConst.var_call_vc,
                'Options': ['AMR', 'EVS'],
                'Values': ['AMR', 'EVS'],
                'Orientation': 'H',
                'GrayOutSingleRadioButton': {'EVS': {MeasurementConst.var_call_net: ['GSM', 'WCDMA']}},
                'GrayOut': {MeasurementConst.var_call_net: ['VoIP']}}
    bandwidth = {'Frame Title': 'Select bandwidth:',
                'VarName': MeasurementConst.var_call_bw,
                'Options': ['NB+WB', 'NB', 'WB', 'SWB', 'FB', 'Wechat(WB)', 'Teams(SWB)'],
                'Values': ['NB+WB', 'NB', 'WB', 'SWB', 'FB', 'Wechat', 'Teams'],
                'Orientation': 'H',
                'GrayOutSingleRadioButton': {
                    'NB+WB': {MeasurementConst.var_call_net: ['VoIP']},
                    'NB': {MeasurementConst.var_call_net: ['VoIP']},
                    'WB': {MeasurementConst.var_call_net: ['VoIP']},
                    'SWB': {MeasurementConst.var_call_net: ['GSM', 'WCDMA','VoIP'],MeasurementConst.var_call_vc: ['AMR']},
                    'FB': {MeasurementConst.var_call_net: ['GSM', 'WCDMA','VoIP'],MeasurementConst.var_call_vc: ['AMR']},
                    'Wechat': {MeasurementConst.var_call_net: ['GSM', 'WCDMA','LTE','5GNR','WLAN']},
                    'Teams': {MeasurementConst.var_call_net: ['GSM', 'WCDMA','LTE','5GNR','WLAN']}},
                'GrayOut': {MeasurementConst.var_seq_test_mode: ['loop']}}
    usecase = {'Frame Title': 'Select usecase:',
                'VarName': MeasurementConst.var_dut_uc,
                'Options': ['All Usecase', 'Handset', 'Headset', 'Handsfree', 'Bluetooth', 'Headset Interface'],
                'Values': ['All', 'HA', 'HE', 'HH', 'BT', 'HI'],
                'Orientation': 'H'}
    hs_type = {'Frame Title': 'Select headset type:',
                'VarName': MeasurementConst.var_hs_type,
                'Options': ['Analog Binaural', 'Digital Binaural', 'Bluetooth Binaural', 'Analog Monaural', 'Digital Monaural', 'Bluetooth Monaural'],
                'Values': ['AnaBin', 'DigiBin', 'BTBin', 'AnaMono', 'DigiMono', 'BTMono'],
                'Orientation': 'H',
                'GrayOut': {MeasurementConst.var_dut_uc: ['HA','HH','BT','HI']}}

    # Specific settings for TMO
    phone_tier_tmo = {'Frame Title': 'Select tier of the phone:',
                'VarName': MeasurementConst.var_dut_tier,
                'Options': ['High-Tier Smartphone', 'Mid-Tier Smartphone', 'Value Smartphone', 'Feature Phone', 'Tablet/Laptop', 'Wearable'],
                'Values': ['highphone', 'midphone', 'valuephone', 'featurephone', 'tablet', 'wearable'],
                'Orientation': 'H'}
    network_tmo = network.copy()
    network_tmo.update({'Options': ['GSM 1900', 'UMTS Band 2 and 4', 'LTE(VoLTE) Band 2, 4, 12, 25, 66 and 71', '5G FR1 Sub6 VoNR n2, n25, n41, n66 and n71 / 5G FR2 mmW VoNR n258, n260 and n261', 'WLAN VoWiFi (WFC 2.0) 2.4GHz and 5GHz']})
    mic_nc_ha = {'Frame Title': 'Select microphone number for noise cancellation in handset mode:',
                'VarName': MeasurementConst.var_dut_mic_nc+'_HA',
                'Options': ['Two or More', 'Single'],
                'Values': ['2', '1'],
                'Orientation': 'H',
                'GrayOut': {MeasurementConst.var_dut_uc: ['HE','HH','BT','HI']}}
    mic_nc_he = mic_nc_ha.copy()
    mic_nc_he.update({'Frame Title': 'Select microphone number for noise cancellation in headset mode:', 'VarName': MeasurementConst.var_dut_mic_nc+'_HE', 'GrayOut': {MeasurementConst.var_dut_uc: ['HA','HH','BT','HI']}})

    @staticmethod
    def check_global_var(seq_name='Default', seq_uc='All'):
        if not Variables.Exists(MeasurementConst.var_sys_labname):
            VoiceMeasurementSetting.set_const_var()
        if not Variables.Exists(MeasurementConst.var_seq_name):
            VoiceMeasurementSetting.set_seq_tag(seq_name, seq_uc)
            VoiceMeasurementSetting.set_global_config()

    @staticmethod
    def set_const_var():
        if Variables.Exists(MeasurementConst.var_sys_equipdesc):
            desc = get_var_value(MeasurementConst.var_sys_equipdesc)
        elif Variables.Exists('System.'+MeasurementConst.var_sys_equipdesc):
            desc = get_var_value('System.'+MeasurementConst.var_sys_equipdesc)
        else:
            desc = MeasurementConst.var_equip_dflt_desc
        for key, val in MeasurementConst.var_equip_dflt_list.items():
            if not Variables.Exists(key):
                if Variables.Exists('System.'+key):
                    val = get_var_value('System.'+key)
                save_var(key, val, const.evsUserDefined, '', desc, '', False)
        for key, val in MeasurementConst.var_equip_dflt_val.items():
            if not Variables.Exists(key):
                if Variables.Exists('System.'+key):
                    val = get_var_value('System.'+key)
                save_var(key, val[0], const.evsUserDefined, val[1], desc, '', False)

    @staticmethod
    def set_seq_tag(seq_name, seq_uc):
        save_var(MeasurementConst.var_seq_name, seq_name, const.evsUserDefined, '', '', Smd.Title, False)
        save_var(MeasurementConst.var_seq_uc, seq_uc, const.evsUserDefined, '', '', Smd.Title, False)

    @staticmethod
    def set_global_config():
        seq_name = get_var_value(MeasurementConst.var_seq_name)
        seq_uc = get_var_value(MeasurementConst.var_seq_uc)
        if 'All' != seq_uc and seq_uc in ['HA', 'HE', 'HH', 'BT', 'HI']:
            usecase = VoiceMeasurementSetting.usecase
            usecase.update({'GrayOut': {VoiceMeasurementSetting.seq_test_mode: ['single','loop']}})
            save_var(MeasurementConst.var_dut_uc, seq_uc, const.evsUserDefined, '', '', Smd.Title, True)
        if 'TMO' == seq_name:
            run_universal_questionnaire_gui(VoiceMeasurementSetting.seq_test_mode, VoiceMeasurementSetting.phone_tier_tmo, VoiceMeasurementSetting.network_tmo, VoiceMeasurementSetting.vocoder, usecase, VoiceMeasurementSetting.mic_nc_ha, VoiceMeasurementSetting.mic_nc_he, VoiceMeasurementSetting.hs_type)
        elif 'BigRule' == seq_name:
            run_universal_questionnaire_gui(VoiceMeasurementSetting.seq_test_mode, VoiceMeasurementSetting.network, VoiceMeasurementSetting.vocoder, usecase, VoiceMeasurementSetting.hs_type)
        else:
            run_universal_questionnaire_gui(VoiceMeasurementSetting.seq_filter_mode, VoiceMeasurementSetting.seq_test_mode, VoiceMeasurementSetting.network, VoiceMeasurementSetting.vocoder, VoiceMeasurementSetting.bandwidth,usecase, VoiceMeasurementSetting.hs_type)

class VoiceMeasurementHelper():
    def __init__(self):
        self.timeout_dut = 5
        self.usecase = self.get_usecase()
        self.network = self.get_network()
        self.vocoder = self.get_vocoder()
        self.bandwidth = self.get_bandwidth()
        self.bitrate = self.get_bitrate()
        self.init_adb()
        self.init_cmw()

    @staticmethod
    def get_scenario():
        scenario = {'HA':'earpiece', 'HE':'headset', 'HH':'speaker', 'BT':'bt_a2dp'}
        if Variables.Exists(MeasurementConst.var_hs_type):
            hstype = get_var_value(MeasurementConst.var_hs_type)
            if hstype.startswith('Digi'):
                scenario['HE'] = 'usb_headset'
            elif hstype.startswith('BT'):
                scenario['HE'] = 'bt_a2dp'
        return scenario

    @staticmethod
    def get_usecase():
        if Tags.Exists('UseCase'):
            usecase = get_tag_values('UseCase')
            if usecase not in ['HA', 'HE', 'HH', 'BT']:
                raise Exception('Invalid UseCase.')
            else:
                return usecase
        else:
            raise Exception('Missing tag: UseCase.')

    @staticmethod
    def get_network():
        if Variables.Exists(MeasurementConst.var_call_net):
            network = get_var_value(MeasurementConst.var_call_net)
        else:
            network = None
        return network

    @staticmethod
    def get_vocoder():
        if Variables.Exists(MeasurementConst.var_call_vc):
            vocoder = get_var_value(MeasurementConst.var_call_vc)
        else:
            vocoder = None
        return vocoder

    @staticmethod
    def get_bandwidth(base=True):
        if Tags.Exists('Bandwidth'):
            bandwidth = get_tag_values('Bandwidth')
            if base and Variables.Exists(MeasurementConst.var_call_bw):
                bw = get_var_value(MeasurementConst.var_call_bw)
                if ('SWB' == bw and bandwidth == VoiceMeasurementHelper.get_defined_var(MeasurementConst.var_test_swb_base)) or ('FB' == bw and bandwidth == VoiceMeasurementHelper.get_defined_var(MeasurementConst.var_test_fb_base)):
                    bandwidth = bw
        else:
            bandwidth = None
        return bandwidth

    @staticmethod
    def get_bitrate():
        if Tags.Exists('Bitrate'):
            bitrate = get_tag_values('Bitrate')
        else:
            network = VoiceMeasurementHelper.get_network()
            vocoder = VoiceMeasurementHelper.get_vocoder()
            bandwidth = VoiceMeasurementHelper.get_bandwidth()
            bitrate = CMWController.get_default_bitrate(network, vocoder, bandwidth)
        return bitrate

    def init_adb(self, sn=None):
        # Check DUT Remote Control
        if not Smd.Cancel and self.get_defined_var(MeasurementConst.var_dut_remo_ctr):
            if not AdbPhoneControl.connected() and 'WiFi' == self.get_defined_var(MeasurementConst.var_dut_remo_ctr_mode) and self.get_defined_var(MeasurementConst.var_dut_wifi_addr):
                AdbPhoneControl.cmd(['adb','connect', self.get_defined_var(MeasurementConst.var_dut_wifi_addr)])
            # Notice if adb connection fail
            if not AdbPhoneControl.connected():
                ret = HelperFunctions.MessageBox('Adb connection fail.\nPress YES to continue the test without DUT remote control.\nPress NO to stop the test.', 'Info', 0x41)
                if 2 == ret:
                    Smd.Cancel = True
                else:
                    save_var(MeasurementConst.var_dut_remo_ctr, AdbPhoneControl.connected(), const.evsUserDefined)

    def init_cmw(self):
        self.cmw = CMWController()
        # Check CMW Remote Control
        if not Smd.Cancel and self.get_defined_var(MeasurementConst.var_cmw_remo_ctr):
            ret = 0
            if None in (self.network, self.vocoder, self.bandwidth):
                ret = HelperFunctions.MessageBox('Missing CMW control vars, will disable CMW remote control.', 'Info', 0x41)
            else:
                self.cmw.check_connection()
                if self.cmw.connected:
                    self.cmw.set_call_config(self.network, self.vocoder, self.bandwidth, self.bitrate)
                else:
                    ret = HelperFunctions.MessageBox('CMW connection fail.\nPress YES to continue the test without CMW remote control.\nPress NO to stop the test.', 'Info', 0x41)
            if 2 == ret:
                Smd.Cancel = True
            else:
                save_var(MeasurementConst.var_cmw_remo_ctr, self.cmw.connected, const.evsUserDefined)

    def establish_call(self):
        ret = 0
        if not self.cmw.connected:
            ret = HelperFunctions.MessageBox('CMW not connected, check the connection first!\nEstablish the call manually, then start this test.', 'Info', 0x41)
        elif self.cmw.get_established():
            ret = HelperFunctions.MessageBox('Call is still alive, release the call first!', 'Info', 0x41)
        elif not self.cmw.get_registered():
            ret = HelperFunctions.MessageBox('Phone is not registered, check the phone connection!', 'Info', 0x41)
        else:
            self.cmw.init_config()
            self.cmw.put_mtcall()
            cnt = 0
            if AdbPhoneControl.connected():
                # Pickup call via adb
                while AdbCallState.INCALL not in AdbPhoneControl.call_state() and cnt < self.timeout_dut:
                    if AdbCallState.RING in AdbPhoneControl.call_state():
                        AdbPhoneControl.key_call()
                    time.sleep(1)
                    cnt += 1
            else:
                # Waiting for auto answer
                while not self.cmw.get_established() and cnt < self.timeout_dut:
                    time.sleep(1)
                    cnt += 1
            if not self.cmw.get_established():
                ret = HelperFunctions.MessageBox('Fail to establish the call, check the calling step!', 'Info', 0x41)
            elif 'HH' == self.usecase and self.get_defined_var(MeasurementConst.var_dut_hh_pos):
                AdbPhoneControl.input(['tap', self.get_defined_var(MeasurementConst.var_dut_hh_pos)])
        if 2 == ret:
            Smd.Cancel = True
        else:
            save_var('current_bandwidth', self.bandwidth, const.evsUserDefined)
            save_var('current_bitrate', self.bitrate, const.evsUserDefined)

    # Get var value
    @staticmethod
    def get_defined_var(var_name):
        if Variables.Exists(var_name):
            return get_var_value(var_name)
        elif Variables.Exists('System.'+var_name):
            return get_var_value('System.'+var_name)
        else:
            return False

    # Get volume range by adb
    def get_volume_range(self, usecase, bandwidth):
        if Variables.Exists('VOL_MIN_'+usecase+bandwidth):
            MINVol = get_var_value('VOL_MIN_'+usecase+bandwidth)
        else:
            MINVol = int(AdbPhoneControl.stream_volumes('VOICE_CALL')['Min'])
            save_var('VOL_MIN_'+usecase+bandwidth, MINVol, const.evsMeasured, '', 'Auto read from DUT via adb remote control.', Smd.Title, False)
        if Variables.Exists('VOL_MAX_'+usecase+bandwidth):
            MAXVol = get_var_value('VOL_MAX_'+usecase+bandwidth)
        else:
            MAXVol = int(AdbPhoneControl.stream_volumes('VOICE_CALL')['Max'])
            save_var('VOL_MAX_'+usecase+bandwidth, MAXVol, const.evsMeasured, '', 'Auto read from DUT via adb remote control.', Smd.Title, False)
        if Variables.Exists('VOL_NOM_'+usecase+bandwidth):
            NOMVol = get_var_value('VOL_NOM_'+usecase+bandwidth)
        elif 'HH' == usecase:
            NOMVol = (MAXVol - MINVol) // 2 + 2
        else:
            NOMVol = (MAXVol - MINVol) // 2 + 1
            save_var('VOL_NOM_'+usecase+bandwidth, NOMVol, const.evsUserDefined, '', 'Defined based on DUT max and min volume.', Smd.Title, False)
        return MINVol, MAXVol, NOMVol

    def set_volume(self):
        ret = 0
        vol = get_tag_values('VolumeCTRL')
        vol_cur = get_var_value('current_volume') if Variables.Exists('current_volume') else ''
        if vol_cur != vol:
            if AdbPhoneControl.connected():
                minvol, maxvol, nomvol = self.get_volume_range(self.usecase, self.bandwidth)
                AdbPhoneControl.set_vol_by_key('voice', self.get_scenario()[self.usecase], vol, minvol, maxvol, nomvol)
            else:
                ret = HelperFunctions.MessageBox('Set the Volume to '+vol, 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True
        else:
            save_var('current_volume', vol, const.evsUserDefined)

    def set_force(self):
        force_cur = get_var_value('current_force') if Variables.Exists('current_force') else ''
        if Tags.Exists('AppForce'):
            force = get_tag_values('AppForce')
        elif Tags.Exists('Direction'):
            force = self.get_defined_var(MeasurementConst.var_test_dflt_force)
        else:
            force = force_cur
        if force_cur != force:
            ret = HelperFunctions.MessageBox('Set the Application Force to '+force, 'Info', 0x41)
            if 2 == ret:
                Smd.Cancel = True
            else:
                save_var('current_force', force, const.evsUserDefined)

    def update_call(self):
        ret = 0
        bandwidth_cur = get_var_value('current_bandwidth') if Variables.Exists('current_bandwidth') else ''
        bitrate_cur = get_var_value('current_bitrate') if Variables.Exists('current_bitrate') else ''
        if bandwidth_cur != self.bandwidth or bitrate_cur != self.bitrate:
            if self.cmw.connected:
                self.cmw.update_call(self.vocoder, self.bandwidth, self.bitrate)
            else:
                ret = HelperFunctions.MessageBox(f'Set the Bandwidth to {self.bandwidth} and Bitrate to {self.bitrate}.', 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True
        else:
            save_var('current_bandwidth', self.bandwidth, const.evsUserDefined)
            save_var('current_bitrate', self.bitrate, const.evsUserDefined)

    def release_call(self):
        ret = 0
        if AdbPhoneControl.connected():
            cnt = 0
            while AdbCallState.INCALL in AdbPhoneControl.call_state() and cnt < self.timeout_dut:
                AdbPhoneControl.key_endcall()
                time.sleep(1)
                cnt += 1
            if AdbCallState.INCALL in AdbPhoneControl.call_state():
                ret = HelperFunctions.MessageBox('Fail to release the call via adb, release the call manually!', 'Info', 0x41)
        else:
             ret = HelperFunctions.MessageBox('Release the call manually!', 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True

    def reestablish_call(self):
        # Call via CMW
        self.release_call()
        if not Smd.Cancel:
            self.establish_call()
        if not Smd.Cancel and Tags.Exists('Number'):
            num = get_tag_values('Number')
            if self.cmw.connected:
                ulink = self.cmw.get_delay_net('SND')
                dlink = self.cmw.get_delay_net('RCV')
            else:
                dlink = input_delay_radio_rcv()
                ulink = input_delay_radio_snd()
            ucbw = self.usecase+self.get_bandwidth(False)
            save_var(f'D_SND_NET_{ucbw}_{num}', ulink, const.evsMeasured, 'ms', 'Auto read from CMW500 via visa remote control.', Smd.Title, True)
            save_var(f'D_RCV_NET_{ucbw}_{num}', dlink, const.evsMeasured, 'ms', 'Auto read from CMW500 via visa remote control.', Smd.Title, True)

    def check_audio_delay(self, err=False):
        if self.cmw.connected:
            direction = get_tag_values('Direction')
            dnet_cur = self.cmw.get_delay_net(direction)
            # If fail, wait for 3s and try again
            if not dnet_cur:
                time.sleep(3)
                dnet_cur = self.cmw.get_delay_net(direction)
            # If fail, re-establisheh the call and try again
            if not dnet_cur:
                self.reestablish_call()
                time.sleep(3)
                dnet_cur = self.cmw.get_delay_net(direction)
            if dnet_cur:
                ucbw = self.usecase+VoiceMeasurementHelper.get_bandwidth(False)[0]
                if Variables.Exists(f'D_{direction}_NET_{ucbw}'):
                    dnet = get_var_value(f'D_{direction}_NET_{ucbw}')
                else:
                    dnet = dnet_cur
                # Warning if the delay changed too much
                if err and (dnet > 800 or dnet < 0 or abs(dnet-dnet_cur) > 200):
                    raise Exception('Audio delay change too much, please retest the overall delay!')
                save_var(f'D_{direction}_NET_{ucbw}', dnet_cur, const.evsMeasured, 'ms', 'Auto read from CMW500 via visa remote control.', Smd.Title, True)
                # Auto adjust the EQ delay based on the change of NET delay
                if Variables.Exists(f'D_{direction}_EQ_{ucbw}'):
                    deq = get_var_value(f'D_{direction}_EQ_{ucbw}')
                    deq_cur = deq - dnet + dnet_cur
                    if deq_cur < 0:
                        raise Exception('Invalid audio delay value!')
                    save_var(f'D_{direction}_EQ_{ucbw}', deq_cur, const.evsMeasured, 'ms', 'Adjusted value based on the change of net delay.', Smd.Title, True)
            else:
                raise Exception('Fail to get audio delay, please check the connection!')

    @staticmethod
    def backup_delay():
        direction = get_tag_values('Direction')
        ucbw = VoiceMeasurementHelper.get_usecase()+VoiceMeasurementHelper.get_bandwidth(False)[0]
        if Variables.Exists(f'D_{direction}_EQ_{ucbw}'):
            deq = get_var_value(f'D_{direction}_EQ_{ucbw}')
            save_var(f'D_{direction}_EQ_{ucbw}_BAK', deq, const.evsMeasured, 'ms', 'Backup data of the original tested delay value.', Smd.Title, True)

    def check_call_alive(self):
        if (AdbPhoneControl.connected() and '2' not in AdbPhoneControl.call_state()) or (self.cmw.connected and not self.cmw.get_established()):
            self.establish_call()
        if (AdbPhoneControl.connected() and '2' not in AdbPhoneControl.call_state()) or (self.cmw.connected and not self.cmw.get_established()):
            ret = HelperFunctions.MessageBox('Call is not alive and auto connection fail.\nCheck the call connection first!', 'Info', 0x41)
            if 2 == ret:
                Smd.Cancel = True

    @staticmethod
    def check_LabBGN_conn():
        remote_control = RemoteControlHAE(auto_connect=False)
        ret = 0
        try:
            remote_control.connect()
            ret = remote_control.send_command('?')
            if 'HAE' not in ret:
                raise BGNConnectionError
        except BGNConnectionError:
            ret = HelperFunctions.MessageBox('BGN connection error!\n1. Connect labBGN to ACQUA PC via USB cable\n2. Switch on labBGN\n3. Open AutoEQ\n4. Enable HAERemote', 'Info', 0x41)
        else:
            remote_control.disconnect()
        finally:
            remote_control = None
        if 2 == ret:
            Smd.Cancel = True

    @staticmethod
    def stop_LabBGN():
        bgn_config = BGNConfigurator()
        if bgn_config.has_controller():
            bgn_config.stop_bgn()

    @staticmethod
    def setup_bgn():
        bgns = get_tag_values('BGNScenario')
        if bgns.startswith('NG:'):
            save_var('BGNSetup', 'Default', const.evsUserDefined, '', 'Setup for other tests.', Smd.Title, True)
        else:
            save_var('BGNSetup', '3quest', const.evsUserDefined, '', 'Setup for 3Quest test.', Smd.Title, True)

class MeasurementSupport():
    # Run before each measurement
    @staticmethod
    def before_each_measurement():
        VoiceMeasurementSetting.check_global_var()
        if 'VoIP' == get_var_value(MeasurementConst.var_call_net):
            save_var(MeasurementConst.var_cmw_remo_ctr, False, const.evsUserDefined)
        vmh = VoiceMeasurementHelper()
        set_d_script(tagname_usecase='UseCase', tagname_bandwidth='Bandwidth', tagname_direction='Direction')
        if 'VoIP' != get_var_value(MeasurementConst.var_call_net):
            vmh.cmw.interface.Connect()
            # Check call alive or establish call
            if not Smd.Cancel:
                vmh.check_call_alive()
            # Bandwidth and Bitrate setting
            if not Smd.Cancel:
                vmh.update_call()
            if not Smd.Cancel and Tags.Exists('Direction'):
                vmh.check_audio_delay()
        # DUT volume control
        if not Smd.Cancel and Tags.Exists('VolumeCTRL'):
            vmh.set_volume()
        # Check apllication force
        if not Smd.Cancel and 'HA' == vmh.usecase:
            vmh.set_force()
        if not Smd.Cancel and Tags.Exists('BGNScenario'):
            vmh.setup_bgn()
        # Apply defined action
        if not Smd.Cancel and Tags.Exists('Action'):
            ret = 0
            act = get_tag_values('Action').split(',')
            if 're-establish' in act:
                vmh.reestablish_call()
            if 'charging' in act:
                ret = HelperFunctions.MessageBox('Start charging the phone.', 'Info', 0x41)
            if 2 == ret:
                Smd.Cancel = True
        if 'VoIP' != get_var_value(MeasurementConst.var_call_net):
            vmh.cmw.interface.Disconnect()

    # Run after each measurement
    @staticmethod
    def after_each_measurement():
        if Tags.Exists('Action'):
            act = get_tag_values('Action')
            ret = 0
            if 'charging' in act:
                ret = HelperFunctions.MessageBox('Stop charging the phone.', 'Info', 0x41)
            if 'backup_delay' in act:
                VoiceMeasurementHelper.backup_delay()
            if 2 == ret:
                Smd.Cancel = True

    # Run after canceled measurement
    @staticmethod
    def after_canceled_measurement():
        if Variables.Exists('current_force'):
            delete_vars('current_force')
        if Variables.Exists('current_volume'):
            delete_vars('current_volume')
        if Variables.Exists('current_bandwidth'):
            delete_vars('current_bandwidth')
        if Variables.Exists('current_bitrate'):
            delete_vars('current_bitrate')
        if Tags.Exists('BGNScenario'):
            VoiceMeasurementHelper.stop_LabBGN()
