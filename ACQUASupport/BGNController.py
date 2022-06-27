from ACQUAlyzer import Smd, HelperFunctions
from HEAD import const
from HSL.MeasurementHandlings.BGN.BGNConfigurator import BGNConfigurator
from HSL.MeasurementHandlings.BGN.BGNRemote import RemoteControlHAE, BGNConnectionError
from HSL.HelperTools.AcquaVariables import get_var_value, save_var
from HSL.HelperTools.SMDTags import get_tag_values

import ACQUASupport.VoiceMeasurementSetting as vms

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
