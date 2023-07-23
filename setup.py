#!/usr/bin/env python
# Copyright (C) 2019-23 Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# ****************************************************************************
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ****************************************************************************

try :
    from hamradio.Version import VERSION
except :
    VERSION = None
from warnings       import filterwarnings
from distutils.core import setup, Extension

filterwarnings \
    ( "ignore"
    , "Unknown distribution option: 'install_requires'"
    )

description = []
with open ('README.rst') as f :
    for line in f :
            description.append (line)

license     = 'BSD License'
setup \
    ( name             = "hamradio"
    , version          = VERSION
    , description      = "Utilities for Ham radio"
    , long_description = ''.join (description)
    , license          = license
    , author           = "Ralf Schlatterbeck"
    , author_email     = "rsc@runtux.com"
    , install_requires = ['rsclib', 'requests', 'bs4']
    , packages         = ['hamradio']
    , package_data     = dict
        (hamradio = ['data/*.txt', 'data/*.dat', 'data/*.html'])
    , platforms        = 'Any'
    , python_requires  = '>=3.6'
    , entry_points     = dict
        ( console_scripts =
            [ 'callsign_lookup=hamradio.dxcc:main'
            , 'qsl-export=hamradio.qslcard:main'
            , 'qso-import=hamradio.dbimport:main'
            ]
        )
    , url              = 'https://github.com/schlatterbeck/hamradio'
    , classifiers      =
        [ 'Development Status :: 5 - Production/Stable'
        , 'License :: OSI Approved :: ' + license
        , 'Operating System :: OS Independent'
        , 'Programming Language :: Python'
        , 'Intended Audience :: Developers'
        , 'Programming Language :: Python :: 3.7'
        , 'Programming Language :: Python :: 3.8'
        , 'Programming Language :: Python :: 3.9'
        , 'Programming Language :: Python :: 3.10'
        , 'Programming Language :: Python :: 3.11'
        ]
    )
