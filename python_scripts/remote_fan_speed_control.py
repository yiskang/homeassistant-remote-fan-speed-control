#!/usr/bin/python
# -*- coding: utf-8 -*-
###
# MIT License
#
# Copyright (c) 2021 Yi-Sheng, Kang (Eason Kang)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###

### Declaration

# Remote service data

service = data.get('service')
[service_domain, service_name] = service.split('.')
service_data_decrease = data.get('service_data_decrease')
service_data_increase = data.get('service_data_increase')

# Fan speed data

speed_percentage = data.get('percentage')
speed_count = data.get('speed_count')

fan_speed_entity_id = data.get('speed_entity_id')
fan_speed_entity = hass.states.get(fan_speed_entity_id)

fan_entity_id = data.get('entity_id')
fan_entity = hass.states.get(fan_entity_id)

logger.debug('<remote_fan_speed_control> fan state ({})'.format(fan_entity.state))
logger.debug('<remote_fan_speed_control> Received fan speed from ({}) to ({})'.format(fan_speed_entity.state,
             speed_percentage))


### Utilities

def check_speed(logger, speed):
    if speed is None:
        logger.warning('<remote_fan_speed_control> Received fan speed is invalid (None)'
                       )
        return False

    if fan_entity.state == 'off':
        logger.debug('<remote_fan_speed_control> call fan on')
        hass.services.call('fan', 'turn_on',
                           {'entity_id': fan_entity_id})

    return True


### Main

if check_speed(logger, speed_percentage):
    speed_step = 100 // speed_count
    target_speed = int(speed_percentage) // speed_step
    last_speed_state = \
        (fan_speed_entity.state if fan_speed_entity.state.isdigit() else 0)
    last_speed = int(last_speed_state) // speed_step
    speed_max = speed_count

    if target_speed > last_speed:
        loop = increase_loop = target_speed - last_speed
        service_data = service_data_increase
        
        if target_speed == 0:
            loop = loop - 1
    elif target_speed < last_speed:
        if target_speed == 0:
            loop = 0
            hass.services.call('fan', 'turn_off',
                               {'entity_id': fan_entity_id})
        else:
            loop = last_speed - target_speed
            service_data = service_data_decrease
    else:
        loop = 0

  # update speed state

    if target_speed > 0:
        hass.states.set(fan_speed_entity_id, speed_percentage)

  # Call service

    if data.get('support_num_repeats', False):
        service_data['num_repeats'] = loop
        logger.debug('<remote_fan_speed_control> call service ({}.{}) {}'.format(service_domain,
                     service_name, service_data))
        hass.services.call(service_domain, service_name, service_data)
    else:
        for i in range(loop):
            logger.debug('<remote_fan_speed_control> call service ({}.{}) {}'.format(service_domain,
                         service_name, service_data))
            result = hass.services.call(service_domain, service_name,
                    service_data)
            time.sleep(1)
else:
    if fan_entity.state == 'off':
        logger.debug('<remote_fan_speed_control> call fan on')
        hass.services.call('fan', 'turn_on',
                           {'entity_id': fan_entity_id})
    else:
        if speed_percentage == 'off':
            logger.debug('<remote_fan_speed_control> call fan off')
            hass.services.call('fan', 'turn_off',
                               {'entity_id': fan_entity_id})