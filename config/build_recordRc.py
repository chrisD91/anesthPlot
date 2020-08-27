

"""
build a yaml file to store che configuration of scripts
input (data) and output(save)
"""

import os
import sys
import yaml
from PyQt5.QtWidgets import QFileDialog, QDialog, QApplication
from PyQt5 import QtCore


#%%
def fileDialog(kind='',
               directory=os.path.dirname(__file__),
               forOpen=True, fmt='', isFolder=False):
    label = 'select the folder for ' + kind
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.DontUseCustomDirectoryIcons
    dialog = QFileDialog(caption=label)
    dialog.setOptions(options)

    dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)

    # ARE WE TALKING ABOUT FILES OR FOLDERS
    if isFolder:
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    else:
        dialog.setFileMode(QFileDialog.AnyFile)
    # OPENING OR SAVING
    dialog.setAcceptMode(QFileDialog.AcceptOpen
                         ) if forOpen else dialog.setAcceptMode(QFileDialog.AcceptSave)

    # SET FORMAT, IF SPECIFIED
    if fmt != '' and isFolder is False:
        dialog.setDefaultSuffix(fmt)
        dialog.setNameFilters([f'{fmt} (*.{fmt})'])

    # SET THE STARTING DIRECTORY
    if directory != '':
        dialog.setDirectory(str(directory))
    else:
        dialog.setDirectory(os.getcwd())

    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]  # returns a list
    else:
        path = ''
    return path

def readConfig():
    #locate
    try:
        # for external call
        #NB __file__ is supposed to
        #"always give you the path to the current file",
        #and sys.argv[0] is supposed to
        #"always give the path of the script that initiated the process"
        print(os.path.dirname(__file__))
        localModPath = os.path.dirname(__file__)
    except:
        # for inside spyder
        localModPath = '/Users/cdesbois/pg/chrisPg/anesthPlot'
    filename = os.path.join(localModPath, 'recordRc.yaml')
    #load
    if os.path.isfile(filename):
        with open(filename, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            return cfg
    else:
        print('no config file present')
        print('please build one -> cf buildConfig.py')
        return None

def writeConfigFile(path):
    os.chdir(paths['recordMain'])
    with open('recordRc.yaml', 'w') as ymlfile:
        yaml.dump(path, ymlfile, default_flow_style=False)



#%%
if __name__ == '__main__':
    try:
        app
    except:
        app = QApplication(sys.argv)
    # test if paths exists
    try:
        paths
    except:
        key = 'record_main.py'
#        recordMainPath = fileDialog(kind=key, directory= os.getcwd(), isFolder=True)
        recordMainPath = fileDialog(kind=key, directory=os.getcwd())
        if os.path.isfile(recordMainPath):
            recordMainPath = os.path.dirname(recordMainPath)
        configName = os.path.join(recordMainPath, 'config', 'recordRc.yaml')
        if os.path.isfile(configName):
            # build from config file
            paths = readConfig()
        else:
            # build from trash
            paths = {}
            paths['recordMain'] = recordMainPath
            paths['cwd'] = os.getcwd()
    home = os.path.expanduser('~')
    # manual define/confirm the paths
    for key in ['root', 'data', 'save']:
        if key in paths.keys():
            paths[key] = fileDialog(kind=key, directory=paths[key], isFolder=True)
        else:
            paths[key] = fileDialog(kind=key, directory=home, isFolder=True)
    paths['sFig'] = paths['save']
    paths['sBg'] = paths['save']
    paths['utils'] = '~'
    #write config
    writeConfigFile(paths)
    try:
        app
    except:
        app.exec_()
