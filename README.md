# PyACQUASupport

## Instructions

### Measurement Support

import and run the related support functions in **Project Options** of each project or add to **Measurement Settings** of MMD settings

import the support functions with `from ACQUASupport.MeasurementSupport import *`

Run function `before_each_measurement()` before each measurement

Run function `after_each_measurement()` after each measurement

Run function `after_canceled_measurement()` after canceled measurement

### Voice Measurement Setting

config and auto change the network in loop mode with lib **VoiceMeasurementSetting**

simply need to import the config funtion with `from ACQUASupport.VoiceMeasurementSetting import set_seq_config`

Run function `set_seq_config()` at the begainning of the sequence or at the time when need to change the network based on network flow process in loop mode
