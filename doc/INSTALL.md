## Installation de panda 3d

Pour le moment, je ne fais que la procédure d'install linux / ubuntu.

### Installation sur une Ubuntu 18.04

Prérequis :
1. avoir python3 installé (c'est déja le cas)

2. pip installé pour python 3 (sur le systeme)
  ```
  sudo apt-get install python3-pip
  ```

3. virtual env installé pour python 3 (au moins pour le user)
  ```
  pip3 install virtualenv
  ```

4. Créez vous un repertoire de travail et placez vous dedans avec le terminal

5. creez un virtualenv pour python3
  ```
  virtualenv -p python3 venv
  ```

6. Activez ce virtualenv
  ```
  source venv/bin/activate
  ```

7. Installez panda3D dans ce virtualenv
  ```
  pip install --pre --extra-index-url https://archive.panda3d.org panda3d
  ```

8. Récuperez les exemples contenus dans ce
[fichier zip](https://www.panda3d.org/download/panda3d-1.9.4/panda3d-1.9.4-samples.zip)
et extrayez le repertoire samples votre **repertoire de travail**

9. Essayez l'un des exemples.
  ```
  cd samples/carousel
  python main.py
  ```
