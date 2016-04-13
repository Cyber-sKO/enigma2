#############################################
# [English]
# Plugin-Bootlogo mod by Cyber_sKO
# Questions etc.: cyber.sko@gmail.com
# Plugin write English
# german will be comming soon
#
# [Deutsch]
# Plugin-Bootlogo modifiziert von Cyber_sKO
# Fragen etc.: cyber.sko@gmail.com
# Plugin nur in Englisch geschrieben
# deutsch wird bald kommen
#############################################

# imports
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.Label import Label
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from skin import parseColor
from os import environ, listdir, remove, rename, system
from enigma import ePicLoad
import gettext

# language translation
lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("BootlogoMod", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/BootlogoMod/locale/"))

def _(txt):
	t = gettext.dgettext("BootlogoMod", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

# Bootlogos
config.plugins.BootlogoMod = ConfigSubsection()
config.plugins.BootlogoMod.active = ConfigSelection(default="default-OpenATV", choices = [
#				("omblackblue", _("OpenMips Black/Blue")),
				("Standard", _("default-OpenATV")),
				("Dark", _("OpenATV Dark")),
				("3D_Blue", _("OpenATV 3D blue")),
				("3D_Red", _("OpenATV 3D red")),
				("Old_Movie", _("OpenATV Old Movie")),
				("Silverlight", _("OpenATV Silverlight")),
				("Spaceship1", _("OpenATV Spaceship 1")),
				("Spaceship2", _("OpenATV Spaceship 2")),
				("Spaceship3", _("OpenATV Spaceship 3")),
				("Wet", _("OpenATV Wet")),
				("White_Blue", _("OpenATV White/Blue"))
				])

# screen konfig
class BootlogoMod(ConfigListScreen, Screen):
	skin = """
  <screen name="BootlogoMod-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#90000000">
    <eLabel name="new eLabel" position="390,90" zPosition="-2" size="500,540" backgroundColor="#20000000" transparent="0" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="427,595" size="250,33" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="727,595" size="250,33" text="Save" transparent="1" />
    <widget name="config" position="410,400" size="460,150" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel position="415,115" size="498,50" text="Bootlogo" font="Regular; 40" valign="center" transparent="1" backgroundColor="#20000000" />
    <eLabel position="710,590" size="5,40" backgroundColor="#61e500" />
    <eLabel position="410,590" size="5,40" backgroundColor="#e61700" />
    <widget name="bootlogohelperimage" position="515,200" size="250,141" zPosition="1" />
  </screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.bootlogosourcepath = "/usr/lib/enigma2/python/Plugins/Extensions/BootlogoMod/logos/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["bootlogomodhelperimage"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("Select Bootlogo:"), config.plugins.BootlogoMod.active))
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
		self.onLayoutFinish.append(self.UpdatePicture)

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/BootlogoMod/preview/" + returnValue + ".png"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/BootlogoMod/preview/nopreview.png"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["bootlogohelperimage"].instance.size().width(),self["bootlogohelperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#20000000"])
		self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["bootlogohelperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartSTB,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart STB"))

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass
		configfile.save()
		self.changebootlogo()
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartSTB,MessageBox,_("Your STB needs a restart to apply the new bootlogo.\nDo you want to Restart you STB now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart STB"))

	def changebootlogo(self):
		try:
			self.bootlogomodactive = (config.plugins.BootlogoMod.active.value + ".mvi")
			self.bootlogomodsource = (self.bootlogosourcepath + self.bootlogomodactive)
			self.bootlogomodtarget = "/usr/share/bootlogo.mvi"
			self.bootlogomodcommand = (self.bootlogomodsource + " " + self.bootlogomodtarget)
			system('cp -f ' + self.bootlogomodcommand)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error setting Bootlogo!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def restartSTB(self, answer):
		if answer is True:
			configfile.save()
			system('reboot')
		else:
			self.close()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

# plugin descriptior

def main(session, **kwargs):
	session.open(BootlogoMod)

def Plugins(**kwargs):
	return PluginDescriptor(
							name="BootlogoMod by Cyber_sKO", 
							description=_("Select your Bootlogo"), 
							where = PluginDescriptor.WHERE_PLUGINMENU, 
							icon="plugin.png", 
							fnc=main
							)