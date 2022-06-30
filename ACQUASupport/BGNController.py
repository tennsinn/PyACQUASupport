import numpy as np
import pandas as pd
from pathlib import Path

from ACQUAlyzer import Smd, SubProject, Tags, HelperFunctions
from HEAD import const
import HEAD.HdfIO.MarkTools as mt
from HSL.MeasurementHandlings.BGN.BGNConfigurator import BGNConfigurator, BGNSettings
from HSL.MeasurementHandlings.BGN.BGNRemote import RemoteControlHAE, BGNConnectionError
from HSL.ReportEditor import ExistingReport
from HSL.HelperTools.AcquaVariables import get_var_value, save_var
from HSL.HelperTools.SMDTags import get_tag_values

import ACQUASupport.VoiceMeasurementSetting as vms

# Provide Mapping from BGNConfigurator keywords to Tag names
BGNTags = {'bgn_scenario': 'BGNScenario',
           'loops': 'BGNRepeats',
           'gain': 'BGNGain',
           'use_case': 'UseCase'}
# Provide BGN Mapping for AUTO mode
bgn_map_file = str(Path(SubProject.Path) / 'BGNMapping.xlsx')

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

def get_bgn_mapping(file_path: str):
    if not Path(file_path).is_file():
        raise FileNotFoundError('Could not find BGN Mapping file at\n\'{}\''.format(file_path))
    return pd.read_excel(file_path, sheet_name='Mapping', index_col=[0, 1])

def get_bgn_tags(tag_map: dict):
    # check input requirements
    try:
        scenario_tag = tag_map['bgn_scenario']
    except KeyError:
        raise Exception('The usage of a Tag for the BGN Scenario is not optional for remote controlled BGN.')
    settings = dict()

    # ### Get BGN Scenario ###
    if Tags.Value(scenario_tag):
        bgn_scenario = Tags.Value(scenario_tag)
        if bgn_scenario.startswith('AUTO:'):
            # Get Use Case
            try:
                usecase_tag = tag_map['use_case']
            except KeyError:
                raise Exception('The usage of a Tag, specifying the UseCase, is not optional in \'Auto\' mode.')

            if Tags.Value(usecase_tag):
                use_case = Tags.Value(usecase_tag)
                if use_case in ['HE', 'HA']:
                    use_case = 'HA'
                elif use_case in ['WW', 'HH']:
                    use_case = 'HH'
                else:
                    raise ValueError('The value of Tag {!r} must be in {!r}, but is {!r}!'
                                     .format(usecase_tag, {'HA', 'HE', 'HH', 'WW'}, use_case))
                settings['use_case'] = use_case
            else:
                raise Exception('Tag \'{}\' is not optional when using \'AUTO\' mode.'.format(usecase_tag))
            settings['bgn_scenario'] = bgn_scenario
        elif bgn_scenario.startswith('NG:'):
            settings['bgn_scenario'] = bgn_scenario.split(':')[1]
        else:
            settings['bgn_scenario'] = bgn_scenario
    else:
        raise Exception('Could not find tag \'{}\', or tag is empty.'.format(scenario_tag))

    # Get BGN Repeats
    loops_tag = tag_map.get('loops')
    if loops_tag and Tags.Value(loops_tag):
        try:
            settings['loops'] = int(Tags.Value(loops_tag))
        except ValueError:
            raise TypeError('Tag value \'{}\' is invalid for the number of BGN repeats!\nPlease change the value of '
                            '\'{}\' to either\n'
                            '    - a positive integer number,\n'
                            '    - 0 for infinite repeats or a\n'
                            '    - negative integer number for automatic calculation of the repeats number.\n'
                            'Note that automatic calculation is only available in \'AUTO\' mode and will default to '
                            'infinite repeats otherwise.'
                            .format(Tags.Value(loops_tag), loops_tag, scenario_tag))
    else:
        if bgn_scenario.startswith('AUTO:'):
            settings['loops'] = -1
        else:
            settings['loops'] = 0

    # Get Gain
    gain_tag = tag_map.get('gain')
    if gain_tag and Tags.Value(gain_tag):
        try:
            settings['gain'] = int(Tags.Value(gain_tag))
        except ValueError:
            raise TypeError('Tag value \'{}\' is invalid for gain!\nPlease change the value of \'{}\' to a numeric '
                            'value'.format(Tags.Value(gain_tag), gain_tag))

    return settings


def automatic_config(bgn_config: BGNConfigurator, tags: dict, bgn_map_file: str):
    bgn_map = get_bgn_mapping(bgn_map_file)

    # Change bgn_scenario
    bgn_software = bgn_config[BGNSettings.Software]
    bgn_key = tags['bgn_scenario'].split(':')[1]
    try:
        tags['bgn_scenario'] = bgn_map.loc[(bgn_key, bgn_software), tags['use_case']]
    except KeyError:
        raise Exception('Could not find BGN scenario {!r} in {!r}'.format(bgn_key, bgn_map_file))

    # Change number of repeats
    if tags['loops'] < 0:
        source_duration = mt.SignalDuration(Smd.SourceFilename)
        bgn_duration = bgn_map.loc[(bgn_key, bgn_software), 'Duration']
        tags['loops'] = int(np.ceil(source_duration / bgn_duration))

    # delete use_case, no longer needed
    del tags['use_case']

    return tags


def before_bgn_main():
    set_bgn_setup()
    bgn_config = BGNConfigurator()
    if bgn_config.has_controller():
        tags = get_bgn_tags(BGNTags)
        if 'use_case' in tags.keys():
            tags = automatic_config(bgn_config, tags, bgn_map_file)
        bgn_config.set_up_bgn(**tags)
        state = bgn_config.start_bgn()
        if state != 'OK':
            raise Exception('Could not start BGN. Response from {} is:\n{}'.format(bgn_config[BGNSettings.Software], state))

def add_bgn_info_to_report(bgn_config: BGNConfigurator, tags: dict):
    report = ExistingReport()
    section = report.section(const.estMfe3Settings)
    section.title('BGN Settings')

    bgn_software = bgn_config[BGNSettings.Software]
    bgn_scenario = tags['bgn_scenario']
    bgn_repeats = tags['loops'] if tags['loops'] > 0 else 'infinite'
    bgn_gain = tags.get('gain', None)
    if bgn_gain is not None:
        report_string = '{:<20}{:<42}{:<20}{:<20}\n{:<25}{:<47}{:<27}{:<20}'\
            .format('BGNSoftware:', bgn_software, 'BGN Scenario:', bgn_scenario, 'Repeats:', bgn_repeats, 'Gain:', bgn_gain)
    else:
        report_string = '{:<20}{:<42}{:<20}{:<20}\n{:<25}{:<47}' \
            .format('BGNSoftware:', bgn_software, 'BGN Scenario:', bgn_scenario, 'Repeats:', bgn_repeats)
    section.add_string(report_string)

def after_bgn_main():
    bgn_config = BGNConfigurator()
    if bgn_config.has_controller():
        bgn_config.stop_bgn()
        # Get Tag stuff for report
        tags = get_bgn_tags(BGNTags)
        if 'use_case' in tags.keys():
            tags = automatic_config(bgn_config, tags, bgn_map_file)
        add_bgn_info_to_report(bgn_config, tags)
