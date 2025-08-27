# Raspberry-CM4-XGO-Rider

XGO-Rider, a fun two-wheeled biped robot.

# Choose Language / 选择语言

- [中文](README.md)
- [English](#README_en.md)

## Table of Contents

- [Project Overview](#project-overview)
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Project Overview

XGO-Rider is a desktop-level open-source two-wheeled biped development platform based on the Raspberry Pi CM4 module, enabling AI edge computing applications. It uses 4.5KG.CM full-metal magnetic encoder bus serial servos for joints, and FOC hub integrated motors as wheels. The robot supports flexible movement, self-balancing control, motion superposition, and image/voice interaction based on large language models. It is open for secondary development.

## Directory Structure
- RaspberryPi-CM4-main: Main program folder
  - demos: Example programs
    - expression: Emoji files
    - music: Audio files
    - speechCn: Chinese speech recognition
    - speechEn: English speech recognition
    - xiaozhi: Xiaozhi real-time voice interaction
  - flacksocket: Robot control and image transfer via flacksocket
  - language: Language configuration files
  - pics: Image files
  - volume: Volume configuration files

## Installation and Usage

1. Clone the repository:
    ```bash
    git clone https://github.com/Xgorobot/RaspberryPi-CM4-XGO-Rider.git
    ```

2. Enter the project directory:
    ```bash
    cd RaspberryPi-CM4-main
    ```

3. Run main.py:
    ```bash
    sudo python3 main.py
    ```

## Features
1. Web Remote Control: Visual remote control based on flacksocket.  
2. Voice Interaction: Voice interaction powered by Volcano large language model.  
3. Xiaozhi Interaction: Fun real-time interaction with Xiaozhi.  

## 📜 Changelog
### 2025-04-14
- **Code Improvement**: Optimized language switching in /RaspberryPi-CM4-main/demos/language.py, allowing switching without restarting the whole system.  
- **New Feature**: Added `update.sh` script to optimize system startup time.  

## Contributing
Contributions are welcome! We encourage suggestions, fixes, and feature enhancements. If you are interested in contributing to this project, please follow these steps:  
1. Fork this repository  
2. Create your own branch (`git checkout -b feature-branch`)  
3. Commit your changes (`git commit -am 'Add new feature'`)  
4. Push to your branch (`git push origin feature-branch`)  
5. Submit a Pull Request  

## License
This project is licensed under the MIT License.

## Acknowledgments
Special thanks to the following contributors:  
- Liu Pengfei Robotics  
- jd3096  

If you encounter any issues while using this project, feel free to submit Issues or Pull Requests!
