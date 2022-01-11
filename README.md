# [SynDatGen](https://syndatgen.org)
## Synthetic data generator for machine learning
### Make datasets for image recognition systems from 3D models

<!--
**SynDatGen/SynDatGen** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
#### ⚡Installation⚡
pip3 install -r requirements.txt

#### ⚡Launch⚡
python3 main.py

#### ⚡Launch Parameters⚡
|Parameter|Description|Example|Default|
|:---------|:---------|:------|:------|
|-i --input|input folder of file|in|in|
|-o --out|output folder|out|out|
|-s --size|image size|128|128|
|-c --colors|color(s)|"red green blue"|"none"|
|-d --distance|distance(s) from camera to 3D model|"1.5 2.7"|"1.7"|
|-e --elevation|elevation angle(s) of 3D model|"0 45 90"|0|
|-r --rotation|rotation angle(s)|"0 45 90"|"0 45 90"|
|-l --labels|Generate labels.txt|True or False|True| 
|-lo --label|Label override|"Car"|subfolders from input folder|

#### ⚡Avaliable colors⚡
* red   
* green
* blue
* yellow
* purple
* cyan
* white
* black
* random
* none (use model's default)

#### ⚡Supported 3D models formats⚡
* .obj
* .stl
* .off

#### ⚡Structure⚡
![classes](https://github.com/SynDatGen/SynDatGen/blob/main/classes_SynDatGen.png)
