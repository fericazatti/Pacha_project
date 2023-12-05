##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import copyreg as copy_reg
import math
import re
from datetime import datetime
from time import altzone
from time import daylight
from time import gmtime
from time import localtime
from time import time
from time import timezone
from time import tzname

from zope.interface import implementer

from .interfaces import DateError
from .interfaces import DateTimeError
from .interfaces import IDateTime
from .interfaces import SyntaxError
from .interfaces import TimeError
from .pytz_support import PytzCache


basestring = str
long = int
explicit_unicode_type = type(None)

default_datefmt = None


def getDefaultDateFormat():
    global default_datefmt
    if default_datefmt is None:
        try:
            from App.config import getConfiguration
            default_datefmt = getConfiguration().datetime_format
            return default_datefmt
        except Exception:
            return 'us'
    else:
        return default_datefmt


# To control rounding errors, we round system time to the nearest
# microsecond.  Then delicate calculations can rely on the fact that the
# maximum precision that needs to be preserved is known.
_system_time = time


def time():
    return round(_system_time(), 6)


# Determine machine epoch
tm = ((0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334),
      (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
yr, mo, dy, hr, mn, sc = gmtime(0)[:6]
i = int(yr - 1)
to_year = int(i * 365 + i // 4 - i // 100 + i // 400 - 693960.0)
to_month = tm[yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)][mo]
EPOCH = ((to_year + to_month + dy +
          (hr / 24.0 + mn / 1440.0 + sc / 86400.0)) * 86400)
jd1901 = 2415385

_TZINFO = PytzCache()

INT_PATTERN = re.compile(r'([0-9]+)')
FLT_PATTERN = re.compile(r':([0-9]+\.[0-9]+)')
NAME_PATTERN = re.compile(r'([a-zA-Z]+)', re.I)
SPACE_CHARS = ' \t\n'
DELIMITERS = '-/.:,+'

_MONTH_LEN = ((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
              (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))
_MONTHS = ('', 'January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December')
_MONTHS_A = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
_MONTHS_P = ('', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June',
             'July', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.')
_MONTHMAP = {'january': 1, 'jan': 1,
             'february': 2, 'feb': 2,
             'march': 3, 'mar': 3,
             'april': 4, 'apr': 4,
             'may': 5,
             'june': 6, 'jun': 6,
             'july': 7, 'jul': 7,
             'august': 8, 'aug': 8,
             'september': 9, 'sep': 9, 'sept': 9,
             'october': 10, 'oct': 10,
             'november': 11, 'nov': 11,
             'december': 12, 'dec': 12}
_DAYS = ('Sunday', 'Monday', 'Tuesday', 'Wednesday',
         'Thursday', 'Friday', 'Saturday')
_DAYS_A = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
_DAYS_P = ('Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.')
_DAYMAP = {'sunday': 1, 'sun': 1,
           'monday': 2, 'mon': 2,
           'tuesday': 3, 'tues': 3, 'tue': 3,
           'wednesday': 4, 'wed': 4,
           'thursday': 5, 'thurs': 5, 'thur': 5, 'thu': 5,
           'frieg                               #  one W
    (?P<week>\d\d)                  #  two digits week
    (?:-?                           #  one optional dash
     (?P<week_day>\d)               #  one digit week day
    )?                              #  week day is optional
   |                                # or:
    (?P<month>\d\d)?                #  two digits month
    (?:-?                           #  one optional dash
     (?P<day>\d\d)?                 #  two digits day
    )?                              #  after day is optional
   )                                #
  )?                                # after year is optional
  (?:[T ]                           # one T or one whitespace
   (?P<hour>\d\d)                   # two digits hour
   (?::?                            # one optional colon
    (?P<minute>\d\d)?               # two digits minute
    (?::?                           # one optional colon
     (?P<second>\d\d)?              # two digits second
     (?:[.,]                        # one dot or one comma
      (?P<fraction>\d+)             # n digits fraction
     )?                             # after second is optional
    )?                              # after minute is optional
   )?                               # after hour is optional
   (?:                              # timezone:
    (?P<Z>Z)                        #  one Z
   |                                # or:
    (?P<signal>[-+])                #  one plus or one minus as signal
    (?P<hour_off>\d                 #  one digit for hour offset...
     (?:\d(?!\d$)                   #  ...or two, if not the last two digits
    )?)                             #  second hour offset digit is optional
    (?::?                           #  one optional colon
     (?P<min_off>\d\d)              #  two digits minute offset
    )?                              #  after hour offset is optional
   )?                               # timezone is optional
  )?                                # tcb�G�����2���2FW&�fRF�RF��W���R֖�FWV�FV�B6V6��Bg&��F�RF��W���P�2FWV�FV�B6V6��B�g6WDDW�6���G��fg6WB�G������V%F��R���g6WDDW�6�����r�U�4����cC��0�2�V%F��R�2��rv�F������W"�b&V��r6�'&V7B�2&V6�7V�FRB66�&F��rF�E5B�g6WB����r��G��fg6WB�G���V%F��R���B����g6WB���cC����2��cC���B���g6WB����r�U�4����cC��0�֖7&�2�����cC�g6WB��������r�&�V�B��2��������r�U�4�����2�B��F��f���"�B��&WGW&��2�B�B�֖7&�2����FVb�6�4��2����2���2��W'2�֖�WFW2�6V6��G2g&����FVvW"�Bf��B��"����3c ������"�3c �������c �62������c��0�&WGW&���"����62����FVb�6�5��D��2����2���2��2F��W���R�FWV�FV�B��FVvW"�b6V6��G2�2&�GV6W2�"����G�Ƈ"����62��"����G���6�V�F&F������cC��C�������B��������cC���cC���"����3c ������"�3c �������c �62������c��0�&WGW&���"����G���"����62����FVb��VƖ�F���"����G��������B����r��"�����r�������r�G����b��#��������� ����R �VƖb�������Т�������"����"��R ��b�����%�6�'&V7B� �V�6S���%�6�'&V7B�0��b��3����������� ��b������B�S�#C��"�"��������C �V�6S��"� �&WGW&���Cc����%�6�'&V7B���B��3c��������B�s#��B�"����FVb�6�V�F&F�����������r�����b���##��c���"���S#P�V�6S����B���sCc��c���Cc�p�"���S#b����@�2��#�"�#CC"���s3P�B�Cc�2��@�R���"�B���3c�G����B�"�B�3c�R��������R�B��B��B�R���"��B�R�2���"�����"��B�2�Csb��"�B��G�66�R�����f�VW2�������6�727G&gF��Tf�&�GFW#���FVb����E��6V�b�GB�f�&�B���6V�b�GB�G@�6V�b�f�&�B�f�&�@��FVb��6����6V�b���&WGW&�6V�b�GB�7G&gF��R�6V�b�f�&�B�������V�V�FW"��FFUF��R��6�72FFUF��S��""$FFUF��R�&�V7G2&W&W6V�B��7F�G2��F��R�B&�f�FP���FW&f6W2f�"6��G&��Ɩ�r�G2&W&W6V�FF���v�F��W@�ffV7F��rF�R'6��WFRf�VR�bF�R�&�V7BࠢFFUF��R�&�V7G2��&R7&VFVBg&��v�FRf&�WG��b7G&��p��"�V�W&�2FF��"��&R6��WFVBg&���F�W"FFUF��R�&�V7G2�FFUF��W27W�'BF�R&�ƗG�F�6��fW'BF�V�"&W&W6V�FF���0�F������"F��W���W2�2vV��2F�R&�ƗG�F�7&VFR�FFUF��R�&�V7B��F�R6��FW�B�bv�fV�F��W���RࠢFFUF��R�&�V7G2&�f�FR'F���V�W&�6�&V�f��#����Gv�FFR�F��R�&�V7G26�&R7V'G&7FVBF��'F��F��R����F�2&WGvVV�F�RGv�ࠢ�FFR�F��R�&�V7B�B�6�F�fR�"�VvF�fR�V�&W"���&RFFVBF��'F���WrFFR�F��R�&�V7BF�B�2F�Rv�fV��V�&W"�bF�2�FW"F��F�R��WBFFR�F��R�&�V7Bࠢ��6�F�fR�"�VvF�fR�V�&W"�BFFR�F��R�&�V7B���&RFFVBF��'F���WrFFR�F��R�&�V7BF�B�2F�Rv�fV��V�&W"�bF�2�FW"F��F�R��WBFFR�F��R�&�V7Bࠢ��6�F�fR�"�VvF�fR�V�&W"��&R7V'G&7FVBg&���FFR�F��R�&�V7BF��'F���WrFFR�F��R�&�V7BF�B�0�F�Rv�fV��V�&W"�bF�2V&ƖW"F��F�R��WBFFR�F��P��&�V7BࠢFFUF��R�&�V7G2��&R6��fW'FVBF���FVvW"����r��"f��@��V�&W'2�bF�26��6R��V'����W6��rF�R7F�F&B��B�����r��Bf��BgV�7F���2�6��F�&�ƗG���FS���B����r�@�f��B&WGW&�F�R�V�&W"�bF�26��6R���t�B&F�W"F����6��6���RF��W���R��FFUF��R�&�V7G2�6�&�f�FR66W70�F�F�V�"f�VR��f��Bf�&�BW6&�Rv�F�F�R�F���F��P���GV�R�&�f�FVBF�BF�Rf�VR�bF�R�&�V7Bf��2��F�P�&�vR�bF�RW�6��&6VBF��R��GV�R��B2FFWF��R�FFWF��P��&�V7BࠢFFUF��R�&�V7B6��V�B&R6��6�FW&VB���WF&�S���6��fW'6����B�V�W&�2�W&F���2&WGW&��WrFFUF��R�&�V7B&F�W"F����F�g�F�R7W'&V�B�&�V7B�"" ��2f�"6V7W&�G��6���W'�����&��W5������P������u�66W75�F��V�&�FV7FVE�7V&�&�V7G5�����2Ɩ֗BF�R��V�B�b��7F�6RGG&�'WFW0���6��G5�����u�F��W���U���fRr��u�G�r��u�F��fg6WBr��u��V"r��u����F�r��u�F�r��u���W"r��u�֖�WFRr��u�6V6��Br��u��V'6V2r��u�Br��u�֖7&�2r��wF��Rr�����FVb����E��6V�b��&w2����r���""%&WGW&��WrFFR�F��R�&�V7B"" �G'���&WGW&�6V�b��'6U�&w2��&w2����r��W�6WB�FFTW'&�"�F��TW'&�"�FFUF��TW'&�"���&�6P�W�6WBW�6WF��㠢&�6R7��F�W'&�"�uV�&�RF�'6R�����r�f�&�B�&w2��r����FVb��vWG7FFU��6V�b���2vR7F�&Rf��B�b�֖7&�2���7FVB�bF�R�֖7&�2���r�2vR��7@�2�gFV�F��wB�fR�7V"�6V6��B&W6��WF����B6�6fRF��6R'�FW0�&WGW&��6V�b��֖7&�2����vWFGG"�6V�b�u�F��W���U���fRr�f�6R���6V�b��G����FVb��6WG7FFU��6V�b�f�VR����b�6��7F�6R�f�VR�GW�R���6V�b��'6U�&w2�f�VU���f�VU�%Ґ�6V�b��֖7&�2����r�f�VU�����6V�b��F��W���U���fR�f�VU�ТV�6S��f�"��b��f�VR�FV�2�����b���6V�b���6��G5��6WFGG"�6V�b���b��2$$#�7W�'Bf�"fW'���BFFUF��R�6��W0��bu�֖7&�2r��B��f�VS��6V�b��֖7&�2����r�f�VU�u�Bu�����bu�F��W���U���fRr��B��f�VS��6V�b��F��W���U���fR�f�6P��FVb�'6U�&w2�6V�b��&w2����r���""%&WGW&��WrFFR�F��R�&�V7BࠢFFUF��R�&�V7B�v�2���F��2�G2f�VR2�'6��WFP�UD2F��R��B�2&W&W6V�FVB��F�R6��FW�B�b6��RF��W���P�&6VB��F�R&wV�V�G2W6VBF�7&VFRF�R�&�V7B�FFUF��P��&�V7Bw2�WF��G2&WGW&�f�VW2&6VB��F�RF��W���R6��FW�Bࠢ��FRF�B����66W2F�R��6��6���RF��W���R�2W6VBf� �&W&W6V�FF����b��F��W���R�27V6�f�VBࠢFFUF��W2��&R7&VFVBv�F��W&�F�6WfV�&wV�V�G2ࠢ��bF�RgV�7F����26��VBv�F���&wV�V�G2�"v�F����R��F�V�F�R7W'&V�BFFR�F��R�2&WGW&�VB�&W&W6V�FVB��F�P�F��W���R�bF�R��6��6���Rࠢ��bF�RgV�7F����2��f��VBv�F�6��v�R7G&��r&wV�V�@�v��6��2&V6�v旦VBF��W���R��R���&�V7B&W&W6V�F��p�F�R7W'&V�BF��R�2&WGW&�VB�&W&W6V�FVB��F�R7V6�f�V@�F��W���Rࠢ��bF�RgV�7F����2��f��VBv�F�6��v�R7G&��r&wV�V�@�&W&W6V�F��rfƖBFFR�F��R���&�V7B&W&W6V�F��p�F�BFFR�F��Rv���&R&WGW&�VBࠢ2vV�W&�'V�R��FFR�F��R&W&W6V�FF���F�B�0�&V6�v旦VB�BV��&�wV�W2F�&W6�FV�B�b��'F��W&�6��266WF&�R�F�R&V6��f�"F��2VƖf�6F����2F�@�����'F��W&�6�FFRƖ�S�"����B�2��FW'&WFV@�2fV''V'����B�v���R��6��R'G2�bF�Rv�&�B���B�2��FW'&WFVB2��V'�"���BࠢFFR�F��R7G&��r6��6�7G2�bGv�6����V�G2�FFP�6����V�B�B��F����F��R6����V�B�6W&FVB'���P��"��&R76W2��bF�RF��R6����V�B�2�֗GFVB�#���0�77V�VB��&V6�v旦VBF��W���R��R7V6�f�VB2F�Rf����V�V�V�B�bF�RFFR�F��R7G&��rv���&RW6VBf�"6��WF��p�F�RFFR�F��Rf�VR��b��R7&VFRFFUF��Rv�F�F�P�7G&��rt�"����r�CW�U2�6�f�2r�F�Rf�VRv����W76V�F��ǒ&RF�R6�R2�b��R�B6GW&VBF��R�F��R���BF�R7V6�f�VBFFR�BF��R���6���R��F�BF��W���S����&S�R�FFUF��R�uU2�V7FW&�r��2&WGW&�27W'&V�BFFR�F��R�&W&W6V�FVB��U2�V7FW&�ࠢ��FFUF��R�s��r�2��CW�r��2&WGW&�27V6�f�VBF��R�&W&W6V�FVB����6��6���R���Rࠢ��FFUF��R�t�"����r3�CS�r��2��2WV�F�����&SࠢF�RFFR6����V�B6��6�7G2�b�V"����F���BF��f�VW2�F�R�V"f�VR�W7B&R��R��Gv���� �f�W"�F�v�B��FVvW"��b��R��"Gv��F�v�B�V"�0�W6VB�F�R�V"�277V�VBF�&R��F�RGvV�F�WF��6V�GW'��F�R���F���&R���FVvW"�g&��F�"�����F���R��"���F�&'&Wf�F����v�W&RW&��B����F����ǒf����rF�R&'&Wf�F����F�RF��W7B&R���FVvW"g&��F�F�R�V�&W"�bF�2��F�R���F��F�P��V"����F���BF�f�VW2��&R6W&FVB'��W&��G2����V�2�f�'v&B6�6�W2��"76W2�W�G&�76W2&RW&֗GFVB&�V�BF�RFVƖ֗FW'2��V"�����F���BF�f�VW2��&Rv�fV�����&FW"2���p�2�B�2�76�&�RF�F�7F��wV�6�F�R6����V�G2��b���F�&VR6����V�G2&R�V�&W'2F�B&R�W72F��2��F�V����F��F�זV"�&FW&��r�277V�VBࠢF�RF��R6����V�B6��6�7G2�b��W"�֖�WFR��B6V6��@�f�VW26W&FVB'�6����2�F�R��W"f�VR�W7B&R���FVvW"&WGvVV��B#2��6�W6�fVǒ�F�R֖�WFRf�VP��W7B&R���FVvW"&WGvVV��BS���6�W6�fVǒ�F�P�6V6��Bf�VR��&R���FVvW"f�VR&WGvVV��@�S�㓓���6�W6�fVǒ�F�R6V6��Bf�VR�"&�F�F�R֖�WFP��B6V6��Bf�VW2��&R�֗GFVB�F�RF��R��&P�f����vVB'���"���WW"�"��vW"66R���v��6��66R"ֆ�W"6��6��277V�VBࠢ�Wr����R"�C��F�RFFUF��R6��7G'V7F�"WF��F�6�ǒFWFV7G2�B��F�W0��4�c6��Ɩ�BFFW2���������DEF���73���E�B�ࠢ�Wr����R"��c��F�RW��7F��r�4�c'6W"v2W�FV�FVBF�7W�'B���7@�F�Rv���R�4�c7V6�f�6F�����Wrf�&�G2��6�VFW3����&S���FFUF��R�s��2�CRr��2&WGW&�2F�RCWF�F�g&����2�v��6��2GF�fV''V'���r�FFUF��R�s��2�sb�rr��2&WGW&�2F�RwF�F�g&��F�RgF�vVV�g&����2�v��6��2�2�6�GF�fV''V'����&Sࠢ6VR�GG���V��v���VF���&r�v�����4��cf�"gV��7V72ࠢ��FRF�BF�R��RFFUF��R'6W"77V�W2F��W���R��fR�4�7G&��w2F�&R��UD2&F�W"F����6�F��R27V6�f�VBࠢ��bF�RFFUF��RgV�7F����2��f��VBv�F�6��v�R�V�W&�0�&wV�V�B�F�R�V�&W"�277V�VBF�&Rf��F��r���Bf�VP�7V6�2F�B&WGW&�VB'�F��R�F��R��ࠢFFUF��R�&�V7B�2&WGW&�VBF�B&W&W6V�G2F�Rt�Bf�VP��bF�RF��R�F��R��f��B&W&W6V�FVB��F�R��6��6���Rw0�F��W���Rࠢ��bF�RFFUF��RgV�7F����2��f��VBv�F�6��v�R&wV�V�@�F�B�2FFUF��R��7F�6R�6��&G&VB�&�wV�W2FFW22&F�2&Vf�&R���F��&Vf�&R�V""�F��2W6VgV��b��R�VVBF�'6R����U0�FFW2��&VƖ&�Rv������66RF�Bf��F��r���B�V�&W"�b6V6��G2�2v�fV��"FW&�fVB��Bw2&�V�FVBF�F�R�V&W7B֖�Ɨ6V6��Bࠢ�b7G&��r&wV�V�B76VBF�F�RFFUF��R6��7G'V7F�"6���B&P�'6VB��Bv���&�6RFFUF��R�7��F�W'&�"���fƖBFFR6����V�G0�v���&�6RFFTW'&�"�v���R��fƖBF��R�"F��W���R6����V�G0�v���&�6RFFUF��TW'&�"ࠢF�R��GV�RgV�7F���F��W���W2��v���&WGW&�Ɨ7B�bF�R�6����␢F��W���W2&V6�v旦VB'�F�RFFUF��R��GV�R�&V6�v�F����`�F��W���R��W2�266R֖�6V�6�F�fR�"" ��FFVf�B��r�vWB�vFFVf�Br�vWDFVfV�DFFTf�&�B����B�B�2����P�2��V�&w2��֖7&�6V72����P���b2����2��FW&��f�&�B6��VB��ǒ'�FFUF��P��"����G���"����62�G��B�B�2�&w0�VƖb2����2��FW&��f�&�BF�B��6�VFW2֖�Ɨ6V6��G2�g&��F�RW�6����"����G���"����62�G��B�B�2�֖�Ɨ6V72�&w0�֖7&�6V72�֖�Ɨ6V72� ��VƖb2��#��2��FW&��f�&�BF�B��6�VFW2֖7&�6V6��G2�g&��F�RW�6���B�2f�r��F�6F��rv�WF�W"F��2v26��7G'V7FVB��F��W���R��fP�2���W ��"����G���"����62�G��B�B�2�֖7&�6V72�G���fR�&w0��bG���fR�2��B���S�2&W6W'fRF��2��f�&�F���6V�b��F��W���U���fR�G���fP��VƖb��B&w2�"�2�B&w5���2���R���27W'&V�BF��R�F�&RF�7��VB����6�F��W���P�B�F��R����B�6fV��6�F��R�B��G��6V�b���6Ŧ��R��B���2��B��F��f���"�B���2�B��6�54B�B���"����G���"����62��E��eТ62�62��0�6V�b��F��W���U���fR�f�6P��VƖbltm = safelocaltime(nearTime)
        tz = self.localZone(ltm)
        return tz

    def _parse(self, st, datefmt=getDefaultDateFormat()):
        # Parse date-time components from a string
        month = year = tz = tm = None
        ValidZones = _TZINFO._zidx
        TimeModifiers = ['am', 'pm']

        # Find timezone first, since it should always be the last
        # element, and may contain a slash, confusing the parser.
        st = st.strip()
        sp = st.split()
        tz = sp[-1]
        if tz and (tz.lower() in ValidZones):
            self._timezone_naive = False
            st = ' '.join(sp[:-1])
        else:
            self._timezone_naive = True
            tz = None  # Decide later, since the default time zone
        # could depend on the date.

        ints = []
        i = 0
        len_st = len(st)
        while i < len_st:
            while i < len_st and st[i] in SPACE_CHARS:
                i += 1
            if i < len_st and st[i] in DELIMITERS:
                d = st[i]
                i += 1
            else:
                d = ''
            while i < len_st and st[i] in SPACE_CHARS:
                i += 1

            # The float pattern needs to look back 1 character, because it
            # actually looks for a preceding colon like ':33.33'. This is
            # needed to avoid accidentally matching the date part of a
            # dot-separated date string such as '1999.12.31'.
            if i > 0:
                b = i - 1
            else:
                b = i

            ts_results = FLT_PATTERN.match(st, b)
            if ts_results:
                s = ts_results.group(1)
                i = i + len(s)
                ints.append(float(s))
                continue

            ts_results = INT_PATTERN.match(st, i)
            if ts_results:
                s = ts_results.group(0)

                ls = len(s)
                i = i + ls
                if (ls == 4 and d and d in '+-' and
                        (l�', '/') and len(ints) > 2:
            year = ints[-1]
            del ints[-1]
            if month:
                day = ints[0]
                del ints[:1]
            else:
                if datefmt == "us":
                    month = ints[0]
                    day = ints[1]
                else:
                    month = ints[1]
                    day = ints[0]
                del ints[:2]
        elif month:
            if len(ints) > 1:
                if ints[0] > 31:
                    year = ints[0]
                    day = ints[1]
                else:
                    year = ints[1]
                    day = ints[0]
                del ints[:2]
        elif len(ints) > 2:
            if ints[0] > 31:
                year = ints[0]
                if ints[1] > 12:
                    day = ints[1]
                    month = ints[2]
                else:
                    day = ints[2]
                    month = ints[1]
            if ints[1] > 31:
                year = ints[1]
                if ints[0] > 12 and ints[2] <= 12:
                    day = ints[0]
                    month = ints[2]
                elif ints[2] > 12 and ints[0] <= 12:
                    day = ints[2]
                    month = ints[0]
            elif ints[2] > 31:
                year = ints[2]
                if ints[0] > 12:
                    day = ints[0]
                    month = ints[1]
                else:
                    if datefmt == "us":
                        day = ints[1]
                        month = ints[0]
                    else:
                        day = ints[0]
                        month = ints[1]

            elif ints[0] <= 12:
                month = ints[0]
                day = ints[1]
                year = ints[2]
            del ints[:3]

        if day is None:
            # Use today's date.
            year, month, day = localtime(time())[:3]

        year = _correctYear(year)
        if year < 1000:
            raise SyntaxError(st)

        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        try:
            if not day or day > _MONTH_LEN[leap][month]:
                raise DateError(st)
        except IndexError:
            raise DateError(st)

        tod = 0
        if ints:
            i = ints[0]
            # Modify hour to reflect am/pm
            if tm and (tm == 'pm') and i < 12:
                i += 12
            if tm and (tm == 'am') and i == 12:
                i = 0
            if i > 24:
                raise TimeError(st)
            tod = tod + int(i) * 3600
            del ints[0]
            if ints:
                i = ints[0]
                if i > 60:
                    raise TimeError(st)
                tod = tod + int(i) * 60
                del ints[0]
                if ints:
                    i = ints[0]
                    if i > 60:
                        raise TimeError(st)
                    tod = tod + i
                    del ints[0]
                    if ints:
                        raise SyntaxError(st)

        tod_int = int(math.floor(tod))
        ms = tod - tod_int
        hr, mn, sc = _calcHMS(tod_int, ms)
        if not tz:
            # Figure out what time zone it is in the local area
            # on the given date.
            x = _calcDependentSecond2(year, month, day, hr, mn, sc)
            tz = self._calcTimezoneName(x, ms)

        return year, month, day, hr, mn, sc, tz

    # Internal methods
    def _validDate(self, y, m, d):
        if m < 1 or m > 12 or y < 0 or d < 1 or d > 31:
            return 0
        return d <= _MONTH_LEN[
            (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))][m]

    def _validTime(self, h, m, s):
        return h >= 0 and h <= 23 and m >= 0 and m <= 59 and s >= 0 and s < 60

    def __getattr__(self, name):
        if '%' in name:
            return strftimeFormatter(self, name)
        raise AttributeError(name)

    # Conversion and comparison methods

    def timeTime(self):
        """Return the date/time as a floating-point number in UTC,
        in the format used by the Python time module.

        Note that it is possible to create date/time values with
        DateTime that have no meaningful value to the time module.
        """
        return self._micros / 1000000.0

    def toZone(self, z):
        """Return a DateTime with the value as the current
        object, represented in the indicated timezone.
        """
        t, tz = self._t, _TZINFO._zmap[z.lower()]
        micros = self.micros()
        tznaive = False  # you're performing a timzone change, can't be naive

        try:
            # Try to use time module for speed.
            yr, mo, dy, hr, mn, sc = safegmtime(t + _tzoffset(tz, t))[:6]
            sc = self._second
            return self.__class__(yr, mo, dy, hr, mn, sc, tz, t,
                                  self._d, self.time, micros, tznaive)
        except Exception:
            # gmtime can't perform the calculation in the given range.
            # Calculate the difference between the two time zones.
            tzdiff = _tzoffset(tz, t) - _tzoffset(self._tz, t)
            if tzdiff == 0:
                return self
            sc = self._second
            ms = sc - math.floor(sc)
            x = _calcDependentSecond2(self._year, self._month, self._day,
                                      self._hour, self._minute, sc)
            x_new = x + tzdiff
            yr, mo, dy, hr, mn, sc = _calcYMDHMS(x_new, ms)
            return self.__class__(yr, mo, dy, hr, mn, sc, tz, t,
                                  self._d, self.time, micros, tznaive)

    def isFuture(self):
        """Return true if this object represents a date/time
        later than the time of the call.
        """
        return (self._t > time())

    def isPast(self):
        """Return true if this object represents a date/time
        earlier than the time of the call.
        """
        return (self._t < time())

    def isCurrentYear(self):
        """Return true if this object represents a date/time
        that falls within the current year, in the context
        of this object's timezone representation.
        """
        t = time()
        return safegmtime(t + _tzoffset(self._tz, t))[0] == self._year

    def isCurrentMonth(self):
        """Return true if this object represents a date/time
        that falls within the current month, in the context
        of this object's timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return gmt[0] == self._year and gmt[1] == self._month

    def isCurrentDay(self):
        """Return true if this object represents a date/time
        that falls within the current day, in the context
        of this object's timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day)

    def isCurrentHour(self):
        """Return true if this object represents a date/time
        that falls within the current hour, in the context
        of this object's timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day and gmt[3] == self._hour)

    def isCurrentMinute(self):
        """Return true if this object represents a date/time
        that falls within the current minute, in the context
        of this object's timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day and gmt[3] == self._hour and
                gmt[4] == self._minute)

    def earliestTime(self):
        """Return a new DateTime object that represents the earliest
        possible time (in whole seconds) that still falls within
        the current object's day, in the object's timezone context.
        """
        return self.__class__(
            self._year, self._month, self._day, 0, 0, 0, self._tz)

    def latestTime(self):
        """Return a new DateTime object that represents the latest
        possible time (in whole seconds) that still falls within
        the current object's day, in the object's timezone context.
        """
        return self.__class__(
            self._year, self._month, self._day, 23, 59, 59, self._tz)

    def greaterThan(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the Python time module.

        Returns true if the object represents a date/time greater
        than the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            return True
        if isinstance(t, (float, int)):
            return self._micros > long(t * 1000000)
        else:
            return self._micros > t._micros

    __gt__ = greaterThan

    def greaterThanEqualTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the Python time module.

        Returns true if the object represents a date/time greater
        than or equal to the specified DateTime or time module style
        time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            return True
        if isinstance(t, (float, int)):
            return self._micros >= long(t * 1000000)
        else:
            return self._micros >= t._micros

    __ge__ = greaterThanEqualTo

    def equalTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the Python time module.

        Returns true if the object represents a date/time equal to
        the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            return False
        if isinstance(t, (float, int)):
            return self._micros == long(t * 1000000)
        else:
            return self._micros == t._micros

    def notEqualTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the Python time module.

        Returns true if the object represents a date/time not equal
        to the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        return not self.equalTo(t)

    def __eq__(self, t):
        """Compare this DateTime object to another DateTime object.
        Return True if their internal state is the same. Two objects
        representing the same time in different timezones are regared as
        unequal. Use the equalTo method if you are only interested in them
        referring to the same moment in time.
        """
        if not isinstance(t, DateTime):
            return False
        return (self._micros, self._tz) == (t._micros, t._tz)

    def __ne__(self, t):
        return not self.__eq__(t)

    def lessThan(self, t):
        """Compare this DateTimf.t((d + jd1901) - _julianday(self._year, 1, 0))

    # Component access
    def parts(self):
        """Return a tuple containing the calendar year, month,
        day, hour, minute second and timezone of the object.
        """
        return (self._year, self._month, self._day, self._hour,
                self._minute, self._second, self._tz)

    def timezone(self):
        """Return the timezone in which the object is represented."""
        return self._tz

    def tzoffset(self):
        """Return the timezone offset for the objects timezone."""
        return _tzoffset(self._tz, self._t)

    def year(self):
        """Return the calendar year of the object."""
        return self._year

    def month(self):
        """Return the month of the object as an integer."""
        return self._month

    @property
    def _fmon(self):
        return _MONTHS[self._month]

    def Month(self):
        """Return the full month name."""
        return self._fmon

    @property
    def _amon(self):
        return _MONTHS_A[self._month]

    def aMonth(self):
        """Return the abbreviated month name."""
        return self._amon

    def Mon(self):
        """Compatibility: see aMonth."""
        return self._amon

    @property
    def _pmon(self):
        return _MONTHS_P[self._month]

    def pMonth(self):
        """Return the abbreviated (with period) month name."""
        return self._pmon

    def Mon_(self):
        """Compatibility: see pMonth."""
        return self._pmon

    def day(self):
        """Return the integer day."""
        return self._day

    @property
    def _fday(self):
        return _DAYS[self._dayoffset]

    def Day(self):
        """Return the full name of the day of the week."""
        return self._fday

    def DayOfWeek(self):
        """Compatibility: see Day."""
        return self._fday

    @property
    def _aday(self):
        return _DAYS_A[self._dayoffset]

    def aDay(self):
        """Return the abbreviated name of the day of the week."""
        return self._aday

    @property
    def _pday(self):
        return _DAYS_P[self._dayoffset]

    def pDay(self):
        """Return the abbreviated (with period) name of the day of the week."""
        return self._pday

    def Day_(self):
        """Compatibility: see pDay."""
        return self._pday

    def dow(self):
        """Return the integer day of the week, where Sunday is 0."""
        return self._dayoffset

    def dow_1(self):
        """Return the integer day of the week, where Sunday is 1."""
        return self._dayoffset + 1

    @property
    def _pmhour(self):
        hr = self._hour
        if hr > 12:
            return hr - 12
        return hr or 12

    def h_12(self):
        """Return the 12-hour clock representation of the hour."""
        return self._pmhour

    def h_24(self):
        """Return the 24-hour clock representation of the hour."""
        return self._hour

    @property
    def _pm(self):
        hr = self._hour
        if hr >= 12:
            return 'pm'
        return 'am'

    def ampm(self):
        """Return the appropriate time modifier (am or pm)."""
        return self._pm

    def hour(self):
        """Return the 24-hour clock representation of the hour."""
        return self._hour

    def minute(self):
        """Return the minute."""
        return self._minute

    def second(self):
        """Return the second."""
        return self._second

    def millis(self):
        """Return the millisecond since the epoch in GMT."""
        return self._micros // 1000

    def micros(self):
        """Return the microsecond since the epoch in GMT."""
        return self._micros

    def timezoneNaive(self):
        """The Python datetime module introduces the idea of distinguishing
        between timezone aware and timezone naive datetime values. For lossless
        conversion to and from datetime.datetime we record this
        information using True / False. DateTime makes no distinction, if we
        don't have any information we return None here.
        """
        try:
            return self._timezone_naive
        except AttributeError:
            return None

    def strftime(self, format):
        """Format the date/time using the *current timezone representation*."""
        x = _calcDependentSecond2(self._year, self._month, self._day,
                                  self._hour, self._minute, self._second)
        ltz = self._calcTimezoneName(x, 0)
        tzdiff = _tzoffset(ltz, self._t) - _tzoffset(self._tz, self._t)
        zself = self + tzdiff / 86400.0
        microseconds = int((zself._second - zself._nearsec) * 1000000)
        unicode_format = False
        if isinstance(format, explicit_unicode_type):
            format = format.encode('utf-8')
            unicode_format = True
        ds = datetime(zself._year, zself._month, zself._day, zself._hour,
                      zself._minute, int(zself._nearsec),
                      microseconds).strftime(format)
        if unicode_format:
            return ds.decode('utf-8')
        return ds

    # General formats from previous DateTime
    def Date(self):
        """Return the date string for the object."""
        return "%s/%2.2d/%2.2d" % (self._year, self._month, self._day)

    def Time(self):
        """Return the time string for an object to the nearest second."""
        return '%2.2d:%2.2d:%2.2d' % (self._hour, self._minute, self._nearsec)

    def TimeMinutes(self):
        """Return the time string for an object not showing seconds."""
        return '%2.2d:%2.2d' % (self._hour, self._minute)

    def AMPM(self):
        """Return the time string for an object to the nearest second."""
        return '%2.2d:%2.2d:%2.2d %s' % (
            self._pmhour, self._minute, self._nearsec, self._pm)

    def AMPMMinutes(self):
        """Return the time string for an object not showing seconds."""
        return '%2.2d:%2.2d %s' % (self._pmhour, self._minute, self._pm)

    def PreciseTime(self):
        """Return the time string for the object."""
        return '%2.2d:%2.2d:%06.3f' % (self._hour, self._minute, self._second)

    def PreciseAMPM(self):
        """Return the time string for the object."""
        return '%2.2d:%2.2d:%06.3f %s' % (
            self._pmhour, self._minute, self._second, self._pm)

    def yy(self):
        """Return calendar year as a 2 digit string."""
        return str(self._year)[-2:]

    def mm(self):
        """Return month as a 2 digit string."""
        return '%02d' % self._month

    def dd(self):
        """Return day as a 2 digit string."""
        return '%02d' % self._day

    def rfc822(self):
        """Return the date in RFC 822 format."""
        tzoffset = _tzoffset2rfc822zone(_tzoffset(self._tz, self._t))
        return '%s, %2.2d %s %d %2.2d:%2.2d:%2.2d %s' % (
            self._aday, self._day, self._amon, self._year,
            self._hour, self._minute, self._nearsec, tzoffset)

    # New formats
    def fCommon(self):
        """Return a string representing the object's value
        in the format: March 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._fmon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def fCommonZ(self):
        """Return a string representing the object's value
        in the format: March 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._fmon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def aCommon(self):
        """Return a string representing the object's value
        in the format: Mar 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._amon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def aCommonZ(self):
        """Return a string representing the object's value
        in the format: Mar 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._amon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def pCommon(self):
        """Return a string representing the object's value
        in the format: Mar. 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._pmon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def pCommonZ(self):
        """Return a string representing the object's value
        in the format: Mar. 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._pmon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def ISO(self):
        """Return the object in ISO standard format.

        Note: this is *not* ISO 8601-format! See the ISO8601 and
        HTML4 methods below for ISO 8601-compliant output.

        Dates are output as: YYYY-MM-DD HH:MM:SS
        """
        return "%.4d-%.2d-%.2d %.2d:%.2d:%.2d" % (
            self._year, self._month, self._day,
            self._hour, self._minute, self._second)

    def ISO8601(self):
        """Return the object in ISO 8601-compatible format containing the
        date, time with seconds-precision and the time zone identifier.

        See: http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSTZD
            T is a literal character.
            TZD is Time Zone Designator, format +HH:MM or -HH:MM

        If the instance is timezone naive (it was not specified with a timezone
        when it was constructed) then the timezone is omitted.

        The HTML4 method below offers the same formatting, but converts
        to UTC before returning the value and sets the TZD "Z".
        """
        if self.timezoneNaive():
            return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2d" % (
                self._year, self._month, self._day,
                self._hour, self._minute, self._second)
        tzoffset = _tzoffset2iso8601zone(_tzoffset(self._tz, self._t))
        return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2d%s" % (
            self._year, self._month, self._day,
            self._hour, self._minute, self._second, tzoffset)

    def HTML4(self):
        """Return the object in the format used in the HTML4.0 specification,
        one of the standard forms in ISO8601.

        See: http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSZ
           T, Z are literal characters.
           The time is in UTC.
        """
        newdate = self.toZone('UTC')
        return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2dZ" % (
            newdate._year, newdate._month, newdate._day,
            newdate._hour, newdate._minute, newdate._second)

    def asdatetime(self):
        """Return a standard library datetime.datetime
        """
        tznaive = self.timezoneNaive()
        if tznaive:
            tzinfo = None
        else:
            tzinfo = _TZINFO[self._tz].tzinfo
        second = int(self._second)
        microsec = self.micros() % 1000000
        dt = datetime(self._year, self._month, self._day, self._hour,
                      self._minute, second, microsec, tzinfo)
        return dt

    def utcdatetime(self):
        """Convert the time to UTC and return a timezone naive datetime object
        """
        utc = self.toZone('UTC')
        second = int(utc._second)
        microsec = utc.micros() % 1000000
        dt = datetime(utc._year, utc._month, utc._day, utc._hour,
                      utc._minute, second, microsec)
        return dt

    def __add__(self, other):
        """A DateTime may be added to a number and a number may be
        added to a DateTime; two DateTimes cannot be added.
        """
        if hasattr(other, '_t'):
            raise DateTimeError('Cannot add two DateTimes')
        o = float(other)
        tz = self._tz
        omicros = round(o * 86400000000)
        tmicros = self.micros() + omicros
        t = tmicros / 1000000.0
        d = (tmicros + long(EPOCH * 1000000)) / 86400000000.0
        s = d - math.floor(d)
        ms = t - math.floor(t)
        x = _calcDependentSecond(tz, t)
        yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
        return self.__class__(yr, mo, dy, hr, mn, sc, self._tz,
                              t, d, s, tmicros, self.timezoneNaive())

    __radd__ = __add__

    def __sub__(self, other):
        """Either a DateTime or a number may be subtracted from a
        DateTime, however, a DateTime may not be subtracted from
        a number.
        """
        if hasattr(other, '_d'):
            return (self.micros() - other.micros()) / 86400000000.0
        else:
            return self.__add__(-(other))

    def __repr__(self):
        """Convert a DateTime to a string that looks like a Python
        expression.
        """
        return '{}"P      """Convert a DateTime to a string."""
        y, m, d = self._year, self._month, self._day
        h, mn, s, t = self._hour, self._minute, self._second, self._tz
        if s == int(s):
            # A whole number of seconds -- suppress milliseconds.
            return '%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%2.2d %s' % (
                y, m, d, h, mn, s, t)
        else:
            # s is already rounded to the nearest microsecond, and
            # it's not a whole number of seconds.  Be sure to print
            # 2 digits before the decimal point.
            return '%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%06.6f %s' % (
                y, m, d, h, mn, s, t)

    def __format__(self, fmt):
        """Render a DateTime in an f-string."""
        if not isinstance(fmt, str):
            raise TypeError("must be str, not %s" % type(fmt).__name__)
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    def __hash__(self):
        """Compute a hash value for a DateTime."""
        return int(((self._year % 100 * 12 + self._month) * 31 +
                    self._day + self.time) * 100)

    def __int__(self):
        """Convert to an integer number of seconds since the epoch (gmt)."""
        return int(self.micros() // 1000000)

    def __long__(self):
        """Convert to a long-int number of seconds since the epoch (gmt)."""
        return long(self.micros() // 1000000)  # pragma: PY2

    def __float__(self):
        """Convert to floating-point number of seconds since the epoch (gmt).
        """
        return self.micros() / 1000000.0

    @property
    def _t(self):
        return self._micros / 1000000.0

    def _parse_iso8601(self, s):
        # preserve the previously implied contract
        # who knows where this could be used...
        return self._parse_iso8601_preserving_tznaive(s)[:7]

    def _parse_iso8601_preserving_tznaive(self, s):
        try:
            return self.__parse_iso8601(s)
        except IndexError:
            raise SyntaxError(
                'Not an ISO 8601 compliant date string: "%s"' % s)

    def __parse_iso8601(self, s):
        """Parse an ISO 8601 compliant date.

        See: http://en.wikipedia.org/wiki/ISO_8601
        """
        month = day = week_day = 1
        year = hour = minute = seconds = hour_off = min_off = 0
        tznaive = True

        iso8601 = iso8601Match(s.strip())
        fields = iso8601 and iso8601.groupdict() or {}
        if not iso8601 or fields.get('garbage'):
            raise IndexError

        if fields['year']:
            year = int(fields['year'])
        if fields['month']:
            month = int(fields['month'])
        if fields['day']:
            day = int(fields['day'])

        if fields['year_day']:
            d = DateTime('%s-01-01' % year) + int(fields['year_day']) - 1
            month = d.month()
            day = d.day()

        if fields['week']:
            week = int(fields['week'])
            if fields['week_day']:
                week_day = int(fields['week_day'])
            d = DateTime('%s-01-04' % year)
            d = d - (d.dow() + 6) % 7 + week * 7 + week_day - 8
            month = d.month()
            day = d.day()

        if fields['hour']:
            hour = int(fields['hour'])

        if fields['minute']:
            minute = int(fields['minute'])
        elif fields['fraction']:
            minute = 60.0 * float('0.%s' % fields['fraction'])
            seconds, minute = math.modf(minute)
            minute = int(minute)
            seconds = 60.0 * seconds
            # Avoid reprocess when handling seconds, bellow
            fields['fraction'] = None

        if fields['second']:
            seconds = int(fields['second'])
            if fields['fraction']:
                seconds = seconds + float('0.%s' % fields['fraction'])
        elif fields['fraction']:
            seconds = 60.0 * float('0.%s' % fields['fraction'])

        if fields['hour_off']:
            hour_off = int(fields['hour_off'])
            if fields['signal'] == '-':
                hour_off *= -1

        if fields['min_off']:
            min_off = int(fields['min_off'])

        if fields['signal'] or fields['Z']:
            tznaive = False
        else:
            tznaive = True

        # Differ from the specification here. To preserve backwards
        # compatibility assume a default timezone == UTC.
        tz = 'GMT%+03d%02d' % (hour_off, min_off)

        return year, month, day, hour, minute, seconds, tz, tznaive

    def JulianDay(self):
        """Return the Julian day.

        See: https://www.tondering.dk/claus/cal/julperiod.php#formula
        """
        a = (14 - self._month) // 12
        y = self._year + 4800 - a
        m = self._month + (12 * a) - 3
        return (self._day + (153 * m + 2) // 5 + 365 * y +
                y // 4 - y // 100 + y // 400 - 32045)

    def week(self):
        """Return the week number according to ISO.

        See: https://www.tondering.dk/claus/cal/week.php#weekno
        """
        J = self.JulianDay()
        d4 = (J + 31741 - (J % 7)) % 146097 % 36524 % 1461
        L = d4 // 1460
        d1 = ((d4 - L) % 365) + L
        return d1 // 7 + 1

    def encode(self, out):
        """Encode value for XML-RPC."""
        out.write('<value><dateTime.iso8601>')
        out.write(self.ISO8601())
        out.write('</dateTime.iso8601></value>\n')


# Provide the _dt_reconstructor function here, in case something
# accidentally creates a reference to this function

orig_reconstructor = copy_reg._reconstructor


def _dt_reconstructor(cls, base, state):
    if cls is DateTime:
        return cls(state)
    return orig_reconstructor(cls, base, state)
