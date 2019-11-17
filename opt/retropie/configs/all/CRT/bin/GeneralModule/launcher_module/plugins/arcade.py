#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher arcade.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, logging
from launcher_module.core import CFG_VIDEOUTILITY_FILE
from launcher_module.file_helpers import ini_get
from launcher_module.arcade import arcade, TMP_ARCADE_FILE

class arcade(arcade):
    m_oConfigureFunc = None
    m_bIntegerScale = False

    @staticmethod
    def get_system_list():
        return ["arcade", "mame-advmame", "mame-libretro", "fba", "neogeo"]

    def pre_configure(self):
        self.m_lBinaryUntouchable = ["advmame"] #Identifing emulators that is not necesary to change
        
        if self.m_sSystem == "mame-advmame":
            self.m_oConfigureFunc = self.adv_config_generate
            self.m_lBinaryMasks = ["advmame"]
            self.m_lProcesses = ["advmame"] # default emulator process is retroarch
        elif self.m_sSystem == "arcade":
            self.m_oConfigureFunc = self.arcade_config_generate
            self.m_lBinaryMasks = ["lr-", "advmame"]
            self.m_lProcesses = ["retroarch", "advmame", "mame", "fba2x"] # if BinaryMask doesn't match will try to close all these process
        else:
            self.m_oConfigureFunc = self.ra_config_generate
            self.m_lBinaryMasks = ["lr-"]
            self.m_lProcesses = ["retroarch"] # default emulator process is retroarch
            
        if ini_get(CFG_VIDEOUTILITY_FILE, "integer_scale") == "1":
            self.m_bIntegerScale = True
            logging.info("enabled integer scale for arcade/neogeo")

    def arcade_config_generate(self):
        #Check if libretro core of advmame is selected whitin
        #arcade system to generate configuration
        if "lr-" in self.m_sBinarySelected:
            logging.info("INFO: generating retroarch configuration for ARCADE binary selected (%s)" % self.m_sBinarySelected)
            self.ra_config_generate()
        elif "advmame" in self.m_sBinarySelected:
            logging.info("INFO: generating advmame configuration for ARCADE binary selected (%s)" % self.m_sBinarySelected)
            self.adv_config_generate()

    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(arcade, self).runcommand_generate(p_sCMD)

        #Check if a VALID binary of the list must be excluded of the --appendconfig flag addition (non RetroArch emulators):
        if self.m_sNextValidBinary in self.m_lBinaryUntouchable:
            return current_cmd

        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % TMP_ARCADE_FILE
        append_cmd += " " + self.m_sFileNameVar
        return current_cmd.replace(self.m_sFileNameVar, append_cmd)