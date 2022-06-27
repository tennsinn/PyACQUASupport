import time
from HEAD.RadiotesterRemoteControl.CMWRemoteControlCommon import CMWPythonInterface as interface
import VoiceMeasurementHelper as vmh

cmw_bitrates = {
    'GSM_AMR_NB':{'12.2kbps':'C1220','10.2kbps':'C1020','7.95kbps':'C0795','7.4kbps':'C0740','6.7kbps':'C0670','5.9kbps':'C0590','5.15kbps':'C0515','4.75kbps':'C0475'},
    'GSM_AMR_WB':{'23.85kbps':'C2385','15.85kbps':'C1585','12.65kbps':'C1265','8.85kbps':'C0885','6.6kbps':'C0660'},
    'WCDMA_AMR_NB':{'12.2kbps':'A','10.2kbps':'B','7.95kbps':'C','7.4kbps':'D','6.7kbps':'E','5.9kbps':'F','5.15kbps':'G','4.75kbps':'H'},
    'WCDMA_AMR_WB':{'23.85kbps':'A','23.05kbps':'B','19.85kbps':'C','18.25kbps':'D','15.85kbps':'E','14.25kbps':'F','12.65kbps':'G','8.85kbps':'H','6.6kbps':'I'},
    'LTE_AMR_NB':{'4.75kbps':'1','5.15kbps':'2','5.9kbps':'3','6.7kbps':'4','7.4kbps':'5','7.95kbps':'6','10.2kbps':'7','12.2kbps':'8'},
    'LTE_AMR_WB':{'6.6kbps':'1','8.85kbps':'2','12.65kbps':'3','14.25kbps':'4','15.85kbps':'5','18.25kbps':'6','19.85kbps':'7','23.05kbps':'8','23.85kbps':'9'},
    'LTE_EVS_NB':{'5.9kbps':'R59','7.2kbps':'R72','8.0kbps':'R80','9.6kbps':'R96','13.2kbps':'R132','16.4kbps':'R164','24.4kbps':'R244'},
    'LTE_EVS_WB':{'5.9kbps':'R59','7.2kbps':'R72','8.0kbps':'R80','9.6kbps':'R96','13.2kbps':'R132','16.4kbps':'R164','24.4kbps':'R244','32.0kbps':'R320','48.0kbps':'R480','64.0kbps':'R640','96.0kbps':'R960','128.0kbps':'R1280'},
    'LTE_EVS_SWB':{'9.6kbps':'R96','13.2kbps':'R132','16.4kbps':'R164','24.4kbps':'R244','32.0kbps':'R320','48.0kbps':'R480','64.0kbps':'R640','96.0kbps':'R960','128.0kbps':'R1280'}
}

cmw_adcodecs = {'GSM_AMR_NB':'ANFG', 'GSM_AMR_WB':'AWF8', 'WCDMA_AMR_NB':'NARRow', 'WCDMA_AMR_WB':'WIDE', 
    'LTE_AMR_NB':'NARRowband', 'LTE_AMR_WB':'WIDeband', 'LTE_EVS_NB':'EVS', 'LTE_EVS_WB':'EVS', 'LTE_EVS_SWB':'EVS'}

def use_default_bitrate():
    if 'EVS' == vmh.CallConfig.vocoder:
        vmh.CallConfig.bitrate = '13.2kbps'
    elif 'NB' == vmh.CallConfig.bandwidth:
        vmh.CallConfig.bitrate = '12.2kbps'
    else:
        vmh.CallConfig.bitrate = '12.65kbps'
    return vmh.CallConfig.bitrate

def check_connection():
    try:
        interface.Connect()
        vmh.CallConfig.cmw_connected = True
    except:
        vmh.CallConfig.cmw_connected = False
    return vmh.CallConfig.cmw_connected

def set_call_config(network, vocoder, bandwidth, bitrate=None):
    if network in ['GSM', 'WCDMA', 'LTE']:
        vmh.CallConfig.network = network
    else:
        raise Exception('Do not support the selected network!')
    if 'AMR' == vocoder or ('LTE' == vmh.CallConfig.network and 'EVS' == vocoder):
        vmh.CallConfig.vocoder = vocoder
    else:
        raise Exception('Do not support the selected vocoder!')
    if ('AMR' == vmh.CallConfig.vocoder and bandwidth in ['NB','WB']) or ('EVS' == vmh.CallConfig.vocoder and bandwidth in ['NB','WB','SWB']):
        vmh.CallConfig.bandwidth = bandwidth
    else:
        raise Exception('Do not support the selected bandwidth!')
    if None == bitrate:
        vmh.CallConfig.bitrate = use_default_bitrate()
    elif bitrate in cmw_bitrates[vmh.CallConfig.key()]:
        vmh.CallConfig.bitrate = bitrate
    else:
        raise Exception('Do not support the selected bitrate!')

def get_delay_net(direction):
    val = False
    if 'GSM' == vmh.CallConfig.network or 'WCDMA' == vmh.CallConfig.network:
        delay = interface.QueryCommand(f'SENSe:{vmh.CallConfig.network}:SIGN1:CVINfo?')
        delay = delay.split(',')
        if 'SND' == direction and 'INV' != delay[2]:
            val = eval(delay[2])*1000
        elif 'RCV' == direction and 'INV' != delay[1]:
            val = eval(delay[1])*1000
    elif 'LTE' == vmh.CallConfig.network or '5GNR' == vmh.CallConfig.network or 'WLAN' == vmh.CallConfig.network:
        if 'SND' == direction:
            delay = interface.QueryCommand('READ:DATA:MEAS1:ADElay:ULINK?')
        else:
            delay = interface.QueryCommand('READ:DATA:MEAS1:ADElay:DLINK?')
        delay = delay.split(',')
        if 'INV' != delay[1]:
            val = eval(delay[1])*1000
    return val

def get_delay_tau():
    tau = False
    if 'LTE' == vmh.CallConfig.network or '5GNR' == vmh.CallConfig.network or 'WLAN' == vmh.CallConfig.network:
        tau = interface.QueryCommand('READ:DATA:MEAS1:ADElay:TAULink?')
        tau = tau.split(',')
        if 'INV' != tau[1]:
            tau = eval(tau[1])*1000
    return tau

def get_registered():
    registered = False
    if 'GSM' == vmh.CallConfig.network:
        ret = interface.QueryCommand('FETCh:GSM:SIGN1:CSWitched:STATe?')
        if 'SYNC' == ret:
            registered = True
    if 'WCDMA' == vmh.CallConfig.network:
        ret = interface.QueryCommand('FETCh:WCDMa:SIGN1:CSWitched:STATe?')
        if 'REG' == ret:
            registered = True
    elif 'LTE' == vmh.CallConfig.network:
        ret = interface.QueryCommand('SOURce:LTE:SIGN:CELL:STATe:ALL?')
        if ret == 'ON,ADJ':
            ret = interface.QueryCommand('FETCh:LTE:SIGN:PSWitched:STATe?')
            if 'ATT' == ret:
                ret = interface.QueryCommand('SENSe:DATA:CONTrol:IMS2:MOBile1:STATus?')
                if 'REG' == ret:
                    registered = True
    return registered

def get_established():
    established = False
    if 'GSM' == vmh.CallConfig.network or 'WCDMA' == vmh.CallConfig.network:
        ret = interface.QueryCommand(f'FETCh:{vmh.CallConfig.network}:SIGN1:CSWitched:STATe?')
        if 'CEST' == ret:
            established = True
    elif 'LTE' == vmh.CallConfig.network:
        ret = interface.QueryCommand('SENse:DATA:CONTrol:IMS2:RELease:LIST?')
        if ret != '':
            established = True
    return established

def put_mtcall():
    if 'GSM' == vmh.CallConfig.network:
        interface.WriteCommand('CALL:GSM:SIGN1:CSWitched:ACTion CONNect')
    elif 'WCDMA' == vmh.CallConfig.network:
        interface.WriteCommand('CALL:WCDMa:SIGN1:CSWitched:ACTion CONNect')
    elif 'LTE' == vmh.CallConfig.network:
        id = interface.QueryCommand('SENSe:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:DESTination:LIST?').split(',')[0]
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:DESTination {id}')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:TYPE AUDio')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:CALL')

def update_call(vocoder, bandwidth, bitrate):
    set_call_config(vmh.CallConfig.network, vocoder, bandwidth, bitrate)
    str_bitrate = cmw_bitrates[vmh.CallConfig.key()][bitrate]
    str_adcodec = cmw_adcodecs[vmh.CallConfig.key()]
    if 'GSM' == vmh.CallConfig.network:
        interface.WriteCommand('CALL:GSM:SIGN1:PSWitched:ACTion DISConnect')
        interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:TMODe {str_adcodec}')
    elif 'WCDMA' == vmh.CallConfig.network:
        interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:CODec {bandwidth}')
        interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:AMR:{str_adcodec} {str_bitrate}')
    elif 'LTE' == vmh.CallConfig.network:
        id = interface.QueryCommand('SENse:DATA:CONTrol:IMS2:RELease:LIST?').split(',')[0]
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:CALL:ID {id}')
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:ADCodec:TYPE {str_adcodec}')
        if 'AMR' == vocoder:
            for br_key, br_val in cmw_bitrates[vmh.CallConfig.key()].items():
                if br_key == bitrate:
                    interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:CODec{br_val}:ENABle ON')
                else:
                    interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:CODec{br_val}:ENABle OFF')
        elif 'EVS' == vocoder:
            interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:BWCommon {bandwidth}')
            interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:PERForm')

def _signaling(state='ON', err=True):
    if state not in ['ON','OFF']:
        raise Exception('Invalid signaling state!')
    cnt = 0
    net = {'GSM':'GSM', 'WCDMA':'WCDMa', 'LTE':'LTE'}
    while cnt < 60:
        time.sleep(1)
        cnt += 1
        ret = interface.QueryCommand(f'SOURce:{net[vmh.CallConfig.network]}:SIGN1:CELL:STATe:ALL?')
        ret = ret.split(',')
        if state != ret[0]:
            interface.WriteCommand(f'SOURce:{net[vmh.CallConfig.network]}:SIGN1:CELL:STATe {state}')
        elif 'ADJ' == ret[1]:
            return True
    if err:
        raise Exception(f'Failed to change the signaling state to {state}!')
    else:
        return False

def signaling_on():
    _signaling('ON')

def signaling_off():
    _signaling('OFF')

def init_config():
    str_adcodec = cmw_adcodecs[vmh.CallConfig.key()]
    str_bitrate = cmw_bitrates[vmh.CallConfig.key()][vmh.CallConfig.bitrate]
    interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:ILEVel 1.572')
    interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:OLEVel 1.572')
    interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:FILTer:HPASs H6')
    if 'GSM' == vmh.CallConfig.network:
        interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "GSM Sig1"')
        interface.WriteCommand('CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:SIGNaling:MODE LTRR')
        rate_conf = {'NB':'GMSK', 'WB':'EPSK'}
        rate_conf2 = {'NB':{'C1220':'4', 'C0795':'3', 'C0590':'2', 'C0475':'1'}, 'WB':{'C2385':'4', 'C1585':'3', 'C1265':'2', 'C0660':'1'}}
        str_rate_conf = ', '.join(rate_conf2[vmh.CallConfig.bandwidth].keys())
        interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:RSET:{vmh.CallConfig.bandwidth}:FRATe:{rate_conf[vmh.CallConfig.bandwidth]} {str_rate_conf}')
        interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:CMODe:{vmh.CallConfig.bandwidth}:FRATe:{rate_conf[vmh.CallConfig.bandwidth]}:DL {rate_conf2[vmh.CallConfig.bandwidth][str_bitrate]}')
        interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:CMODe:{vmh.CallConfig.bandwidth}:FRATe:{rate_conf[vmh.CallConfig.bandwidth]}:UL {rate_conf2[vmh.CallConfig.bandwidth][str_bitrate]}')
        interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe ON')
    elif 'WCDMA' == vmh.CallConfig.network:
        interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "WCDMA Sig1"')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:UETerminate VOICe')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:SRBData R13K6, R13K6')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:CSWitched:CRELease NORMal')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:SOURce SPEech')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:DTX OFF')
        interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:CODec {vmh.CallConfig.bandwidth}')
        interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:AMR:{str_adcodec} {str_bitrate}')
        interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:TFCI OFF')
        interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe ON')
    elif 'LTE' == vmh.CallConfig.network:
        interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe OFF')
        interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "DAU IMS Server"')
        interface.WriteCommand('SOURce:DATA:CONTrol:STATe ON')
        interface.WriteCommand('SOURce:DATA:CONTrol:IMS2:STATe ON')
        # Config Virtual Subscriber1
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:BEHaviour ANSWer')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SIGNalingtyp PRECondit')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:BEARer ON')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:VIDeo ON')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:STANdalone ON')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:SESSionmode ON')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:FILetransfer ON')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:FORCemocall ON')
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:ADCodec:TYPE {str_adcodec}')
        if 'AMR' == vmh.CallConfig.vocoder:
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:ALIGnment OCTetaligned')
            for br_key, br_val in cmw_bitrates[vmh.CallConfig.key()].items():
                if br_key == vmh.CallConfig.bitrate:
                    interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:CODec{br_val}:ENABle ON')
                else:
                    interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:CODec{br_val}:ENABle OFF')
        else:
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:STARtmode EPRimary')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:HFONly BOTH')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:DTX DISable')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:DTXRecv NP')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:SYNCh:SELect COMMon')
            interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:BWCommon {vmh.CallConfig.bandwidth}')
            interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:CMR ENABle')
            interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:CHAWmode DIS')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:VIDeo:CODec H264')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:VIDeo:ATTRibutes ""')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MEDiaendpoin AUDioboard')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AUDioboard:CONFig INST1, OFF, FREE, FREE, SDP')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:IO:MODE:CONFig EVSamrwb')
        # Config Update
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:CALL:TYPE AUDio')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:VIDeo:CODec H264')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:ALIGnment OCT')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:STARtmode EPRimary')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:HFONly BOTH')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:DTX DISable')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:DTXRecv NP')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:SYNCh:SELect COMMon')
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:BWCommon {vmh.CallConfig.bandwidth}')
        interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:CMR ENABle')
        interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:CHAWmode DIS')
        interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe ON')
    signaling_on()
