class Detection():
    jpgByteslist = [b'\xff',b'\xd8']
    pngByteslist = [b'\x89',b'P',b'N',b'G']
    pm4Byteslist = [b'f',b't',b'y',b'p']
    aviByteslist = [b'R',b'I',b'F',b'F',b'A',b'V',b'I',b' ']
    movByteslist = [b'f',b't',b'y',b'p']

    def is_avi(self,inputfile):
        BytesList = []
        i = 0
        while(i<8):
            byte = inputfile.read(1)
            BytesList.append(byte)
            i+=1
        del BytesList[4:8]
        inputfile.seek(0, 0)
        if( BytesList == self.aviByteslist):
            return True
        return False

    def is_mp4(self,inputfile):
        BytesList = []
        i = 0
        while(i<8):
            byte = inputfile.read(1)
            BytesList.append(byte)
            i+=1
        del BytesList[0:4]
        inputfile.seek(0, 0)
        if( BytesList == self.pm4Byteslist):
            return True
        return False

    def is_mov(self,inputfile):
        BytesList = []
        i = 0
        while(i<8):
            byte = inputfile.read(1)
            BytesList.append(byte)
            i+=1
        del BytesList[0:4] 
        inputfile.seek(0, 0)
        if( BytesList == self.movByteslist):
            return True
        return False

    def isImage(self,inputfile):
        BytesList = []
        i = 0
        while(i<4):
            byte = inputfile.read(1)
            BytesList.append(byte)
            i+=1
        inputfile.seek(0, 0)
        if( BytesList[1] == self.pngByteslist[1] and BytesList[2] == self.pngByteslist[2] and BytesList[3] == self.pngByteslist[3]):
            return True
        else:
            if BytesList[0] == self.jpgByteslist[0] and BytesList[1] == self.jpgByteslist[1]:
                return True
            else:
                return False
        return False

    def detect(self,input):
        if self.isImage(input):
            return 'img'
        elif self.is_avi(input) or self.is_mov(input) or self.is_mp4(input):
            return 'video'
        else:
            return False
