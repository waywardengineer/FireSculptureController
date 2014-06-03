FireSculptureController
=======================

Controller framework with the goal of being useful for all FLG and other big fire sculptures

Requirements:
Python 2.7 (2.7.6 on Win7 due to greenlet installation issues)

Python libraries:
  Sculpture engine:
    pyserial for talking to sculptures over serial
   
  Server for js GUI:
    gevent
    greenlet
    flask

  Audio pulse:
    pyaudio
    
  OSC server:
    pyOSC