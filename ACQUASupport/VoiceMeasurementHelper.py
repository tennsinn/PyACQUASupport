import time

from ACQUAlyzer import Tags, Variables, HelperFunctions, Smd
from HSL.HelperTools.AcquaVariables import get_var_value, save_var
from HSL.HelperTools.SMDTags import get_tag_values
from HSL.MeasurementHandlings.Delay.SetEquipmentDelays import input_delay_radio_rcv, input_delay_radio_snd
from HSL.MeasurementHandlings.BGN.BGNRemote import RemoteControlHAE, BGNConnectionError
from HSL.MeasurementHandlings.BGN.BGNConfigurator import BGNConfigurator
from HEAD import const

import ADBPhoneControl as adbpc
import ACQUASupport.CMWController as cmwc
import ACQUASupport.VoiceMeasurementSetting as vms

class VoiceMeasurementConfig():
    timeout_dut = 5
    scenario = None
    usecase = None
    network = None
    vocoder = None
    bandwidth = None
    bitrate = None

    @classmethod
    def update_config(cls):
        cls.scenario = get_scenario()
        cls.usecase = get_usecase()
        cls.network = get_network()
        cls.vocoder = get_vocoder()
        cls.bandwidth = get_bandwidth()
        cls.bitrate = get_bitrate()

def get_scenario():
    scenario = {'HA':'earpiece', 'HE':'headset', 'HH':'speaker', 'BT':'bt_a2dp'}
    if Variables.Exists(vms.var_dut_hs_type):
        hstype = get_var_value(vms.var_dut_hs_type)
        if hstype.startswith('Digi'):
            scenario['HE'] = 'usb_headset'
        elif hstype.startswith('BT'):
            scenario['HE'] = 'bt_a2dp'
    return scenario

def get_usecase():
    if Tags.Exists('UseCase'):
        usecase = get_tag_values('UseCase')
        if usecase not in ['HA', 'HE', 'HH', 'BT']:
            raise Exception('Invalid UseCase.')
        else:
            return usecase
    else:
        raise Exception('Missing tag: UseCase.')

def get_network():
    if Variables.Exists(vms.var_call_net):
        network = get_var_value(vms.var_call_net)
    else:
        network = None
    return network

def get_vocoder():
    if Variables.Exists(vms.var_call_vc):
        vocoder = get_var_value(vms.var_call_vc)
    else:
        vocoder = None
    return vocoder

def get_bandwidth(base=True):
    if Tags.Exists('Bandwidth'):
        bandwidth = get_tag_values('Bandwidth')
        if base and Variables.Exists(vms.var_call_bw):
            bw = get_var_value(vms.var_call_bw)
            if ('SWB' == bw and bandwidth == get_defined_var(vms.var_test_swb_base)) or ('FB' == bw and bandwidth == get_defined_var(vms.var_test_fb_base)):
                bandwidth = bw
    else:
        bandwidth = None
    return bandwidth

def get_bitrate():
    if Tags.Exists('Bitrate'):
        bitrate = get_tag_values('Bitrate')
    else:
        bitrate = cmwc.use_default_bitrate()
    return bitrate

# Get var value
def get_defined_var(var_name):
    if Variables.Exists(var_name):
        return get_var_value(var_name)
    elif Variables.Exists(f'system.{var_name}'):
        return get_var_value(f'system.{var_name}')
    else:
        return False

def backup_delay():
    direction = get_tag_values('Direction')
    ucbw = get_usecase()+get_bandwidth(False)[0]
    if Variables.Exists(f'D_{direction}_EQ_{ucbw}'):
        deq = get_var_value(f'D_{direction}_EQ_{ucbw}')
        save_var(f'D_{direction}_EQ_{ucbw}_BAK', deq, const.evsMeasured, 'ms', 'Backup data of the original tested delay value.', Smd.Title, True)

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

def stop_bgn_play():
    bgn_config = BGNConfigurator()
    if bgn_config.has_controller():
        bgn_config.stop_bgn()

def set_bgn_setup():
    bgns = get_tag_values('BGNScenario')
    if bgns.startswith('NG:'):
        save_var('BGNSetup', get_var_value(vms.var_sys_bgnset_noise), const.evsUserDefined, '', 'Setup for Noise Generator.', Smd.Title, True)
    else:
        save_var('BGNSetup', get_var_value(vms.var_sys_bgnset_audio), const.evsUserDefined, '', 'Setup for loaded noise.', Smd.Title, True)

def set_force():
    force_cur = get_var_value('current_force') if Variables.Exists('current_force') else ''
    if Tags.Exists('AppForce'):
        force = get_tag_values('AppForce')
    elif Tags.Exists('Direction'):
        force = get_defined_var(vms.var_test_dflt_force)
    else:
        force = force_cur
    if force_cur != force:
        ret = HelperFunctions.MessageBox('Set the Application Force to '+force, 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True
        else:
            save_var('current_force', force, const.evsUserDefined)

def init_adb():
    # Check DUT Remote Control
    if not Smd.Cancel and get_defined_var(vms.var_dut_remo_ctr):
        if not adbpc.connected() and 'WiFi' == get_defined_var(vms.var_dut_remo_ctr_mode) and get_defined_var(vms.var_dut_wifi_addr):
            adbpc.cmd(['adb','connect', get_defined_var(vms.var_dut_wifi_addr)])
        # Notice if adb connection fail
        if not adbpc.connected():
            ret = HelperFunctions.MessageBox('Adb connection fail.\nPress YES to continue the test without DUT remote control.\nPress NO to stop the test.', 'Info', 0x41)
            if 2 == ret:
                Smd.Cancel = True
            else:
                save_var(vms.var_dut_remo_ctr, adbpc.connected(), const.evsUserDefined)

def init_cmw():
    # Check CMW Remote Control
    if not Smd.Cancel and get_defined_var(vms.var_cmw_remo_ctr):
        ret = 0
        if None in (VoiceMeasurementConfig.network, VoiceMeasurementConfig.vocoder, VoiceMeasurementConfig.bandwidth):
            ret = HelperFunctions.MessageBox('Missing CMW control vars, will disable CMW remote control.', 'Info', 0x41)
        else:
            cmwc.check_connection()
            if cmwc.CMWSettings.connected:
                cmwc.set_call_config(VoiceMeasurementConfig.network, VoiceMeasurementConfig.vocoder, VoiceMeasurementConfig.bandwidth, VoiceMeasurementConfig.bitrate)
            else:
                ret = HelperFunctions.MessageBox('CMW connection fail.\nPress YES to continue the test without CMW remote control.\nPress NO to stop the test.', 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True
        else:
            save_var(vms.var_cmw_remo_ctr, cmwc.CMWSettings.connected, const.evsUserDefined)

# Get volume range by adb
def get_volume_range(usecase, bandwidth):
    if Variables.Exists('VOL_MIN_'+usecase+bandwidth):
        MINVol = get_var_value('VOL_MIN_'+usecase+bandwidth)
    else:
        MINVol = int(adbpc.stream_volumes('VOICE_CALL')['Min'])
        save_var('VOL_MIN_'+usecase+bandwidth, MINVol, const.evsMeasured, '', 'Auto read from DUT via adb remote control.', Smd.Title, False)
    if Variables.Exists('VOL_MAX_'+usecase+bandwidth):
        MAXVol = get_var_value('VOL_MAX_'+usecase+bandwidth)
    else:
        MAXVol = int(adbpc.stream_volumes('VOICE_CALL')['Max'])
        save_var('VOL_MAX_'+usecase+bandwidth, MAXVol, const.evsMeasured, '', 'Auto read from DUT via adb remote control.', Smd.Title, False)
    if Variables.Exists('VOL_NOM_'+usecase+bandwidth):
        NOMVol = get_var_value('VOL_NOM_'+usecase+bandwidth)
    elif 'HH' == usecase:
        NOMVol = (MAXVol - MINVol) // 2 + 2
    else:
        NOMVol = (MAXVol - MINVol) // 2 + 1
        save_var('VOL_NOM_'+usecase+bandwidth, NOMVol, const.evsUserDefined, '', 'Defined based on DUT max and min volume.', Smd.Title, False)
    return MINVol, MAXVol, NOMVol

def set_volume():
    ret = 0
    vol = get_tag_values('VolumeCTRL')
    vol_cur = get_var_value('current_volume') if Variables.Exists('current_volume') else ''
    if vol_cur != vol:
        if adbpc.connected():
            minvol, maxvol, nomvol = get_volume_range(VoiceMeasurementConfig.usecase, VoiceMeasurementConfig.bandwidth)
            adbpc.set_vol_by_key('voice', get_scenario()[VoiceMeasurementConfig.usecase], vol, minvol, maxvol, nomvol)
        else:
            ret = HelperFunctions.MessageBox('Set the Volume to '+vol, 'Info', 0x41)
    if 2 == ret:
        Smd.Cancel = True
    else:
        save_var('current_volume', vol, const.evsUserDefined)

def check_call_alive():
    if (adbpc.connected() and '2' not in adbpc.call_state()) or (cmwc.CMWSettings.connected and not cmwc.get_established()):
        establish_call()
    if (adbpc.connected() and '2' not in adbpc.call_state()) or (cmwc.CMWSettings.connected and not cmwc.get_established()):
        ret = HelperFunctions.MessageBox('Call is not alive and auto connection fail.\nCheck the call connection first!', 'Info', 0x41)
        if 2 == ret:
            Smd.Cancel = True

def establish_call():
    ret = 0
    if not cmwc.CMWSettings.connected:
        ret = HelperFunctions.MessageBox('CMW not connected, check the connection first!\nEstablish the call manually, then start this test.', 'Info', 0x41)
    elif cmwc.get_established():
        ret = HelperFunctions.MessageBox('Call is still alive, release the call first!', 'Info', 0x41)
    elif not cmwc.get_registered():
        ret = HelperFunctions.MessageBox('Phone is not registered, check the phone connection!', 'Info', 0x41)
    else:
        cmwc.init_config()
        cmwc.put_mtcall()
        cnt = 0
        if adbpc.connected():
            # Pickup call via adb
            while adbpc.CallState.INCALL not in adbpc.call_state() and cnt < VoiceMeasurementConfig.timeout_dut:
                if adbpc.CallState.RING in adbpc.call_state():
                    adbpc.key_call()
                time.sleep(1)
                cnt += 1
        else:
            # Waiting for auto answer
            while not cmwc.get_established() and cnt < VoiceMeasurementConfig.timeout_dut:
                time.sleep(1)
                cnt += 1
        if not cmwc.get_established():
            ret = HelperFunctions.MessageBox('Fail to establish the call, check the calling step!', 'Info', 0x41)
        elif 'HH' == VoiceMeasurementConfig.usecase and get_defined_var(vms.var_dut_hh_pos):
            adbpc.input(['tap', get_defined_var(vms.var_dut_hh_pos)])
    if 2 == ret:
        Smd.Cancel = True
    else:
        save_var('current_bandwidth', VoiceMeasurementConfig.bandwidth, const.evsUserDefined)
        save_var('current_bitrate', VoiceMeasurementConfig.bitrate, const.evsUserDefined)

def update_call():
    ret = 0
    bandwidth_cur = get_var_value('current_bandwidth') if Variables.Exists('current_bandwidth') else ''
    bitrate_cur = get_var_value('current_bitrate') if Variables.Exists('current_bitrate') else ''
    if bandwidth_cur != VoiceMeasurementConfig.bandwidth or bitrate_cur != VoiceMeasurementConfig.bitrate:
        if cmwc.CMWSettings.connected:
            cmwc.update_call(VoiceMeasurementConfig.vocoder, VoiceMeasurementConfig.bandwidth, VoiceMeasurementConfig.bitrate)
        else:
            ret = HelperFunctions.MessageBox(f'Set the Bandwidth to {VoiceMeasurementConfig.bandwidth} and Bitrate to {VoiceMeasurementConfig.bitrate}.', 'Info', 0x41)
    if 2 == ret:
        Smd.Cancel = True
    else:
        save_var('current_bandwidth', VoiceMeasurementConfig.bandwidth, const.evsUserDefined)
        save_var('current_bitrate', VoiceMeasurementConfig.bitrate, const.evsUserDefined)

def release_call():
    ret = 0
    if adbpc.connected():
        cnt = 0
        while adbpc.CallState.INCALL in adbpc.call_state() and cnt < VoiceMeasurementConfig.timeout_dut:
            adbpc.key_endcall()
            time.sleep(1)
            cnt += 1
        if adbpc.CallState.INCALL in adbpc.call_state():
            ret = HelperFunctions.MessageBox('Fail to release the call via adb, release the call manually!', 'Info', 0x41)
    else:
         ret = HelperFunctions.MessageBox('Release the call manually!', 'Info', 0x41)
    if 2 == ret:
        Smd.Cancel = True

def reestablish_call():
    # Call via CMW
    release_call()
    if not Smd.Cancel:
        establish_call()
    if not Smd.Cancel and Tags.Exists('Number'):
        num = get_tag_values('Number')
        if cmwc.CMWSettings.connected:
            ulink = cmwc.get_delay_net('SND')
            dlink = cmwc.get_delay_net('RCV')
        else:
            dlink = input_delay_radio_rcv()
            ulink = input_delay_radio_snd()
        ucbw = VoiceMeasurementConfig.usecase+get_bandwidth(False)
        save_var(f'D_SND_NET_{ucbw}_{num}', ulink, const.evsMeasured, 'ms', 'Auto read from CMW500 via visa remote control.', Smd.Title, True)
        save_var(f'D_RCV_NET_{ucbw}_{num}', dlink, const.evsMeasured, 'ms', 'Auto read from CMW500 via visa remote control.', Smd.Title, True)

def check_audio_delay():
    if cmwc.CMWSettings.connected:
        direction = get_tag_values('Direction')
        ucbw = VoiceMeasurementConfig.usecase+get_bandwidth(False)[0]
        if Variables.Exists(f'D_{direction}_NET_{ucbw}'):
            dnet = get_var_value(f'D_{direction}_NET_{ucbw}')
        else:
            dnet = False
        dnet_cur = cmwc.get_delay_net(direction)
        # If fail to get the net delay, wait 3s and try again
        if not check_delay_valid(dnet_cur,dnet):
            time.sleep(3)
            dnet_cur = cmwc.get_delay_net(direction)
        # Reestablish the call if still fail to get delay or the delay changed too much
        if not check_delay_valid(dnet_cur,dnet):
            reestablish_call()
            time.sleep(3)
            dnet_cur = cmwc.get_delay_net(direction)
        if not check_delay_valid(dnet_cur,dnet):
            release_call()
            cmwc.signaling_off()
            time.sleep(5)
            cmwc.signaling_on()
            time.sleep(5)
            establish_call()
            time.sleep(3)
            dnet_cur = cmwc.get_delay_net(direction)
        if check_delay_valid(dnet_cur,dnet):
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

def check_delay_valid(dnet_cur, dnet=False):
    if not dnet_cur:
        return False
    if dnet_cur > 800 or dnet_cur < 0:
        return False
    if dnet and abs(dnet-dnet_cur) > 200:
        return False
    return True
