import time

from ACQUAlyzer import Tags, Variables, HelperFunctions, Smd
from HSL.HelperTools.AcquaVariables import get_var_value, save_var, delete_vars
from HSL.HelperTools.SMDTags import get_tag_values
from HSL.MeasurementHandlings.Delay import set_d_script
from HEAD import const

import VoiceMeasurementSetting as vms
from VoiceMeasurementHelper import VoiceMeasurementHelper

class MeasurementSupport():
    # Run before each measurement
    @staticmethod
    def before_each_measurement():
        vms.check_global_var()
        if 'VoIP' == get_var_value(vms.var_call_net):
            save_var(vms.var_cmw_remo_ctr, False, const.evsUserDefined)
        vmh = VoiceMeasurementHelper()
        set_d_script(tagname_usecase='UseCase', tagname_bandwidth='Bandwidth', tagname_direction='Direction')
        if 'VoIP' != get_var_value(vms.var_call_net):
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
            vmh.set_bgn_setup()
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
        if 'loop' == get_var_value(vms.var_seq_test_mode):
            Smd.ResultComment = get_var_value(vms.var_call_net)+'_'+get_var_value(vms.var_call_vc)+'_'+VoiceMeasurementHelper.get_bandwidth()

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
            VoiceMeasurementHelper.stop_bgn_play()
