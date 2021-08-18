# homeassistant-remote-fan-speed-control

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://opensource.org/licenses/MIT)

# Description

A python script for Home Assistant that help control IR fan speed with [Fan Template](https://www.home-assistant.io/integrations/fan.template/) and [Broadlink](https://www.home-assistant.io/integrations/broadlink/).

## Thumbnail

![thumbnail](/thumbnail.png)

# How it work

The script automatically call remote service (e.g., broadlink) when setting the fan speed.

For example, the speed range of your fan is from 1 to 7.

- Call the `increase` command 4 times when you set fan speed from 1 to 5.

- Call the `decrease` command 3 times when you set fan speed from 5 to 2.


# Installation

1. Enable the Python script support in the HA by adding the following line in your `configuration.yaml`, and then restart HA.

    ```yaml
    python_script:
    ```

2. Install the python script:

   Copy the [python_scripts/remote_fan_speed_control.py](python_scripts/remote_fan_speed_control.py) into your `{config}/python_scripts` directory.


# Script arguments
|key|required|type|description|
|-|-|-|-|
|percentage|true|string|The speed percentage from fan template|
|speed_entity_id|true|string|The input_text entity for storing last speed text in percentage|
|entity_id|true|string|The Fan template entity id|
|speed_count|true|string|The `speed_count` of the Fan template|
|service|true|string|The remote service used to send IR signal to fan|
|service_data_increase|true|object||
|&nbsp;&nbsp;service_data_increase.entity_id|true|string|The remote device entity to send IR signal. e.g., Broadlink|
|&nbsp;&nbsp;service_data_increase.command|true|string|The IR code for increasing the fan speed|
|service_data_decrease|true|object||
|&nbsp;&nbsp;service_data_decrease.entity_id|true|string|The remote device entity to send IR signal. e.g., Broadlink|
|&nbsp;&nbsp;service_data_decrease.command|true|string|The IR code for decreasing the fan speed|

# Main config
```yaml
set_percentage:
  - service: python_script.remote_fan_speed_control
    data_template:
      percentage: "{{ percentage }}"
      entity_id: 'fan.sampo_fan'
      speed_entity_id: 'input_text.status_sampo_fan_speed'
      speed_count: 7
      service: 'remote.send_command'
      service_data_decrease:
        entity_id: remote.broadlink
        command: b64:REMOTE_CODE_DECREASE_SPEED
      service_data_increase:
        entity_id: remote.broadlink
        command: b64:REMOTE_CODE_INCREASE_SPEED
```

## Template Fan config

**Note. Before starting the fan in HA, you need to decrease your actual fan speed to the minimum one to adjust the initial fan speed value storing in the `input_text.status_sampo_fan_speed` entity, or change the `input_text.status_sampo_fan_speed.initial` value to the desire value.**

```yaml
input_text:
  status_sampo_fan_speed:
    name: 'SAMPO DC Fan Speed'
    initial: 0 # //!<<< Adjust this value if your actual fan speed is not zero. Formula: round( current_speed / speed_count * 100 );

switch:
  - platform: template
    switches:
      sampo_fan_power:
        friendly_name: "SAMPO DC Fan Power"
        turn_on:
          service: script.turn_on
          data:
            entity_id: script.broadlink_sampo_fan_power_on_off
        turn_off:
          service: script.turn_on
          data:
            entity_id: script.broadlink_sampo_fan_power_on_off

fan:
  - platform: template
    fans:
      sampo_fan:
        friendly_name: "SAMPO DC Fan"
        speed_count: 7
        value_template: "{{ states('switch.sampo_fan_power') }}"
        percentage_template: "{{ states('input_text.status_sampo_fan_speed') | int }}"
        turn_on:
          - condition: state
            entity_id: switch.sampo_fan_power
            state: 'off'
          - service: switch.turn_on
            entity_id: switch.sampo_fan_power
        turn_off:
          - condition: state
            entity_id: switch.sampo_fan_power
            state: 'on'
          - service: switch.turn_off
            entity_id: switch.sampo_fan_power
        set_percentage:
          - service: python_script.remote_fan_speed_control
            data_template:
              percentage: "{{ percentage }}"
              entity_id: 'fan.sampo_fan'
              speed_entity_id: 'input_text.status_sampo_fan_speed'
              speed_count: 7
              service: 'remote.send_command'
              service_data_decrease:
                entity_id: remote.broadlink
                command: b64:REMOTE_CODE_DECREASE_SPEED
              service_data_increase:
                entity_id: remote.broadlink
                command: b64:REMOTE_CODE_INCREASE_SPEED

script:
  broadlink_sampo_fan_power_on_off:
      sequence:
      - service: remote.send_command
        data:
          entity_id: remote.broadlink
          command: b64:REMOTE_CODE_POWER_ON_OFF
```

# Debug

Add `logger` to your `configuration.yaml`

```yaml
logger:
  default: warn
  logs:
    homeassistant.components.python_script.remote_fan_speed_control.py: debug
```

## License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).

## Written by

Written by [Eason Kang](https://www.facebook.com/yisheng.kang)

Inspired by [Long](https://github.com/iml885203)'s [HA-FanSpeedControl](https://github.com/iml885203/HA-FanSpeedControl)