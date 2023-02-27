# GalaxyEmpire  
This is a tool for Next2fun game Galaxy Empire.  
Wish you have fun here.  

# How to use
1. Download the source code.
```shell
git clone https://github.com/codycjy/GalaxyEmpire.git
```
2. Install python3.8 or above.
3. Install the requirements.
```shell
pip install -r requirements.txt
```
4. open the main.py and setup config. 
5. run the main.py
```shell
python3 main.py
```
# Config
There are three main func in this tool.
1. attack
2. explore
3. escape

## Attack
`ATTACKTARGET`: the target you want to attack.  
A list of targets coordinates, each target should be a list of three integers.  
You'd better set more than one target, because of the 2 hours cooldown of the attack.

`ATTACKFROM`: the planet you want to attack from.  
__IMPORTANT__: THIS ISN'T THE COORDINATE OF THE PLANET,  
THIS IS THE [ID](#planet-id) OF THE PLANET (OR MOON) YOU WANT TO ATTACK FROM.

`ATTACKLEVEL`: Choose the [fleet](#fleet) you want to send.

## Explore
Almost all the config is the same as attack.

# Fleet
The recommanded fleet is in main.py.  
If you want to customize your fleet, please follow the format and keep in mind that level between 50 and 100 is for explore

## Supported ships
| Ship abbr | ship name     |
|-----------|---------------|
| ds        | Deathstar     |
| bs        | Battleship    |
| cargo     | Large Cargo   |
| satellite | Probe         |
| lf        | Light Fighter |
| hf        | Heavy Fighter |
| cr        | Cruiser       |
| de        | Destroyer     |
| bomb      | Bomber        |
| guard     | Guardian      |
 
# Escape
Just open and it works.

# Planet ID
For the first time, you can set `showPlanetID` to `True` to get the planet ID.
## About planet ID
- This won't change if you migrate to another planet.
- When server merge, your planet ID may change. 

# TODO
- [ ] Add CMD README
- [ ] Test CMD func
- [ ] Add logger to CMD
- [ ] Enable proxy ip to bypass 5 account limit
- [ ] Add master Node Controller
- [ ] Apply more node operation

Welcome to contribute to this project.
