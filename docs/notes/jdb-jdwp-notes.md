handshake - 4a4457502d48616e647368616b65

1, 7 - IDSizes - 0000000b pkt = 00000001 00 01 07





15, 1 - EventRequest.Set 00000011 pkt = 00000003 00 0f 01
  0x08 0x00 0x00 0x00 0x00 0x00
  - eventKind: CLASS_PREPARE
  - suspendPolicy: 0
  - modifiers count: 0

pkt = 5
15, 1 - EventRequest.Set data = 0x09 0x00 0x00 0x00 0x00 0x00
  - eventKind: CLASS_UNLOAD
  - suspendPolicy: 0
  - modifiers count: 0

pkt = 7
15, 1 - EventRequest.Set hdr = 0000002e 00000007 00 0f 01 
        data = 08 02 00 00 00 02  05 00 00 00 13 6a 61 76 61 2e 6c 61 6e 67 2e 54 68 72 6f 77 61 62 6c 65 01 00 00 00 01
  - eventKind: CLASS_PREPARE
  - suspendPolicy: 2
  - modifiers count: 2
    - modKind: 05
      - classPattern len: 0x13
      - classPattern str: 6a 61 76 61 2e 6c 61 6e 67 2e 54 68 72 6f 77 61 62 6c 65
    - modKind: 01
      - count: 1

1, 1 - VirtualMachine.Version pkt = 9

pkt = 11
1, 20 - VirtualMachine.AllClassesWithGeneric

pkt = 13
15, 1 - 0000001c 0000000d 000f01 04 02 00000001 0800000000000002290001
  - eventKind: EXCEPTION
  - suspendPolicy: 2
  - modifiers count: 1
    - modKind: 08
    - exceptionOfNull: 0000000000000229
    - caught: 00
    - uncaught: 01

pkt = 15
15, 2 - EventRequest.Clear 000000100000000f000f02 08 00000004

pkt = 17
15, 1 - 00000011 00000011 000f01 060200000000
  - eventKind: THREAD_START
  - suspendPolicy: 2
  - modifiers count: 0

pkt = 19
15, 1 - 0000001100000013000f01 070200000000
  - eventKind: THREAD_DEATH
  - suspendPolicy: 2
  - modifiers count: 0

pkt = 21 (wireshark pkt 91)
1, 13 - VirtualMachine.ClassPaths - 0000000b0000001500010d

??

pkt = f9
1, 4 - VirtualMachine.AllThreads - 0000000b000000f9000104

pkt = fb
1, 9 - VirtualMachine.Resume - 0000000b000000fb000109





