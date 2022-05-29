import time
from HEAD.RadiotesterRemoteControl.CMWRemoteControlCommon import *

class CMWController():
    def __init__(self):
        self.interface = CMWPythonInterface()
        self.connected = False
        self.bitrates= {
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
        self.adcodecs = {'GSM_AMR_NB':'ANFG', 'GSM_AMR_WB':'AWF8', 'WCDMA_AMR_NB':'NARRow', 'WCDMA_AMR_WB':'WIDE', 'LTE_AMR_NB':'NARRowband', 'LTE_AMR_WB':'WIDeband', 'LTE_EVS_NB':'EVS', 'LTE_EVS_WB':'EVS', 'LTE_EVS_SWB':'EVS'}
        self.network = None
        self.vocoder = None
        self.bandwidth = None
        self.bitrate = None

    @staticmethod
    def get_default_bitrate(network, vocoder, bandwidth):
        if 'EVS' == vocoder:
            return '13.2kbps'
        elif 'NB' == bandwidth:
            return '12.2kbps'
        else:
            return '12.65kbps'

    def set_call_config(self, network, vocoder, bandwidth, bitrate=None):
        if network in ['GSM', 'WCDMA', 'LTE']:
            self.network = network
        else:
            raise Exception('Do not support the selected network!')
        if 'AMR' == vocoder or ('LTE' == self.network and 'EVS' == vocoder):
            self.vocoder = vocoder
        else:
            raise Exception('Do not support the selected vocoder!')
        if ('AMR' == self.vocoder and bandwidth in ['NB','WB']) or ('EVS' == self.vocoder and bandwidth in ['NB','WB','SWB']):
            self.bandwidth = bandwidth
        else:
            raise Exception('Do not support the selected bandwidth!')
        if None == bitrate:
            self.bitrate = self.get_default_bitrate()
        elif bitrate in self.bitrates[self.key]:
            self.bitrate = bitrate
        else:
            raise Exception('Do not support the selected bitrate!')

    @property
    def key(self):
        return f'{self.network}_{self.vocoder}_{self.bandwidth}'

    def check_connection(self):
        try:
            self.interface.Connect()
            self.interface.Disconnect()
            self.connected = True
        except:
            self.connected = False
        return self.connected

    def get_delay_net(self, direction):
        if 'GSM' == self.network or 'WCDMA' == self.network:
            delay = self.interface.QueryCommand(f'SENSe:{self.network}:SIGN1:CVINfo?')
            delay = delay.split(',')
            if 'SND' == direction and 'INV' != delay[2]:
                val = eval(delay[2])*1000
            elif 'RCV' == direction and 'INV' != delay[1]:
                val = eval(delay[1])*1000
            else:
                val = False
        elif 'LTE' == self.network:
            if 'SND' == direction:
                delay = self.interface.QueryCommand('READ:DATA:MEAS1:ADElay:ULINK?')
            else:
                delay = self.interface.QueryCommand('READ:DATA:MEAS1:ADElay:DLINK?')
            delay = delay.split(',')
            if 'INV' != delay[1]:
                val = eval(delay[1])*1000
            else:
                val = False
        return val

    def get_delay_tau(self):
        if 'LTE' == self.network:
            tau = self.interface.QueryCommand('READ:DATA:MEAS1:ADElay:TAULink?')
            tau = tau.split(',')
            if 'INV' != tau[1]:
                tau = eval(tau[1])*1000
            else:
                tau = False
        else:
            tau = False
        return tau

    def get_registered(self):
        registered = False
        if 'GSM' == self.network:
            ret = self.interface.QueryCommand('FETCh:GSM:SIGN1:CSWitched:STATe?')
            if 'SYNC' == ret:
                registered = True
        if 'WCDMA' == self.network:
            ret = self.interface.QueryCommand('FETCh:WCDMa:SIGN1:CSWitched:STATe?')
            if 'REG' == ret:
                registered = True
        elif 'LTE' == self.network:
            ret = self.interface.QueryCommand('SOURce:LTE:SIGN:CELL:STATe:ALL?')
            if ret == 'ON,ADJ':
                ret = self.interface.QueryCommand('FETCh:LTE:SIGN:PSWitched:STATe?')
                if 'ATT' == ret:
                    ret = self.interface.QueryCommand('SENSe:DATA:CONTrol:IMS2:MOBile1:STATus?')
                    if 'REG' == ret:
                        registered = True
        return registered

    def get_established(self):
        established = False
        if 'GSM' == self.network or 'WCDMA' == self.network:
            ret = self.interface.QueryCommand(f'FETCh:{self.network}:SIGN1:CSWitched:STATe?')
            if 'CEST' == ret:
                established = True
        elif 'LTE' == self.network:
            ret = self.interface.QueryCommand('SENse:DATA:CONTrol:IMS2:RELease:LIST?')
            if ret != '':
                established = True
        return established

    def put_mtcall(self):
        if 'GSM' == self.network:
            self.interface.WriteCommand('CALL:GSM:SIGN1:CSWitched:ACTion CONNect')
        elif 'WCDMA' == self.network:
            self.interface.WriteCommand('CALL:WCDMa:SIGN1:CSWitched:ACTion CONNect')
        elif 'LTE' == self.network:
            id = self.interface.QueryCommand('SENSe:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:DESTination:LIST?').split(',')[0]
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:DESTination {id}')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:TYPE AUDio')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MTCall:CALL')

    def update_call(self, vocoder, bandwidth, bitrate):
        self.set_call_config(self.network, vocoder, bandwidth, bitrate)
        str_bitrate = self.bitrates[self.key][bitrate]
        str_adcodec = self.adcodecs[self.key]
        if 'GSM' == self.network:
            self.interface.WriteCommand('CALL:GSM:SIGN1:PSWitched:ACTion DISConnect')
            self.interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:TMODe {str_adcodec}')
        elif 'WCDMA' == self.network:
            self.interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:CODec {bandwidth}')
            self.interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:AMR:{str_adcodec} {str_bitrate}')
        elif 'LTE' == self.network:
            id = self.interface.QueryCommand('SENse:DATA:CONTrol:IMS2:RELease:LIST?').split(',')[0]
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:CALL:ID {id}')
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:ADCodec:TYPE {str_adcodec}')
            if 'AMR' == vocoder:
                for br_key, br_val in self.bitrates[self.key].items():
                    if br_key == bitrate:
                        self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:CODec{br_val}:ENABle ON')
                    else:
                        self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:CODec{br_val}:ENABle OFF')
            elif 'EVS' == vocoder:
                self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:BWCommon {bandwidth}')
                self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:PERForm')

    def signling_on(self, err=True):
        state = False
        cnt = 0
        net = {'GSM':'GSM', 'WCDMA':'WCDMa', 'LTE':'LTE'}
        while not state and cnt < 60:
            time.sleep(1)
            cnt += 1
            ret = self.interface.QueryCommand(f'SOURce:{net[self.network]}:SIGN1:CELL:STATe:ALL?')
            ret = ret.split(',')
            if 'ON' not in ret:
                self.interface.WriteCommand(f'SOURce:{net[self.network]}:SIGN1:CELL:STATe ON')
            elif 'ADJ' in ret:
                state = True
        if err and not state:
            raise Exception('Enable signaling failure!')
        else:
            return state

    def init_config(self):
        str_adcodec = self.adcodecs[self.key]
        str_bitrate = self.bitrates[self.key][self.bitrate]
        self.interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:ILEVel 1.572')
        self.interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:OLEVel 1.572')
        self.interface.WriteCommand('CONFigure:AUDio:SPEech1:ANALog:FILTer:HPASs H6')
        if 'GSM' == self.network:
            self.interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "GSM Sig1"')
            self.interface.WriteCommand('CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:SIGNaling:MODE LTRR')
            rate_conf = {'NB':'GMSK', 'WB':'EPSK'}
            rate_conf2 = {'NB':{'C1220':'4', 'C0795':'3', 'C0590':'2', 'C0475':'1'}, 'WB':{'C2385':'4', 'C1585':'3', 'C1265':'2', 'C0660':'1'}}
            str_rate_conf = ', '.join(rate_conf2[self.bandwidth].keys())
            self.interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:RSET:{self.bandwidth}:FRATe:{rate_conf[self.bandwidth]} {str_rate_conf}')
            self.interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:CMODe:{self.bandwidth}:FRATe:{rate_conf[self.bandwidth]}:DL {rate_conf2[self.bandwidth][str_bitrate]}')
            self.interface.WriteCommand(f'CONFigure:GSM:SIGN1:CONNection:CSWitched:AMR:CMODe:{self.bandwidth}:FRATe:{rate_conf[self.bandwidth]}:UL {rate_conf2[self.bandwidth][str_bitrate]}')
            self.interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe ON')
        elif 'WCDMA' == self.network:
            self.interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "WCDMA Sig1"')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:UETerminate VOICe')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:SRBData R13K6, R13K6')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:CSWitched:CRELease NORMal')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:SOURce SPEech')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:DTX OFF')
            self.interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:CODec {self.bandwidth}')
            self.interface.WriteCommand(f'CONFigure:WCDMa:SIGN1:CONNection:VOICe:AMR:{str_adcodec} {str_bitrate}')
            self.interface.WriteCommand('CONFigure:WCDMa:SIGN1:CONNection:VOICe:TFCI OFF')
            self.interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe ON')
        elif 'LTE' == self.network:
            self.interface.WriteCommand('SOURce:GSM:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('SOURce:WCDMa:SIGN1:CELL:STATe OFF')
            self.interface.WriteCommand('ROUTe:AUDio1:SCENario:EASPeech "DAU IMS Server"')
            self.interface.WriteCommand('SOURce:DATA:CONTrol:STATe ON')
            self.interface.WriteCommand('SOURce:DATA:CONTrol:IMS2:STATe ON')
            # Config Virtual Subscriber1
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:BEHaviour ANSWer')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SIGNalingtyp PRECondit')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:BEARer ON')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:VIDeo ON')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:STANdalone ON')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:SESSionmode ON')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:SUPPorted:FEATures:FILetransfer ON')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:FORCemocall ON')
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:ADCodec:TYPE {str_adcodec}')
            if 'AMR' == self.vocoder:
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:ALIGnment OCTetaligned')
                for br_key, br_val in self.bitrates[self.key].items():
                    if br_key == self.bitrate:
                        self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:CODec{br_val}:ENABle ON')
                    else:
                        self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AMR:CODec{br_val}:ENABle OFF')
            else:
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:STARtmode EPRimary')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:HFONly BOTH')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:DTX DISable')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:DTXRecv NP')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:SYNCh:SELect COMMon')
                self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:BWCommon {self.bandwidth}')
                self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:CMR ENABle')
                self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:CHAWmode DIS')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:VIDeo:CODec H264')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:VIDeo:ATTRibutes ""')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:MEDiaendpoin AUDioboard')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:AUDioboard:CONFig INST1, OFF, FREE, FREE, SDP')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:VIRTualsub1:EVS:IO:MODE:CONFig EVSamrwb')
            # Config Update
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:CALL:TYPE AUDio')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:VIDeo:CODec H264')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:AMR:ALIGnment OCT')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:STARtmode EPRimary')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:HFONly BOTH')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:DTX DISable')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:DTXRecv NP')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:SYNCh:SELect COMMon')
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:BWCommon {self.bandwidth}')
            self.interface.WriteCommand(f'CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:COMMon:BITRate:RANGe {str_bitrate}, {str_bitrate}')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:CMR ENABle')
            self.interface.WriteCommand('CONFigure:DATA:CONTrol:IMS2:UPDate:EVS:CHAWmode DIS')
            self.interface.WriteCommand('SOURce:LTE:SIGN1:CELL:STATe ON')
        self.signling_on()
